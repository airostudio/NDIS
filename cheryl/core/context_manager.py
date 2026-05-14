"""
Context Manager
Manages conversation context and user session state
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages conversation context across sessions
    Stores user preferences, conversation history, and state
    """

    def __init__(self, ttl: int = 3600):
        """
        Initialize context manager

        Args:
            ttl: Time-to-live for context in seconds (default 1 hour)
        """
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def get_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context for a user

        Args:
            user_id: User identifier

        Returns:
            User context dictionary
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "conversation_history": [],
                "preferences": {},
                "state": {},
            }
        else:
            # Update last activity
            self.contexts[user_id]["last_activity"] = datetime.now()

        # Clean expired contexts
        self._clean_expired_contexts()

        return self.contexts[user_id]

    def update_context(self, user_id: str, data: Dict[str, Any]):
        """
        Update user context with new data

        Args:
            user_id: User identifier
            data: Data to merge into context
        """
        context = self.get_context(user_id)
        context.update(data)
        context["last_activity"] = datetime.now()

    def add_to_history(
        self,
        user_id: str,
        role: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add message to conversation history

        Args:
            user_id: User identifier
            role: Message role (user, assistant, system)
            message: Message content
            metadata: Optional metadata
        """
        context = self.get_context(user_id)

        history_entry = {
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        context["conversation_history"].append(history_entry)

        # Keep only last 50 messages to avoid memory issues
        if len(context["conversation_history"]) > 50:
            context["conversation_history"] = context["conversation_history"][-50:]

    def get_history(self, user_id: str, limit: int = 10) -> list:
        """
        Get conversation history for user

        Args:
            user_id: User identifier
            limit: Maximum number of messages to return

        Returns:
            List of conversation history entries
        """
        context = self.get_context(user_id)
        history = context.get("conversation_history", [])
        return history[-limit:] if limit else history

    def set_preference(self, user_id: str, key: str, value: Any):
        """
        Set user preference

        Args:
            user_id: User identifier
            key: Preference key
            value: Preference value
        """
        context = self.get_context(user_id)
        context["preferences"][key] = value

    def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Get user preference

        Args:
            user_id: User identifier
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        context = self.get_context(user_id)
        return context.get("preferences", {}).get(key, default)

    def set_state(self, user_id: str, key: str, value: Any):
        """
        Set state value for user

        Args:
            user_id: User identifier
            key: State key
            value: State value
        """
        context = self.get_context(user_id)
        context["state"][key] = value

    def get_state(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Get state value for user

        Args:
            user_id: User identifier
            key: State key
            default: Default value if not found

        Returns:
            State value or default
        """
        context = self.get_context(user_id)
        return context.get("state", {}).get(key, default)

    def clear_context(self, user_id: str):
        """
        Clear context for user

        Args:
            user_id: User identifier
        """
        if user_id in self.contexts:
            del self.contexts[user_id]
            logger.info(f"Cleared context for user {user_id}")

    def _clean_expired_contexts(self):
        """Remove expired contexts based on TTL"""
        now = datetime.now()
        expired_users = []

        for user_id, context in self.contexts.items():
            last_activity = context.get("last_activity", now)
            if now - last_activity > timedelta(seconds=self.ttl):
                expired_users.append(user_id)

        for user_id in expired_users:
            del self.contexts[user_id]
            logger.debug(f"Expired context for user {user_id}")

    def get_summary(self, user_id: str) -> str:
        """
        Get a summary of the user's context

        Args:
            user_id: User identifier

        Returns:
            Context summary string
        """
        context = self.get_context(user_id)
        history_count = len(context.get("conversation_history", []))

        summary = f"User: {user_id}\n"
        summary += f"Active for: {datetime.now() - context['created_at']}\n"
        summary += f"Messages: {history_count}\n"
        summary += f"Last intent: {context.get('last_intent', {}).get('primary_intent', 'N/A')}\n"

        return summary
