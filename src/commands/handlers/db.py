from pathlib import Path
import json
import shutil
from src.commands.utils.utils import Output, CLIResult
from src.commands.config import CorplangConfig
from src.corplang.executor.db.model_parser import parse_models
from src.corplang.executor.db.schema_graph import build_graph, compute_initial_plan, compute_incremental_plan
from src.corplang.executor.db.migrations import write_snapshot, apply_migrations, drop_schema

def init_migrations(path: str = "migrations") -> CLIResult:
    """Initialize migrations directory."""
    mig_path = Path(path)
    mig_path.mkdir(exist_ok=True, parents=True)

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
        
        elif driver in ("postgresql", "postgres"):
            try:
                import psycopg
                conn = psycopg.connect(dsn)
            except ImportError:
                import psycopg2
                conn = psycopg2.connect(dsn)
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
            candidates = [
                Path("examples/orm_demo/models.mp"),
                Path("examples/onr_demo/models.mp"),
                Path("models.mp"),
            ]
            src_file = next((p for p in candidates if p.exists()), None)
            if not src_file:
                Output.error("No models file found (expected examples/orm_demo/models.mp or ./models.mp)")
                return CLIResult(success=False, message="No models file", exit_code=1)

            source = src_file.read_text(encoding="utf-8")
            schema = parse_models(source)
            
            from src.commands.utils.tree_renderer import render_models_tree
            models_info = {str(src_file): schema}
            tree_output = render_models_tree(models_info)
            Output.info("\n" + tree_output)
            
            graph = build_graph(schema)
            
            mig_dir = Path("migrations")
            mig_dir.mkdir(exist_ok=True)
            
            prev_snapshot = mig_dir / "schema.json"
            if prev_snapshot.exists():
                prev_graph = json.loads(prev_snapshot.read_text())
                ops = compute_incremental_plan(prev_graph, graph)
                Output.info("Detecting changes in existing models...")
            else:
                ops = compute_initial_plan(graph)
                Output.info("Creating initial migration plan...")
            
            write_snapshot(mig_dir / "schema.json", graph)
            
            if ops and len(ops) > 0:
                from src.corplang.executor.db.migrations import write_migration
                mig_file = write_migration(mig_dir, ops)
                
                from src.commands.utils.tree_renderer import render_migration_operations
                tree_output = render_migration_operations(ops)
                Output.info("\n" + tree_output)
                
                Output.success(f"Migrations generated: {mig_file.relative_to('.')}")
            else:
                Output.info("No changes detected.")
            
            return CLIResult(success=True, message="makemigrations completed")
        except Exception as e:
            Output.error(f"makemigrations failed: {e}")
            import traceback
            traceback.print_exc()
            return CLIResult(success=False, message=str(e), exit_code=1)

    elif args.db_cmd == "migrate":
        try:
            project_root = CorplangConfig.get_project_root()
            if not project_root:
                Output.error("Not in a Corplang project. Need language_config.yaml or manifest.json")
                return CLIResult(success=False, message="No project root", exit_code=1)

            mig_dir = Path("migrations")
            
            if not mig_dir.exists():
                Output.error("No migrations directory. Run 'mf db makemigrations' first.")
                return CLIResult(success=False, message="Missing migrations", exit_code=1)
            
            snapshot_file = mig_dir / "schema.json"
            if not snapshot_file.exists():
                Output.error("No schema snapshot found. Run 'mf db makemigrations' first.")
                return CLIResult(success=False, message="Missing snapshot", exit_code=1)

            graph = json.loads(snapshot_file.read_text())
            driver, dsn = CorplangConfig.load_database_config(project_root)

            Output.info(f"Using database: {driver}://{dsn}")

            applied = apply_migrations(driver, dsn, mig_dir, graph)
            
            if applied:
                Output.success(f"Applied {len(applied)} migration(s):")
                for mig in applied:
                    Output.info(f"  ✓ {mig}")
                return CLIResult(success=True, message="migrate completed")
            else:
                Output.info("No unapplied migrations.")
                return CLIResult(success=True, message="migrate completed")
        except Exception as e:
            Output.error(f"migrate failed: {e}")
            return CLIResult(success=False, message=str(e), exit_code=1)

    elif args.db_cmd == "reset":
        mig_dir = Path("migrations")
        drop_db = getattr(args, "drop_db", False)

        if drop_db:
            project_root = CorplangConfig.get_project_root()
            if not project_root:
                Output.error("Not in a Corplang project. Need language_config.yaml or manifest.json")
                return CLIResult(success=False, message="No project root", exit_code=1)

            snapshot_file = mig_dir / "schema.json"
            if not snapshot_file.exists():
                Output.warning("No schema snapshot found; skipping database drop")
            else:
                try:
                    graph = json.loads(snapshot_file.read_text())
                    driver, dsn = CorplangConfig.load_database_config(project_root)
                    drop_schema(driver, dsn, graph)
                    Output.success(f"Dropped database objects for {driver}://{dsn}")
                except Exception as e:
                    Output.error(f"Failed to drop database objects: {e}")
                    return CLIResult(success=False, message=str(e), exit_code=1)

        if mig_dir.exists():
            shutil.rmtree(mig_dir)
            Output.success("Migrations directory removed")
        else:
            Output.info("No migrations directory to remove")

        return CLIResult(success=True, message="reset completed")

    return CLIResult(success=False, message="Unknown db command", exit_code=1)

