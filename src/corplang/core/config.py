import logging
import logging.config
import yaml
import os
from typing import Any, Dict, Optional


class ConfigManager:
    """
    Centralized configuration manager for the Corplang interpreter.
    Loads settings from a YAML file.
    """
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def load_config(self, config_path: str = "config.yml"):
        """Loads configuration from a YAML file."""
        if not os.path.exists(config_path):
            # Default minimal config if the file doesn't exist
            self._config = {
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }
        else:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}

        self._setup_logging()

    def _setup_logging(self):
        """Sets up the native logging based on the configuration."""
        logging_config = self._config.get("logging", {})
        level = logging_config.get("level", "INFO")
        log_format = logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                            format=log_format)

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a configuration value by key."""
        return self._config.get(key, default)


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance."""
    return logging.getLogger(name)


# Initialize global config manager
config_manager = ConfigManager()
config_manager.load_config()
