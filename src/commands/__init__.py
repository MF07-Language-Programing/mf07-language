"""
Corplang CLI Commands Module

This module provides the command-line interface for the Corplang language,
including compilation, execution, project initialization, and version management.

Usage:
    from src.commands.main import main
    main()

Or directly from terminal:
    python -m src.commands main run program.mp
    python -m src.commands main compile --dir ./src
    python -m src.commands main init myproject
"""

from src.commands.main import main

__version__ = "0.1.0"
__all__ = ["main"]
