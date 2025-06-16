import json
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI

from src.config.settings import AppConfig, SYSTEM_PROMPT, ELIGIBILITY_CRITERIA

class AIEvaluationService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = AzureOpenAI(
            api_key=config.azure_openai_api_key,
            api_version="2023-12-01-preview",
            azure_endpoint=config.azure_openai_endpoint
        )
    
    async def evaluate_candidate(self, candidate_text: str) -> Dict[str, Any]:
        """Evaluate candidate using AI asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    self._evaluate_candidate_sync, 
                    candidate_text
                )
            return json.loads(result)
        except json.JSONDecodeError:
            return {"outcome": "Error", "rationale": "Failed to parse AI evaluation"}
        except Exception as e:
            return {"outcome": "Error", "rationale": f"Evaluation error: {str(e)}"}
    
    def _evaluate_candidate_sync(self, candidate_text: str) -> str:
        """Synchronous AI evaluation helper"""
        dynamic_prompt = f"""
        {SYSTEM_PROMPT}
        
        SPECIFIC ELIGIBILITY CRITERIA FOR THIS EVALUATION:
        {ELIGIBILITY_CRITERIA}
        
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