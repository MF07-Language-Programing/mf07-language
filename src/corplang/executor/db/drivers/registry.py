"""Driver registry and factory."""
from typing import Dict, Type, Any
from .base import MigrationDriver
from .sqlite import SQLiteDriver
from .postgresql import PostgreSQLDriver


# Registry of available drivers
DRIVERS: Dict[str, Type[MigrationDriver]] = {
    "sqlite": SQLiteDriver,
    "postgresql": PostgreSQLDriver,
    "postgres": PostgreSQLDriver,  # alias
}


def get_driver(driver_name: str) -> Type[MigrationDriver]:
    """Get migration driver by name."""
    driver_name_lower = driver_name.lower()
    
    if driver_name_lower not in DRIVERS:
        raise ValueError(
            f"Unsupported database driver: {driver_name}\n"
            f"Available: {', '.join(DRIVERS.keys())}"
        )
    
    return DRIVERS[driver_name_lower]
