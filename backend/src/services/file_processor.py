import os
import asyncio
import whisper
from concurrent.futures import ThreadPoolExecutor
import PyPDF2
from docx import Document

class FileProcessor:
    @staticmethod
    async def safe_delete_file(file_path: str, max_attempts: int = 3) -> bool:
        """Safely delete file with retry mechanism"""
        for attempt in range(max_attempts):
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                return True
            except PermissionError:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.5)
                    continue
                else:
                    print(f"Warning: Could not delete temporary file {file_path}")
                    return False
        return False
    
    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    FileProcessor._extract_pdf_sync, 
                    file_path
                )
            return result
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    @staticmethod
    def _extract_pdf_sync(file_path: str) -> str:
        """Synchronous PDF extraction helper"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    async def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    FileProcessor._extract_docx_sync, 
                    file_path
                )
            return result
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"
    
    @staticmethod
    def _extract_docx_sync(file_path: str) -> str:
        """Synchronous DOCX extraction helper"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        doc = None  # Explicitly close
        return text.strip()
    
    @staticmethod
    async def transcribe_video(video_path: str) -> str:
        """Transcribe video using Whisper asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    FileProcessor._transcribe_video_sync, 
                    video_path
                )
            return result
        except Exception as e:
            return f"Error transcribing video: {str(e)}"
    
    @staticmethod
    def _transcribe_video_sync(video_path: str) -> str:
        """Synchronous video transcription helper"""
        model = whisper.load_model("base")
        result = model.transcribe(video_path, language='en', task='transcribe')
        return result["text"]