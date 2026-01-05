from src.commands.config import ConfigManager
from src.commands.utils.utils import Output, CLIResult


def validate_env() -> CLIResult:
    """Validate environment setup."""
    Output.section("Environment Validation")

    cm = ConfigManager()
    validation = cm.validate()

    Output.print(f"Project root: {cm.project_root}")
    Output.print(f"eco.system.json: {'✓' if validation['has_eco'] else '✗'}")
    Output.print(f"language_config.yaml: {'✓' if validation['has_language_config'] else '✗'}")

    if validation["issues"]:
        Output.section("Issues Found")
        for issue in validation["issues"]:
            Output.warning(issue)
        return CLIResult(success=False, message="Environment has issues", exit_code=1)

    Output.success("Environment is valid")
    return CLIResult(success=True, message="All checks passed")


def sync_config() -> CLIResult:
    """Synchronize configuration files."""
    cm = ConfigManager()

    Output.info("Synchronizing configuration files...")

    if cm.sync():
        Output.success("Configuration synchronized")
        return CLIResult(success=True, message="Configurations synced")
    else:
        Output.error("Failed to synchronize configuration")
        return CLIResult(success=False, message="Sync failed", exit_code=1)


def show_config() -> CLIResult:
    """Show current configuration."""
    cm = ConfigManager()

    eco = cm.load_eco_system()
    lang = cm.load_language_config()

    Output.section("eco.system.json")
    if eco:
        import json
        Output.print(json.dumps(eco, indent=2))
    else:
        Output.print("(not configured)")

    Output.section("language_config.yaml")
    if lang:
        import json
        Output.print(json.dumps(lang, indent=2))
    else:
        Output.print("(not configured)")

    return CLIResult(success=True, message="")


def handle_env(args) -> CLIResult:
    """CLI handler for env command."""
    if not args.env_cmd:
        return validate_env()

    if args.env_cmd == "validate":
        return validate_env()

    elif args.env_cmd == "config":
        action = getattr(args, "action", "validate")
        if action == "validate":
            return validate_env()
        elif action == "sync":
            return sync_config()
        elif action == "show":
            return show_config()

    return CLIResult(success=False, message="Unknown env command", exit_code=1)
