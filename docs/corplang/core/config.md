# Configuration Manager

The `ConfigManager` provides a centralized way to handle interpreter settings, primarily through a `config.yml` file.

### Key Features

*   **Singleton Pattern:** Ensures a single instance of configuration throughout the application.
*   **YAML Support:** Loads structured configuration from standard YAML files.
*   **Automatic Logging Setup:** Configures Python's native `logging` module based on the provided settings.
*   **Robust Defaults:** Provides fallback values if the configuration file is missing or corrupted.

### Public API

#### `get_logger(name: str) -> logging.Logger`
A convenience function to obtain a configured logger instance for a specific module.

*   `name`: Typically `__name__` of the calling module.

#### `config_manager.get(key: str, default: Any = None) -> Any`
Retrieves a specific configuration value.

*   `key`: The name of the configuration setting.
*   `default`: The value to return if the key is not found.

### Configuration File (`config.yml`)

The interpreter looks for a `config.yml` at the project root. Example structure:

```yaml
logging:
  level: "DEBUG"
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```
