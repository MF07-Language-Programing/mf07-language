"""Test distribution path resolution fixes."""
import os
import sys
from pathlib import Path


def test_path_resolver_absolute():
    """PathResolver should handle absolute paths correctly."""
    from src.commands.utils.utils import PathResolver
    
    test_file = "/tmp/test.mp"
    resolved = PathResolver.resolve_relative_path(test_file)
    
    assert resolved.is_absolute()
    assert str(resolved) == str(Path(test_file).resolve())
    print("✓ test_path_resolver_absolute passed")


def test_path_resolver_relative_with_base():
    """PathResolver should resolve relative paths using base_dir."""
    from src.commands.utils.utils import PathResolver
    
    base = Path("/home/user/project")
    file_path = "subdir/main.mp"
    
    resolved = PathResolver.resolve_relative_path(file_path, base)
    
    assert resolved.is_absolute()
    assert resolved == (base / file_path).resolve()
    print("✓ test_path_resolver_relative_with_base passed")


def test_path_resolver_relative_without_base():
    """PathResolver should use cwd when base_dir is None."""
    from src.commands.utils.utils import PathResolver
    
    file_path = "main.mp"
    resolved = PathResolver.resolve_relative_path(file_path)
    
    expected = (Path.cwd() / file_path).resolve()
    assert resolved == expected
    print("✓ test_path_resolver_relative_without_base passed")


def test_stdlib_roots_includes_installed():
    """_stdlib_roots should include installed package location."""
    from src.corplang.executor.interpreter import _stdlib_roots
    
    roots = _stdlib_roots()
    
    assert len(roots) > 0
    assert all(isinstance(r, Path) for r in roots)
    assert all(r.exists() for r in roots)
    print(f"✓ test_stdlib_roots_includes_installed passed ({len(roots)} roots found)")


def test_find_installed_stdlib():
    """_find_installed_stdlib should find stdlib relative to interpreter.py."""
    from src.corplang.executor.interpreter import _find_installed_stdlib
    
    stdlib = _find_installed_stdlib()
    
    # In dev environment, should find src/corplang/stdlib
    assert stdlib is not None
    assert stdlib.exists()
    assert stdlib.is_dir()
    assert (stdlib / "core").exists()
    print(f"✓ test_find_installed_stdlib passed (found: {stdlib})")


def test_stdlib_manifest_loads():
    """Stdlib manifest should load successfully."""
    from src.corplang.executor.interpreter import _load_stdlib_manifest
    
    fallback_root, manifest = _load_stdlib_manifest()
    
    assert fallback_root is not None, "fallback_root is None"
    assert manifest is not None, "manifest is None"
    assert len(manifest) > 0, "manifest is empty"
    assert any("collections" in key for key in manifest.keys()), "No collections modules found"
    print(f"✓ test_stdlib_manifest_loads passed ({len(manifest)} modules)")


if __name__ == "__main__":
    print("Running distribution fixes tests...\n")
    try:
        test_path_resolver_absolute()
        test_path_resolver_relative_with_base()
        test_path_resolver_relative_without_base()
        test_stdlib_roots_includes_installed()
        test_find_installed_stdlib()
        test_stdlib_manifest_loads()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

