from pathlib import Path

from src.commands.utils.utils import Output, CLIResult


def init_migrations(path: str = "migrations") -> CLIResult:
    """Initialize migrations directory."""
    mig_path = Path(path)
    mig_path.mkdir(exist_ok=True, parents=True)

    config_file = mig_path / "config.yaml"
    if not config_file.exists():
        config_content = """# Database migration configuration
        driver: null
        dsn: null
        auto_discover: true
        """
        config_file.write_text(config_content)

    (mig_path / "__init__.py").write_text("")

    Output.success(f"Migrations directory initialized at {path}")
    return CLIResult(success=True, message="Migrations initialized")


def test_connection(driver: str, dsn: str) -> CLIResult:
    """Test database connection."""
    try:
        Output.info(f"Testing connection to {driver}://{dsn[:30]}...")

        if driver == "sqlite":
            import sqlite3
            conn = sqlite3.connect(dsn)
            conn.close()
            Output.success("Connection successful")
            return CLIResult(success=True, message="Connection verified")

        else:
            Output.warning(f"Driver '{driver}' not yet supported")
            return CLIResult(success=False, message="Driver not supported", exit_code=1)

    except Exception as e:
        Output.error(f"Connection failed: {e}")
        return CLIResult(success=False, message=f"Connection error: {e}", exit_code=1)


def handle_db(args) -> CLIResult:
    """CLI handler for db command."""
    if not args.db_cmd:
        Output.info("Database operations (migrations, schema management)")
        return CLIResult(success=True, message="")

    if args.db_cmd == "init":
        path = getattr(args, "path", "migrations")
        return init_migrations(path)

    elif args.db_cmd == "connect":
        driver = getattr(args, "driver", None)
        dsn = getattr(args, "dsn", None)
        if not driver or not dsn:
            return CLIResult(
                success=False,
                message="Driver and DSN required",
                exit_code=1,
            )
        return test_connection(driver, dsn)

    elif args.db_cmd == "makemigrations":
        Output.warning("Migration generation not yet implemented")
        return CLIResult(success=False, message="Not implemented", exit_code=1)

    elif args.db_cmd == "migrate":
        Output.warning("Migration application not yet implemented")
        return CLIResult(success=False, message="Not implemented", exit_code=1)

    return CLIResult(success=False, message="Unknown db command", exit_code=1)
