"""
Task & Project Coordination Module
Handles task management, deadlines, and project tracking
"""

from typing import Dict, Any
from anthropic import AsyncAnthropic
from ...utils.logger import get_logger

logger = get_logger(__name__)


class TaskModule:
    """Task management and coordination module"""

    def __init__(self, config):
        self.config = config
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)
        logger.info("Task Module initialized")

    async def process(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process task management requests"""

        system_prompt = """You are Velma's task coordination assistant.
        Help with:
        - Creating and managing to-do lists
        - Tracking deadlines and deliverables
        - Following up on pending items
        - Prioritizing tasks

        Be organized and proactive."""

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
            "module": "tasks"
        }

    async def shutdown(self):
        logger.info("Task Module shutting down")
