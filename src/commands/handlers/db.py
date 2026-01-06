from pathlib import Path
import json
from src.commands.utils.utils import Output, CLIResult
from src.corplang.executor.db.model_parser import parse_models
from src.corplang.executor.db.schema_graph import build_graph, compute_initial_plan
from src.corplang.executor.db.migrations import write_snapshot, write_plan, apply_sqlite


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
        try:
            # Discover a models file (minimal heuristic)
            candidates = [
                Path("examples/orm_demo/models.mp"),
                Path("models.mp"),
            ]
            src_file = next((p for p in candidates if p.exists()), None)
            if not src_file:
                Output.error("No models file found (expected examples/orm_demo/models.mp or ./models.mp)")
                return CLIResult(success=False, message="No models file", exit_code=1)

            source = src_file.read_text(encoding="utf-8")
            schema = parse_models(source)
            graph = build_graph(schema)
            ops = compute_initial_plan(graph)

            mig_dir = Path("migrations")
            mig_dir.mkdir(exist_ok=True)
            write_snapshot(mig_dir / "schema.json", graph)
            write_plan(mig_dir / "plan.initial.json", ops)

            Output.success(f"Migrations generated: {mig_dir}/plan.initial.json")
            return CLIResult(success=True, message="makemigrations completed")
        except Exception as e:
            Output.error(f"makemigrations failed: {e}")
            return CLIResult(success=False, message=str(e), exit_code=1)

    elif args.db_cmd == "migrate":
        try:
            mig_dir = Path("migrations")
            plan_file = mig_dir / "plan.initial.json"
            snapshot_file = mig_dir / "schema.json"
            if not plan_file.exists() or not snapshot_file.exists():
                Output.error("No migration plan found. Run 'mf db makemigrations' first.")
                return CLIResult(success=False, message="Missing plan", exit_code=1)

            ops = json.loads(plan_file.read_text())
            graph = json.loads(snapshot_file.read_text())

            # Read config
            config_yaml = mig_dir / "config.yaml"
            driver = "sqlite"
            dsn = "app.db"
            try:
                if config_yaml.exists():
                    text = config_yaml.read_text()
                    # very small parse: look for 'driver:' and 'dsn:' lines
                    for ln in text.splitlines():
                        if ln.strip().startswith("driver:"):
                            val = (ln.split(":", 1)[1].strip() or driver)
                            if val.lower() not in ("null", "none", "",):
                                driver = val
                        if ln.strip().startswith("dsn:"):
                            val = (ln.split(":", 1)[1].strip() or dsn)
                            if val.lower() not in ("null", "none", "",):
                                dsn = val
            except Exception:
                pass

            if driver == "sqlite":
                apply_sqlite(dsn, ops.get("ops", []), graph)
                Output.success(f"Applied migrations to sqlite://{dsn}")
                return CLIResult(success=True, message="migrate completed")
            else:
                Output.warning(f"Driver '{driver}' not yet supported for migration")
                return CLIResult(success=False, message="Driver not supported", exit_code=1)
        except Exception as e:
            Output.error(f"migrate failed: {e}")
            return CLIResult(success=False, message=str(e), exit_code=1)

    return CLIResult(success=False, message="Unknown db command", exit_code=1)
