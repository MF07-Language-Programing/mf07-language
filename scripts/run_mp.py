from pathlib import Path
import logging
import asyncio
from src.corplang.compiler import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.executor import execute

# Silence verbose asyncio internal debug logs (selector reports etc.)
logging.getLogger("asyncio").setLevel(logging.WARNING)
try:
    # Prefer to use get_running_loop to avoid creating or fetching a loop when none exists
    loop = asyncio.get_running_loop()
    loop.set_debug(False)
except RuntimeError:
    # No running loop — create a temporary loop, set debug flag, then close it (no side-effects)
    try:
        tmp = asyncio.new_event_loop()
        tmp.set_debug(False)
        tmp.close()
    except Exception:
        pass
except Exception:
    pass


def run_file(path: str):
    code = Path(path).read_text()
    lexer = Lexer(code)
    parser = Parser(lexer.tokenize(), source_file=path)
    tree = parser.parse()
    execute(tree)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_mp.py <file.mp>")
        sys.exit(1)
    run_file(sys.argv[1])
