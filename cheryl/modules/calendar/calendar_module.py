"""
Calendar & Time Management Module
Handles scheduling, meetings, and calendar coordination
"""

from typing import Dict, Any
from anthropic import AsyncAnthropic
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CalendarModule:
    """Calendar and scheduling module"""

    def __init__(self, config):
        self.config = config
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)
        logger.info("Calendar Module initialized")

    async def process(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process calendar requests"""

        system_prompt = f"""You are Cheryl's calendar assistant for {self.config.company_name}.
        Help with scheduling, appointments, and time management.

        Business hours: {self.config.get('routing.business_hours.monday', ['9:00', '17:00'])}
        Timezone: {self.config.timezone}

        Provide helpful scheduling assistance."""

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
            "module": "calendar"
        }

    async def shutdown(self):
        logger.info("Calendar Module shutting down")
