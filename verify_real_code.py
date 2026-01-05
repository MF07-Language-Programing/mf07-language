from src.corplang.compiler.lexer import Lexer
from src.corplang.compiler.parser import Parser
import sys
import os


def check_parents(node):
    for attr in dir(node):
        if attr.startswith('_'): continue
        val = getattr(node, attr)
        parent = getattr(val, 'parent', None)
        if parent != node:
            continue
        if isinstance(val, list):
            for item in val:
                if hasattr(item, 'parent'):
                    if item.parent != node:
                        print(f"Mismatch parent in list {attr} of {type(node).__name__}")
                    check_parents(item)
        elif hasattr(val, 'parent'):
            if val.parent != node:
                print(f"Mismatch parent in {attr} of {type(node).__name__}")
            check_parents(val)

def test_file(file_path):
    print(f"Testing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source_file=file_path)
        program = parser.parse()
        check_parents(program)
        
        print(f"  SUCCESS! Nodes: {len(program.statements)}")
        return True
    except Exception as e:
        print(f"  FAILED: {str(e)}")
        # import traceback
        # traceback.print_exc()
        return False

# Files to test from stdlib and examples
files_to_test = [
    "src/corplang/stdlib/core/collections/algorithms.mp",
    "src/corplang/stdlib/core/system/env.mp",
    "examples/agents/agent_security_example.mp",
    "examples/agents/console_loop.mp"
]

all_passed = True
for f in files_to_test:
    if not test_file(f):
        all_passed = False

if all_passed:
    print("\nAll targeted files compiled successfully!")
else:
    print("\nSome files failed to compile.")
    sys.exit(1)
