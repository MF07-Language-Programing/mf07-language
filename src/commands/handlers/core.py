"""Core modules inspection handler for Corplang CLI."""
import json
from pathlib import Path
from typing import List, Dict, Any

from src.commands.utils.utils import Output, CLIResult
from src.corplang.executor.interpreter import _stdlib_roots, _load_stdlib_manifest


def list_core_modules() -> List[Dict[str, Any]]:
    """List all available core modules with their paths."""
    roots = _stdlib_roots()
    modules = []
    
    for root in roots:
        if not root.exists():
            continue
        
        # Find all .mp files recursively
        mp_files = list(root.rglob("*.mp"))
        
        for mp_file in mp_files:
            # Get relative path from stdlib root
            relative = mp_file.relative_to(root)
            # Convert path to module name (e.g., core/collections/list.mp -> core.collections.list)
            module_name = str(relative.with_suffix('')).replace('/', '.')
            
            modules.append({
                "name": module_name,
                "path": str(mp_file),
                "root": str(root),
                "size": mp_file.stat().st_size,
                "exists": mp_file.exists(),
            })
    
    return modules


def get_stdlib_info() -> Dict[str, Any]:
    """Get stdlib information including roots and manifest."""
    roots = _stdlib_roots()
    fallback_root, manifest = _load_stdlib_manifest()
    
    return {
        "roots": [str(r) for r in roots],
        "active_root": str(fallback_root) if fallback_root else None,
        "manifest_modules": len(manifest) if manifest else 0,
        "manifest_keys": list(manifest.keys()) if manifest else [],
    }


def handle_core(args) -> CLIResult:
    """Handle the core command."""
    
    if args.core_cmd == "list":
        return handle_core_list(args)
    elif args.core_cmd == "info":
        return handle_core_info(args)
    elif args.core_cmd == "search":
        return handle_core_search(args)
    elif args.core_cmd == "manifest":
        return handle_core_manifest(args)
    else:
        # Default: show info
        return handle_core_info(args)


def handle_core_list(args) -> CLIResult:
    """List all core modules."""
    Output.step("Listing core modules...")
    print()
    
    modules = list_core_modules()
    
    if not modules:
        Output.warning("No core modules found")
        return CLIResult(success=False, message="No core modules found", exit_code=1)
    
    # Group by root
    by_root = {}
    for mod in modules:
        root = mod["root"]
        if root not in by_root:
            by_root[root] = []
        by_root[root].append(mod)
    
    # Display by root
    for root, mods in by_root.items():
        Output.info(f"Root: {root}")
        print(f"  Modules: {len(mods)}")
        
        if args.verbose:
            for mod in sorted(mods, key=lambda m: m["name"]):
                size_kb = mod["size"] / 1024
                print(f"    • {mod['name']} ({size_kb:.1f} KB)")
        else:
            # Show first 10
            for mod in sorted(mods, key=lambda m: m["name"])[:10]:
                print(f"    • {mod['name']}")
            if len(mods) > 10:
                print(f"    ... and {len(mods) - 10} more (use --verbose to see all)")
        print()
    
    Output.success(f"Found {len(modules)} core modules")
    return CLIResult(success=True, message=f"Found {len(modules)} modules", exit_code=0)


def handle_core_info(args) -> CLIResult:
    """Show stdlib information."""
    Output.step("Core modules information")
    print()
    
    info = get_stdlib_info()
    
    Output.info("Stdlib Roots (priority order):")
    for i, root in enumerate(info["roots"], 1):
        marker = "✓" if Path(root).exists() else "✗"
        print(f"  {i}. {marker} {root}")
    print()
    
    if info["active_root"]:
        Output.info(f"Active Root: {info['active_root']}")
    else:
        Output.warning("No active root found")
    print()
    
    Output.info(f"Manifest Modules: {info['manifest_modules']}")
    
    if args.verbose and info["manifest_keys"]:
        print("\nManifest Keys (first 20):")
        for key in sorted(info["manifest_keys"])[:20]:
            print(f"  • {key}")
        if len(info["manifest_keys"]) > 20:
            print(f"  ... and {len(info['manifest_keys']) - 20} more")
    print()
    
    # Count actual .mp files
    modules = list_core_modules()
    Output.info(f"Total .mp Files: {len(modules)}")
    
    return CLIResult(success=True, message="Core info retrieved", exit_code=0)


def handle_core_search(args) -> CLIResult:
    """Search for core modules."""
    if not args.query:
        return CLIResult(success=False, message="No search query provided", exit_code=1)
    
    query = args.query.lower()
    Output.step(f"Searching for: {query}")
    print()
    
    modules = list_core_modules()
    matches = [m for m in modules if query in m["name"].lower()]
    
    if not matches:
        Output.warning(f"No modules found matching '{query}'")
        return CLIResult(success=False, message="No matches found", exit_code=1)
    
    Output.info(f"Found {len(matches)} matching module(s):")
    print()
    
    for mod in sorted(matches, key=lambda m: m["name"]):
        print(f"  • {mod['name']}")
        if args.verbose:
            print(f"    Path: {mod['path']}")
            print(f"    Size: {mod['size'] / 1024:.1f} KB")
        print()
    
    Output.success(f"Found {len(matches)} matches")
    return CLIResult(success=True, message=f"Found {len(matches)} matches", exit_code=0)


def handle_core_manifest(args) -> CLIResult:
    """Show manifest contents."""
    Output.step("Loading stdlib manifest...")
    print()
    
    fallback_root, manifest = _load_stdlib_manifest()
    
    if not manifest:
        Output.error("Manifest not found or empty")
        return CLIResult(success=False, message="Manifest not found", exit_code=1)
    
    Output.info(f"Manifest Root: {fallback_root}")
    Output.info(f"Total Entries: {len(manifest)}")
    print()
    
    if args.json:
        # Output as JSON
        print(json.dumps(manifest, indent=2))
    else:
        # Group by namespace
        namespaces = {}
        for key in manifest.keys():
            parts = key.split('.')
            if len(parts) >= 2:
                ns = f"{parts[0]}.{parts[1]}"
            else:
                ns = parts[0]
            
            if ns not in namespaces:
                namespaces[ns] = []
            namespaces[ns].append(key)
        
        for ns, keys in sorted(namespaces.items()):
            Output.info(f"{ns} ({len(keys)} modules)")
            if args.verbose:
                for key in sorted(keys):
                    print(f"  • {key}")
            else:
                for key in sorted(keys)[:5]:
                    print(f"  • {key}")
                if len(keys) > 5:
                    print(f"  ... and {len(keys) - 5} more")
            print()
    
    return CLIResult(success=True, message="Manifest loaded", exit_code=0)
