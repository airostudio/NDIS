"""
Receptionist Module
Handles calls, visitors, and information requests
"""

from typing import Dict, Any
from anthropic import AsyncAnthropic
from ...utils.logger import get_logger

logger = get_logger(__name__)


class ReceptionistModule:
    """Receptionist and front-desk module"""

    def __init__(self, config):
        self.config = config
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self.greeting = config.get(
            'modules.receptionist.greeting',
            f"Thank you for calling {config.company_name}. This is Cheryl, how may I help you today?"
        )
        logger.info("Receptionist Module initialized")

    async def process(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process receptionist requests"""

        system_prompt = f"""You are Cheryl, the receptionist for {self.config.company_name}, an NDIS service provider.

        Greeting: "{self.greeting}"

        You handle:
        - Incoming calls and route them appropriately
        - Visitor check-in and management
        - General inquiries about services
        - Appointment scheduling

        Be warm, professional, and helpful. Use Australian English."""

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
            "module": "receptionist"
        }

    async def shutdown(self):
        logger.info("Receptionist Module shutting down")
