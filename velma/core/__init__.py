"""
Velma Core Module
Central orchestration and AI engine for the NDIS Virtual Executive Suite
"""

from .velma import Velma
from .context_manager import ContextManager
from .decision_engine import DecisionEngine

__all__ = ["Velma", "ContextManager", "DecisionEngine"]
