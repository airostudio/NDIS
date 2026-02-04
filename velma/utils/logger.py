"""
Logging Configuration
Centralized logging setup for Velma
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON

        Args:
            record: Log record

        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Mask sensitive data
        log_data = self._mask_sensitive_data(log_data)

        return json.dumps(log_data)

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive information in log data

        Args:
            data: Log data dictionary

        Returns:
            Masked log data
        """
        sensitive_keys = [
            "password",
            "api_key",
            "secret",
            "token",
            "authorization",
            "credit_card",
            "ssn",
            "medicare",
        ]

        masked_data = data.copy()

        for key, value in masked_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "***" + value[-2:]
                else:
                    masked_data[key] = "***"

        return masked_data


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Use JSON formatter if configured
    log_format = os.getenv("LOG_FORMAT", "text")
    if log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


# Create a default logger for the application
velma_logger = get_logger("velma")
