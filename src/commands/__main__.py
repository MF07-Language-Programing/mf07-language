#!/usr/bin/env python3
"""
Corplang Language CLI Entry Point

This module makes the CLI executable via: python -m src.commands
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from src.commands.main import main

if __name__ == "__main__":
    main()
