import os
import asyncio
import tempfile
from typing import Dict, Any, List
import pandas as pd

from src.models.candidate_models import ProcessingResult
from src.services.drive_service import GoogleDriveService
from src.services.file_processor import FileProcessor
from src.services.ai_service import AIEvaluationService

class CandidateProcessor:
    def __init__(self, drive_service: GoogleDriveService, file_processor: FileProcessor, ai_service: AIEvaluationService):
        self.drive_service = drive_service
        self.file_processor = file_processor
        self.ai_service = ai_service
    
    def create_candidate_narrative(self, email: str, data: pd.DataFrame) -> str:
        """Create comprehensive text narrative for a candidate"""
        candidate = data[data['Email address'] == email]
        
        if candidate.empty:
            return f"No candidate found with email: {email}"
        
        candidate = candidate.iloc[0]
        
        def safe_get(column_name):
            value = candidate.get(column_name, 'Not provided')
            return 'Not provided' if pd.isna(value) or str(value).strip() == '' else str(value)
        
        narrative = f"""
        CANDIDATE PROFILE NARRATIVE
        
        Personal Information:
        {safe_get('Title')} {safe_get('Name (surname first)')} is a {safe_get('Gender').lower()} candidate born on {safe_get('Date of birth')}. 
        Their marital status is {safe_get('Marital status').lower()} and they follow the {safe_get('Religion')} faith.
        
        Contact Details:
        The candidate can be reached at {safe_get('Email address')} or by phone at {safe_get('Phone number')}. 
        They currently reside at: {safe_get('Residential address')}.
        
        Professional Background:
        Currently, they are employed as {safe_get('Current employment or occupation (if applicable)')} in the {safe_get('Current employment or occupational category')} sector. 
        Their workplace is located at: {safe_get('Company address')}.
        
        Educational Background:
        For their undergraduate studies, they attended {safe_get('University attended')} where they pursued a {safe_get('Degree type  (undergraduate)')} degree in {safe_get('Programme (undergraduate)')}. 
        They achieved a {safe_get('Class of degree (undergraduate)')} and completed their studies on {safe_get('Date of completion (undergraduate)')}.
        
        For postgraduate education, they pursued a {safe_get('Degree type (postgraduate)')} in {safe_get('Programme (postgraduate)')}, achieving a {safe_get('Class of degree (postgraduate)')} and completed/expecting to complete on {safe_get('Date of completion/Expected date of completion (postgraduate)')}.
        
        Additional Qualifications:
        Their educational qualifications include: {safe_get('Education qualification(s)')}.
        Professional qualifications: {safe_get('Professional qualification(s)')}.
        
        Career Aspirations:
        The candidate's career interests are: {safe_get('Career interests')}.
        
        Programme Interest:
        Regarding the Management Scholars Academy (MSA), their interest level is: {safe_get('Would you be interested in joining the Management Scholars Academy (MSA) if such an option is available? See https://www.lbs.edu.ng/faculty-and-research/management-scholars-academy-2/ for details')}.
        
        Previous Applications: {safe_get('Have you applied for this programme before?')}.
        
        Candidate's Essay:
        {safe_get('Write an essay demonstrating why you are an ideal candidate for this programmme, highlighting all significant details')}
        
        Application Date: {safe_get('Timestamp')}
        """
        
        return narrative.strip()
    
    async def process_candidate_files(self, email: str, data: pd.DataFrame) -> ProcessingResult:
        """Process candidate files (CV and video) asynchronously"""
        candidate = data[data['Email address'] == email]
        if candidate.empty:
            return ProcessingResult(
                email=email,
                name="Unknown",
                errors=[f"No candidate found with email: {email}"]
            )
        
        candidate = candidate.iloc[0]
        result = ProcessingResult(
            email=email,
            name=candidate.get('Name (surname first)', 'Unknown')
        )
        
        # Process CV and video concurrently
        cv_task = self._process_cv(candidate, result)
        video_task = self._process_video(candidate, result)
        
        await asyncio.gather(cv_task, video_task, return_exceptions=True)
        
        return result
    
    async def _process_cv(self, candidate: pd.Series, result: ProcessingResult):
        """Process CV file"""
        cv_url = candidate.get('Curriculum vitae ', '')
        if not cv_url or pd.isna(cv_url):
            return
        
        cv_file_id = self.drive_service.extract_file_id(cv_url)
        if not cv_file_id:
            result.errors.append("Could not extract CV file ID")
            return
        
        temp_cv = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_cv_path = temp_cv.name
        temp_cv.close()
        
        try:
            if await self.drive_service.download_file(cv_file_id, temp_cv_path):
                # Try PDF first
                cv_text = await self.file_processor.extract_text_from_pdf(temp_cv_path)
                
                if "Error extracting PDF" in cv_text:
                    # Try as DOCX
                    docx_path = temp_cv_path.replace('.pdf', '.docx')
                    try:
                        os.rename(temp_cv_path, docx_path)
                        cv_text = await self.file_processor.extract_text_from_docx(docx_path)
                        await self.file_processor.safe_delete_file(docx_path)
                    except Exception as e:
                        cv_text = f"Error processing as DOCX: {str(e)}"
                        await self.file_processor.safe_delete_file(temp_cv_path)
                else:
                    await self.file_processor.safe_delete_file(temp_cv_path)
                
                result.cv_text = cv_text
            else:
                result.errors.append("Failed to download CV")
                await self.file_processor.safe_delete_file(temp_cv_path)
        except Exception as e:
            result.errors.append(f"CV processing error: {str(e)}")
            await self.file_processor.safe_delete_file(temp_cv_path)
    
    async def _process_video(self, candidate: pd.Series, result: ProcessingResult):
        """Process video file"""
        video_url = candidate.get('Create a video presentation describing yourself and share your experiences', '')
        if not video_url or pd.isna(video_url):
            return
        
        video_file_id = self.drive_service.extract_file_id(video_url)
        if not video_file_id:
            result.errors.append("Could not extract video file ID")
            return
        
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video_path = temp_video.name
        temp_video.close()
        
        try:
            if await self.drive_service.download_file(video_file_id, temp_video_path):
                result.video_transcript = await self.file_processor.transcribe_video(temp_video_path)
                await self.file_processor.safe_delete_file(temp_video_path)
            else:
                result.errors.append("Failed to download video")
                await self.file_processor.safe_delete_file(temp_video_path)
        except Exception as e:
            result.errors.append(f"Video processing error: {str(e)}")
            await self.file_processor.safe_delete_file(temp_video_path)
    
    async def create_comprehensive_evaluation(self, email: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive candidate evaluation"""
        candidate = data[data['Email address'] == email]
        
        if candidate.empty:
            return {"error": f"No candidate found with email: {email}"}
        
        candidate = candidate.iloc[0]
        
        # Get basic narrative
        basic_narrative = self.create_candidate_narrative(email, data)
        
        # Process files
        file_results = await self.process_candidate_files(email, data)
        
        # Create enhanced narrative
        enhanced_narrative = f"""
        {basic_narrative}
        
        EXTRACTED CV CONTENT:
        {file_results.cv_text[:2000]}{'...' if len(file_results.cv_text) > 2000 else ''}
        
        VIDEO PRESENTATION TRANSCRIPT:
        {file_results.video_transcript[:2000]}{'...' if len(file_results.video_transcript) > 2000 else ''}
        
        PROCESSING NOTES:
        Errors encountered: {', '.join(file_results.errors) if file_results.errors else 'None'}
        """
        
        # Get AI evaluation
        evaluation_result = await self.ai_service.evaluate_candidate(enhanced_narrative)
        
        # Helper function to convert pandas types to JSON serializable types
        def safe_convert(value):
            if pd.isna(value):
                return ""
            elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                return str(value)
            elif isinstance(value, (int, float)) and pd.isna(value):
                return ""
            else:
                return str(value)
        
        # Create comprehensive result
        comprehensive_result = {
            # AI Evaluation Results
            "outcome": evaluation_result.get("outcome", "Error"),
            "score": evaluation_result.get("score", 0.0),
            "rationale": evaluation_result.get("rationale", "No rationale provided"),
            
            # Original candidate data (key fields)
            "timestamp": safe_convert(candidate.get('Timestamp', '')),
            "email": safe_convert(candidate.get('Email address', '')),
            "title": safe_convert(candidate.get('Title', '')),
            "name": safe_convert(candidate.get('Name (surname first)', '')),
            "gender": safe_convert(candidate.get('Gender', '')),
            "date_of_birth": safe_convert(candidate.get('Date of birth', '')),
            "marital_status": safe_convert(candidate.get('Marital status', '')),
            "religion": safe_convert(candidate.get('Religion', '')),
            "phone_number": safe_convert(candidate.get('Phone number', '')),
            "residential_address": safe_convert(candidate.get('Residential address', '')),
            "current_employment": safe_convert(candidate.get('Current employment or occupation (if applicable)', '')),
            "employment_category": safe_convert(candidate.get('Current employment or occupational category', '')),
            "company_address": safe_convert(candidate.get('Company address', '')),
            "university_attended": safe_convert(candidate.get('University attended', '')),
            "undergraduate_degree_type": safe_convert(candidate.get('Degree type  (undergraduate)', '')),
            "undergraduate_programme": safe_convert(candidate.get('Programme (undergraduate)', '')),
            "undergraduate_class": safe_convert(candidate.get('Class of degree (undergraduate)', '')),
            "undergraduate_completion_date": safe_convert(candidate.get('Date of completion (undergraduate)', '')),
            "postgraduate_degree_type": safe_convert(candidate.get('Degree type (postgraduate)', '')),
            "postgraduate_programme": safe_convert(candidate.get('Programme (postgraduate)', '')),
            "postgraduate_class": safe_convert(candidate.get('Class of degree (postgraduate)', '')),
            "postgraduate_completion_date": safe_convert(candidate.get('Date of completion/Expected date of completion (postgraduate)', '')),
            "education_qualifications": safe_convert(candidate.get('Education qualification(s)', '')),
            "professional_qualifications": safe_convert(candidate.get('Professional qualification(s)', '')),
            "career_interests": safe_convert(candidate.get('Career interests', '')),
            "msa_interest": safe_convert(candidate.get('Would you be interested in joining the Management Scholars Academy (MSA) if such an option is available? See https://www.lbs.edu.ng/faculty-and-research/management-scholars-academy-2/ for details', '')),
            "previous_applications": safe_convert(candidate.get('Have you applied for this programme before?', '')),
            "candidate_essay": safe_convert(candidate.get('Write an essay demonstrating why you are an ideal candidate for this programmme, highlighting all significant details', '')),
            
            # File URLs
            "cv_url": safe_convert(candidate.get('Curriculum vitae ', '')),
            "video_url": safe_convert(candidate.get('Create a video presentation describing yourself and share your experiences', '')),
            
            # File processing results
            "cv_text": file_results.cv_text,
            "video_transcript": file_results.video_transcript,
            "processing_errors": file_results.errors,
            
            # Processing metadata
            "evaluation_timestamp": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "files_processed_successfully": len(file_results.errors) == 0
        }
        
        return comprehensive_result

    async def process_all_candidates(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process all candidates asynchronously with controlled concurrency"""
        semaphore = asyncio.Semaphore(3)  # Limit concurrent processing to 3
        
        async def process_with_semaphore(email):
            async with semaphore:
                print(f"Processing candidate: {email}")
                try:
                    result = await self.create_comprehensive_evaluation(email, data)
                    print(f"Completed: {email}")
                    return result
                except Exception as e:
                    print(f"Error processing {email}: {str(e)}")
                    return {"error": f"Processing failed for {email}: {str(e)}", "email": email}
        
        tasks = [
            process_with_semaphore(email) 
            for email in data['Email address'].dropna()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results