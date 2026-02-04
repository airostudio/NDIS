"""
Velma - Core AI Orchestrator
The main AI engine that coordinates all modules and handles intelligent routing
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from anthropic import Anthropic, AsyncAnthropic
import yaml

from .context_manager import ContextManager
from .decision_engine import DecisionEngine
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Velma:
    """
    Velma - NDIS Virtual AI Executive Suite

    Central orchestrator that manages all executive assistant, receptionist,
    HR, and payroll functions for NDIS companies.
    """

    def __init__(self, config: Config):
        """
        Initialize Velma with configuration

        Args:
            config: Application configuration object
        """
        self.config = config
        self.context_manager = ContextManager()
        self.decision_engine = DecisionEngine(config)

        # Initialize AI client
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)

        # Module registry
        self.modules: Dict[str, Any] = {}

        # Initialize modules
        self._initialize_modules()

        logger.info("Velma initialized successfully")

    def _initialize_modules(self):
        """Initialize all enabled modules"""
        from ..modules.calendar import CalendarModule
        from ..modules.communication import CommunicationModule
        from ..modules.receptionist import ReceptionistModule
        from ..modules.hr import HRModule
        from ..modules.payroll import PayrollModule
        from ..modules.tasks import TaskModule
        from ..modules.relationships import RelationshipModule

        # Load each module if enabled in config
        module_classes = {
            'calendar': CalendarModule,
            'communication': CommunicationModule,
            'receptionist': ReceptionistModule,
            'hr': HRModule,
            'payroll': PayrollModule,
            'tasks': TaskModule,
            'relationships': RelationshipModule,
        }

        for module_name, module_class in module_classes.items():
            if self.config.get(f'modules.{module_name}.enabled', True):
                try:
                    self.modules[module_name] = module_class(self.config)
                    logger.info(f"Module '{module_name}' loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load module '{module_name}': {e}")

    async def process_request(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        channel: str = "chat",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming request from any channel

        Args:
            message: The user's message/request
            context: Optional context information
            channel: Communication channel (chat, email, voice, sms)
            user_id: Optional user identifier

        Returns:
            Response dictionary with action, message, and metadata
        """
        try:
            # Update context
            session_context = self.context_manager.get_context(user_id or "default")
            if context:
                session_context.update(context)

            # Log the request
            logger.info(f"Processing request from {channel}: {message[:100]}...")

            # Classify intent and route to appropriate module
            intent = await self._classify_intent(message, session_context)

            # Check if escalation is needed
            if self._should_escalate(message, intent, session_context):
                return await self._escalate(message, intent, session_context)

            # Route to appropriate module
            response = await self._route_to_module(intent, message, session_context)

            # Update context with response
            self.context_manager.update_context(
                user_id or "default",
                {"last_intent": intent, "last_response": response}
            )

            # Log successful processing
            logger.info(f"Request processed successfully: {intent['primary_intent']}")

            return response

        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "I apologize, but I encountered an error processing your request. "
                          "Let me transfer you to a human assistant.",
                "action": "escalate",
                "error": str(e)
            }

    async def _classify_intent(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to classify user intent and extract key information

        Args:
            message: User message
            context: Session context

        Returns:
            Intent classification with confidence scores
        """
        system_prompt = """You are Velma, an AI assistant for an NDIS company.
        Analyze the user's message and classify their intent.

        Available intents:
        - calendar: Schedule, reschedule, or check appointments/meetings
        - communication: Email, messages, correspondence
        - receptionist: Calls, visitors, general inquiries
        - hr: Employee matters, compliance, worker screening, onboarding
        - payroll: Pay calculations, timesheets, leave, SCHADS Award questions
        - tasks: Task management, deadlines, to-dos
        - relationships: Contact management, reminders, networking
        - general: General questions or chat

        Return a JSON object with:
        - primary_intent: The main intent
        - secondary_intents: List of related intents
        - confidence: Confidence score 0-1
        - entities: Extracted entities (dates, names, amounts, etc.)
        - urgency: low, medium, high, critical
        - sentiment: positive, neutral, negative
        """

        try:
            response = await self.ai_client.messages.create(
                model=self.config.ai_model,
                max_tokens=1024,
                temperature=0.3,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Context: {context}\n\nMessage: {message}"
                }]
            )

            # Parse AI response
            import json
            intent_data = json.loads(response.content[0].text)

            return intent_data

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Fallback to simple keyword matching
            return self._fallback_intent_classification(message)

    def _fallback_intent_classification(self, message: str) -> Dict[str, Any]:
        """Simple keyword-based intent classification as fallback"""
        message_lower = message.lower()

        keywords = {
            'calendar': ['meeting', 'appointment', 'schedule', 'calendar', 'book', 'reschedule'],
            'communication': ['email', 'message', 'send', 'reply', 'draft'],
            'receptionist': ['call', 'visitor', 'reception', 'phone', 'transfer'],
            'hr': ['employee', 'worker', 'screening', 'wwcc', 'onboarding', 'compliance'],
            'payroll': ['pay', 'payroll', 'timesheet', 'hours', 'schads', 'leave', 'superannuation'],
            'tasks': ['task', 'todo', 'deadline', 'project', 'follow up'],
            'relationships': ['contact', 'birthday', 'anniversary', 'reminder'],
        }

        intent_scores = {}
        for intent, words in keywords.items():
            score = sum(1 for word in words if word in message_lower)
            if score > 0:
                intent_scores[intent] = score

        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[primary_intent] / 3, 1.0)
        else:
            primary_intent = 'general'
            confidence = 0.5

        return {
            'primary_intent': primary_intent,
            'secondary_intents': [],
            'confidence': confidence,
            'entities': {},
            'urgency': 'medium',
            'sentiment': 'neutral'
        }

    def _should_escalate(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Determine if request should be escalated to human

        Args:
            message: User message
            intent: Classified intent
            context: Session context

        Returns:
            True if should escalate
        """
        # Auto-escalate keywords
        escalate_keywords = self.config.get('routing.auto_escalate.keywords', [])
        if any(keyword in message.lower() for keyword in escalate_keywords):
            return True

        # Escalate on very negative sentiment
        sentiment_threshold = self.config.get('routing.auto_escalate.sentiment_threshold', -0.7)
        if intent.get('sentiment') == 'negative' and intent.get('confidence', 0) < 0.5:
            return True

        # Escalate critical urgency
        if intent.get('urgency') == 'critical':
            return True

        # Escalate if low confidence and high stakes
        if intent.get('confidence', 1.0) < 0.4 and intent.get('urgency') in ['high', 'critical']:
            return True

        return False

    async def _escalate(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Escalate to appropriate human

        Args:
            message: User message
            intent: Classified intent
            context: Session context

        Returns:
            Escalation response
        """
        # Determine escalation contact based on intent
        escalation_map = {
            'hr': self.config.get('routing.escalation.hr_contact'),
            'payroll': self.config.get('routing.escalation.hr_contact'),
            'emergency': self.config.get('routing.escalation.after_hours_contact'),
            'technical': self.config.get('routing.escalation.technical_contact'),
        }

        contact = escalation_map.get(
            intent.get('primary_intent'),
            self.config.get('routing.escalation.priority_contact')
        )

        logger.warning(f"Escalating request to {contact}: {message[:100]}")

        # Notify the contact (implement notification logic)
        await self._notify_escalation(contact, message, intent, context)

        return {
            "status": "escalated",
            "message": f"I've escalated your request to {contact} who will assist you shortly. "
                      "They will be in touch within the next 30 minutes.",
            "action": "escalate",
            "contact": contact
        }

    async def _notify_escalation(
        self,
        contact: str,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """Send notification to escalation contact"""
        # This would integrate with email/SMS modules
        logger.info(f"Sending escalation notification to {contact}")
        # TODO: Implement actual notification

    async def _route_to_module(
        self,
        intent: Dict[str, Any],
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route request to appropriate module

        Args:
            intent: Classified intent
            message: User message
            context: Session context

        Returns:
            Module response
        """
        primary_intent = intent.get('primary_intent', 'general')

        if primary_intent in self.modules:
            module = self.modules[primary_intent]
            return await module.process(message, intent, context)
        else:
            # Handle general queries with AI
            return await self._handle_general_query(message, context)

    async def _handle_general_query(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general queries that don't fit specific modules"""
        system_prompt = f"""You are Velma, a helpful AI assistant for {self.config.company_name},
        an NDIS service provider. You assist with executive tasks, reception, HR, and payroll.

        Be professional, friendly, and helpful. Use Australian English.
        If you don't know something, be honest and offer to find out or escalate.
        """

        try:
            response = await self.ai_client.messages.create(
                model=self.config.ai_model,
                max_tokens=2048,
                temperature=0.7,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )

            return {
                "status": "success",
                "message": response.content[0].text,
                "action": "respond",
                "intent": "general"
            }

        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return {
                "status": "error",
                "message": "I apologize, but I'm having trouble processing that. "
                          "Could you please rephrase or let me transfer you to someone who can help?",
                "action": "error"
            }

    async def proactive_tasks(self):
        """Run proactive tasks (morning briefing, reminders, etc.)"""
        if not self.config.get('proactive.enabled', True):
            return

        logger.info("Running proactive tasks...")

        # Morning briefing
        # End of day summary
        # Deadline warnings
        # Compliance reminders

        # This would be scheduled via APScheduler or Celery
        pass

    async def shutdown(self):
        """Gracefully shutdown Velma"""
        logger.info("Shutting down Velma...")

        # Close module connections
        for module_name, module in self.modules.items():
            if hasattr(module, 'shutdown'):
                await module.shutdown()

        logger.info("Velma shutdown complete")
