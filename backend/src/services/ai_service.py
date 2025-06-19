import json
import asyncio
from typing import Dict, Any, Optional, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI

from src.config.settings import AppConfig, SYSTEM_PROMPT_TEMPLATE, get_json_schema

if TYPE_CHECKING:
    from src.services.database_service import DatabaseService

class AIEvaluationService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = AzureOpenAI(
            api_key=config.azure_openai_api_key,
            api_version="2023-12-01-preview",
            azure_endpoint=config.azure_openai_endpoint
        )
    
    async def evaluate_candidate(
        self, 
        candidate_text: str, 
        user_id: str = None,
        db_service: "DatabaseService" = None
    ) -> Dict[str, Any]:
        """Evaluate candidate using AI with user-specific criteria"""
        try:
            # Get user-specific criteria if available
            eligibility_criteria = await self._get_user_criteria(user_id, db_service)
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    self._evaluate_candidate_sync, 
                    candidate_text,
                    eligibility_criteria
                )
            return json.loads(result)
        except json.JSONDecodeError:
            return {"outcome": "Error", "score": 0.0, "rationale": "Failed to parse AI evaluation"}
        except Exception as e:
            return {"outcome": "Error", "score": 0.0, "rationale": f"Evaluation error: {str(e)}"}
    
    async def _get_user_criteria(self, user_id: str, db_service: "DatabaseService") -> str:
        """Get user-specific eligibility criteria"""
        if user_id and db_service and db_service.is_available():
            criteria = await db_service.get_active_criteria(user_id)
            if criteria:
                return criteria.content
        
        # Fallback to default criteria
        from src.config.settings import ELIGIBILITY_CRITERIA
        return ELIGIBILITY_CRITERIA
    
    def _evaluate_candidate_sync(self, candidate_text: str, eligibility_criteria: str) -> str:
        """Synchronous AI evaluation helper with dynamic criteria"""
        dynamic_prompt = f"""
        {SYSTEM_PROMPT_TEMPLATE.replace("{schema}", get_json_schema())}
        
        SPECIFIC ELIGIBILITY CRITERIA FOR THIS EVALUATION:
        {eligibility_criteria}
        
        Evaluate the candidate strictly against these criteria.
        """
        
        response = self.client.chat.completions.create(
            model=self.config.deployment_name,
            messages=[
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": f"Please evaluate the candidate's application based on the following information:\n\n{candidate_text}"}
            ],
            response_format={"type": "json_object"},
            seed=42,
            max_tokens=4096,
            temperature=0,
            frequency_penalty=0,
            top_p=1,
        )
        
        return response.choices[0].message.content