#!/usr/bin/env python3
"""
CLI Test Suite - Verifies all Corplang CLI commands
"""

import subprocess
import sys
from pathlib import Path

def run_test(name: str, cmd: list, expected_success: bool = True) -> bool:
    """Run a single CLI test."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"CMD:  {' '.join(cmd)}")
    print(f"{'-'*60}")

    try:
        result = subprocess.run(
            cmd,
            cwd="/home/bugson/PycharmProjects/mf07-language",
            capture_output=True,
            text=True,
            timeout=10,
        )

        success = (result.returncode == 0) == expected_success
        status = "✓ PASS" if success else "✗ FAIL"

        print(f"{status}")
        if result.stdout:
            lines = result.stdout.split("\n")[:5]
            for line in lines:
                print(f"  {line}")
        if result.stderr and result.returncode != 0:
            print(f"  Error: {result.stderr[:100]}")

        return success

    except subprocess.TimeoutExpired:
        print("✗ FAIL (timeout)")
        return False
    except Exception as e:
        print(f"✗ FAIL ({e})")
        return False


def main():
    """Run all tests."""
    tests = [
        ("Help", ["python", "-m", "src.commands", "--help"]),
        ("Version", ["python", "-m", "src.commands", "version"]),
        ("Version Verbose", ["python", "-m", "src.commands", "version", "--verbose"]),
        ("Versions List", ["python", "-m", "src.commands", "versions", "list"]),
        ("Versions List Detailed", ["python", "-m", "src.commands", "versions", "list", "--detailed"]),
        ("Env Validate", ["python", "-m", "src.commands", "env", "validate"]),
        ("Env Config Show", ["python", "-m", "src.commands", "env", "config", "show"]),
        ("Compile File", ["python", "-m", "src.commands", "compile", "examples/first_project/main.mp"]),
        ("Compile Directory", ["python", "-m", "src.commands", "compile", "--dir", "examples/new_main"]),
        ("Run Program", ["python", "-m", "src.commands", "run", "examples/new_main/type_demo.mp"]),
        ("Init Project", ["python", "-m", "src.commands", "init", "test_proj"]),
        ("Build", ["python", "-m", "src.commands", "build"]),
        ("DB Init", ["python", "-m", "src.commands", "db", "init", "/tmp/mf-db-test"]),
        ("Docs Generate", ["python", "-m", "src.commands", "docs", "examples/new_main", "--output", "/tmp/mf-docs"]),
    ]

    print("\n" + "="*60)
    print("CORPLANG CLI TEST SUITE")
    print("="*60)

    passed = 0
    failed = 0

    for name, cmd in tests:
        if run_test(name, cmd):
            passed += 1
        else:
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
