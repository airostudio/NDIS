"""
Communication Management Module
Handles email, messages, and correspondence
"""

from typing import Dict, Any
from anthropic import AsyncAnthropic
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CommunicationModule:
    """Communication and correspondence module"""

    def __init__(self, config):
        self.config = config
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)
        logger.info("Communication Module initialized")

    async def process(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process communication requests"""

        system_prompt = f"""You are Cheryl's communication assistant for {self.config.company_name}.
        Help with emails, messages, and professional correspondence.

        Use professional, clear Australian English.
        Be helpful with drafting, filtering, and managing communications."""

        response = await self.ai_client.messages.create(
            model=self.config.ai_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )

        return {
            "status": "success",
            "message": response.content[0].text,
            "action": "inform",
            "module": "communication"
        }

    async def shutdown(self):
        logger.info("Communication Module shutting down")
