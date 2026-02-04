"""
Decision Engine
Makes intelligent decisions about routing, prioritization, and actions
"""

from typing import Dict, Any, List
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Makes intelligent decisions for Velma
    Handles routing, prioritization, and action selection
    """

    def __init__(self, config):
        """
        Initialize decision engine

        Args:
            config: Application configuration
        """
        self.config = config

    def should_handle_now(self, intent: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if request should be handled immediately or deferred

        Args:
            intent: Classified intent
            context: Session context

        Returns:
            True if should handle now
        """
        # Always handle critical urgency immediately
        if intent.get('urgency') == 'critical':
            return True

        # Handle during business hours
        if self._is_business_hours():
            return True

        # Defer low urgency items outside business hours
        if intent.get('urgency') == 'low':
            return False

        return True

    def _is_business_hours(self) -> bool:
        """
        Check if current time is within business hours

        Returns:
            True if within business hours
        """
        now = datetime.now()
        day_name = now.strftime('%A').lower()

        business_hours = self.config.get(f'routing.business_hours.{day_name}')

        if business_hours is None:
            return False  # Weekend or day off

        start_time = datetime.strptime(business_hours[0], '%H:%M').time()
        end_time = datetime.strptime(business_hours[1], '%H:%M').time()
        current_time = now.time()

        return start_time <= current_time <= end_time

    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize a list of tasks

        Args:
            tasks: List of task dictionaries

        Returns:
            Sorted list of tasks by priority
        """
        priority_values = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }

        def task_score(task):
            urgency_score = priority_values.get(task.get('urgency', 'medium'), 2)
            deadline_score = 0

            # Add deadline proximity score
            if 'deadline' in task:
                deadline = task['deadline']
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline)

                days_until = (deadline - datetime.now()).days
                if days_until < 1:
                    deadline_score = 3
                elif days_until < 3:
                    deadline_score = 2
                elif days_until < 7:
                    deadline_score = 1

            return (urgency_score * 10) + deadline_score

        return sorted(tasks, key=task_score, reverse=True)

    def select_best_meeting_time(
        self,
        availability: List[Dict[str, Any]],
        duration: int,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select optimal meeting time from available slots

        Args:
            availability: List of available time slots
            duration: Meeting duration in minutes
            preferences: User preferences

        Returns:
            Best meeting time slot
        """
        if not availability:
            return None

        # Score each slot based on preferences
        scored_slots = []

        for slot in availability:
            score = 0
            slot_time = datetime.fromisoformat(slot['start']).time()

            # Prefer morning meetings (9-12)
            if time(9, 0) <= slot_time <= time(12, 0):
                score += 3

            # Prefer afternoon meetings (2-4)
            elif time(14, 0) <= slot_time <= time(16, 0):
                score += 2

            # Prefer earlier in the week
            slot_day = datetime.fromisoformat(slot['start']).weekday()
            score += (5 - slot_day) * 0.5

            # Prefer slots with buffer time before/after
            if slot.get('buffer_before', 0) >= 15:
                score += 1
            if slot.get('buffer_after', 0) >= 15:
                score += 1

            scored_slots.append((score, slot))

        # Return highest scoring slot
        scored_slots.sort(key=lambda x: x[0], reverse=True)
        return scored_slots[0][1]

    def should_auto_respond(
        self,
        email: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Determine if email should be auto-responded to

        Args:
            email: Email data
            context: Context information

        Returns:
            True if should auto-respond
        """
        # Don't auto-respond if disabled
        if not self.config.get('modules.communication.email.auto_reply_enabled', False):
            return False

        # Don't auto-respond to urgent emails
        if 'urgent' in email.get('subject', '').lower():
            return False

        # Don't auto-respond to complex requests
        if email.get('complexity', 'low') in ['high', 'critical']:
            return False

        # Auto-respond to common inquiries
        common_subjects = ['inquiry', 'information', 'question', 'hello', 'hi']
        if any(sub in email.get('subject', '').lower() for sub in common_subjects):
            return True

        return False

    def calculate_confidence(
        self,
        intent: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for an action

        Args:
            intent: Intent classification
            entities: Extracted entities

        Returns:
            Confidence score 0-1
        """
        # Start with intent confidence
        confidence = intent.get('confidence', 0.5)

        # Boost if all required entities are present
        if entities:
            entity_completeness = len([v for v in entities.values() if v]) / max(len(entities), 1)
            confidence = (confidence + entity_completeness) / 2

        # Penalize if conflicting signals
        if intent.get('secondary_intents'):
            confidence *= 0.9

        return min(confidence, 1.0)
