"""
Configuration Management
Handles loading and accessing configuration from environment and files
"""

import os
import yaml
from typing import Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Configuration management class
    Loads from environment variables and YAML config files
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to YAML configuration file
        """
        # Load YAML config
        if config_path is None:
            config_path = os.getenv('CONFIG_PATH', 'config/velma_config.yaml')

        self.config_path = config_path
        self.config_data = self._load_yaml_config()

        # Environment variables (take precedence over YAML)
        self.env = os.environ

    def _load_yaml_config(self) -> dict:
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)

        if not config_file.exists():
            return {}

        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports dot notation, e.g., 'modules.calendar.enabled')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Check environment variables first (convert dots to underscores and uppercase)
        env_key = key.upper().replace('.', '_')
        env_value = self.env.get(env_key)

        if env_value is not None:
            # Convert string booleans to actual booleans
            if env_value.lower() in ('true', 'yes', '1'):
                return True
            elif env_value.lower() in ('false', 'no', '0'):
                return False
            # Try to convert to int/float
            try:
                if '.' in env_value:
                    return float(env_value)
                else:
                    return int(env_value)
            except ValueError:
                return env_value

        # Navigate through nested config using dot notation
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value if value is not None else default

    @property
    def anthropic_api_key(self) -> str:
        """Get Anthropic API key"""
        return self.env.get('ANTHROPIC_API_KEY', '')

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key"""
        return self.env.get('OPENAI_API_KEY', '')

    @property
    def ai_model(self) -> str:
        """Get AI model name"""
        return self.env.get('AI_MODEL', self.get('velma.ai.model', 'claude-sonnet-4-5-20250929'))

    @property
    def database_url(self) -> str:
        """Get database URL"""
        return self.env.get('DATABASE_URL', '')

    @property
    def redis_url(self) -> str:
        """Get Redis URL"""
        return self.env.get('REDIS_URL', 'redis://localhost:6379/0')

    @property
    def company_name(self) -> str:
        """Get company name"""
        return self.env.get('COMPANY_NAME', 'Your NDIS Company')

    @property
    def company_abn(self) -> str:
        """Get company ABN"""
        return self.env.get('COMPANY_ABN', '')

    @property
    def timezone(self) -> str:
        """Get timezone"""
        return self.env.get('TIMEZONE', 'Australia/Sydney')

    def __repr__(self) -> str:
        return f"<Config from {self.config_path}>"
