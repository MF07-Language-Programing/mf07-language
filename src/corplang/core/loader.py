import json
import os
import pickle
import hashlib
import yaml
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Any

from src.corplang.tools.logger import get_logger
from src.corplang.core.module_registry import ModuleRegistry
from src.corplang.core.module_dependency_graph import ModuleDependencyGraph
from src.corplang.executor import parse_file
from src.corplang.compiler.nodes import (
    FunctionDeclaration,
    ClassDeclaration,
    VarDeclaration,
    ImportDeclaration,
    FromImportDeclaration,
)
from src.corplang.tools.diagnostics import safe_message


logger = get_logger(__name__)


def extract_exports_requires(module_path: str, module_name: Optional[str] = None):
    try:
        ast = parse_file(module_path)
        exports = set()
        requires = set()
        if not ast or not hasattr(ast, "statements"):
            if module_name:
                exports.add(module_name)
            return exports, requires
        for stmt in getattr(ast, "statements", []):
            if isinstance(stmt, FunctionDeclaration):
                exports.add(stmt.name)
            elif isinstance(stmt, ClassDeclaration):
                exports.add(stmt.name)
            elif isinstance(stmt, VarDeclaration):
                exports.add(stmt.name)
            elif isinstance(stmt, ImportDeclaration):
                requires.add(stmt.module)
            elif isinstance(stmt, FromImportDeclaration):
                requires.add(stmt.module)
                for sym in getattr(stmt, "names", []):
                    requires.add(f"{stmt.module}.{sym}")
        if module_name:
            exports.add(module_name)
        return exports, requires
    except Exception:
        return ({module_name} if module_name else set(), set())


@dataclass
class CoreModuleSpec:
    name: str
    path: Optional[str] = None
    security: Optional[str] = None


@dataclass
class CoreLoadSummary:
    core_dir: str
    manifest_path: str
    modules: List[str] = field(default_factory=list)
    loaded: List[str] = field(default_factory=list)
    failed: Dict[str, str] = field(default_factory=dict)
    restricted: List[str] = field(default_factory=list)
    manifest_errors: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "core_dir": self.core_dir,
            "manifest_path": self.manifest_path,
            "modules": list(self.modules),
            "loaded": list(self.loaded),
            "failed": dict(self.failed),
            "restricted": list(self.restricted),
            "manifest_errors": list(self.manifest_errors),
        }


_loaded_registry: Dict[str, List[str]] = {}
_default_module_registry = ModuleRegistry()
_default_dependency_graph = ModuleDependencyGraph()


def _get_cache_dir(core_dir: str) -> str:
    cache_dir = os.path.join(core_dir, ".corplang-cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _get_cache_path(core_dir: str, module_name: str, source_path: str) -> str:
    cache_dir = _get_cache_dir(core_dir)
    hash_input = f"{module_name}:{source_path}".encode("utf-8")
    module_hash = hashlib.md5(hash_input).hexdigest()[:12]
    return os.path.join(cache_dir, f"{module_hash}.ast.pkl")


def _is_cache_valid(cache_path: str, source_path: str) -> bool:
    if not os.path.isfile(cache_path):
        return False
    try:
        return os.path.getmtime(cache_path) >= os.path.getmtime(source_path)
    except Exception:
        return False


def _load_cached_ast(cache_path: str) -> Optional[Any]:
    try:
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    except Exception as exc:
        logger.warn(f"Failed to load cached AST: {safe_message(exc)}")
        return None


def _save_cached_ast(cache_path: str, ast_node: Any) -> bool:
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump(ast_node, f, protocol=pickle.HIGHEST_PROTOCOL)
        return True
    except Exception as exc:
        logger.warn(f"Failed to cache AST: {safe_message(exc)}")
        return False


def _normalize_manifest_entry(entry: object, index: int) -> Optional[CoreModuleSpec]:
    if isinstance(entry, str):
        name = entry.strip()
        if not name:
            logger.warn(f"Skipping empty module name in manifest at index {index}")
            return None
        return CoreModuleSpec(name=name)
    if isinstance(entry, dict):
        name = str(entry.get("name") or entry.get("module") or "").strip()
        path = entry.get("path") or entry.get("file")
        security = entry.get("security") or entry.get("policy")
        if not name:
            logger.warn(f"Skipping manifest entry without name at index {index}")
            return None
        normalized_path = str(path).strip() if path else None
        normalized_security = str(security).strip() if security else None
        return CoreModuleSpec(name=name, path=normalized_path, security=normalized_security)
    logger.warn(f"Skipping invalid manifest entry at index {index}: {type(entry).__name__}")
    return None


def load_core_manifest(core_dir: str) -> Tuple[str, List[CoreModuleSpec], List[str]]:
    manifest_path = os.path.abspath(os.path.join(core_dir, "manifest.json"))
    issues: List[str] = []
    specs: List[CoreModuleSpec] = []

    if not os.path.isfile(manifest_path):
        issues.append("manifest_missing")
        logger.warn(f"Core manifest not found: {manifest_path}")
        return manifest_path, specs, issues

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        issues.append(f"manifest_read_error:{safe_message(exc)}")
        logger.error(f"Failed to read core manifest {manifest_path}: {safe_message(exc)}")
        return manifest_path, specs, issues

    modules = data.get("modules") if isinstance(data, dict) else data
    if isinstance(modules, (str, bytes)) or not isinstance(modules, Iterable):
        issues.append("manifest_modules_invalid")
        logger.error(f"Core manifest is missing a modules list: {manifest_path}")
        return manifest_path, specs, issues

    for idx, entry in enumerate(modules):
        spec = _normalize_manifest_entry(entry, idx)
        if spec:
            specs.append(spec)

    return manifest_path, specs, issues


def load_core_modules_from_manifest(
    *,
    core_dir: str,
    import_resolver: Callable[[str, str], Optional[str]],
    module_loader: Callable[[str, str], None],
    current_dir: Optional[str] = None,
    fail_fast: bool = False,
    module_registry: Optional[ModuleRegistry] = None,
    use_cache: bool = True,
    dependency_graph: Optional[ModuleDependencyGraph] = None,
) -> CoreLoadSummary:

    manifest_path, specs, issues = load_core_manifest(core_dir)
    summary = CoreLoadSummary(
        core_dir=os.path.abspath(core_dir),
        manifest_path=manifest_path,
        modules=[spec.name for spec in specs],
        manifest_errors=list(issues),
    )

    work_dir = current_dir or core_dir

    registry = module_registry or _default_module_registry
    dep_graph = dependency_graph or _default_dependency_graph
    for spec in specs:
        module_path: Optional[str] = None
        try:
            if spec.security == "restricted":
                summary.restricted.append(spec.name)
                logger.warn(f"Skipping restricted core module: {spec.name}")
                continue
            if spec.path:
                candidate = os.path.abspath(os.path.join(core_dir, spec.path))
                module_path = candidate if os.path.isfile(candidate) else None
            if module_path is None:
                module_path = import_resolver(spec.name, work_dir)
            if not module_path or not os.path.isfile(module_path):
                summary.failed[spec.name] = "module_not_found"
                logger.error(
                    f"Core module missing: {spec.name} path={module_path or spec.path or '<unresolved>'}"
                )
                if fail_fast:
                    raise FileNotFoundError(spec.name)
                continue

            # Avoid duplicate loads: if module already loaded by name or path, skip executing again
            if registry.is_loaded_by_name(spec.name) or registry.is_loaded_by_path(module_path):
                continue
            # Execute loader to populate exports
            module_loader(spec.name, module_path)
            summary.loaded.append(spec.name)
            try:
                registry.register(spec.name, module_path, exports=None)
            except Exception:
                pass
        except Exception as exc:
            import traceback
            traceback.print_exc()
            summary.failed[spec.name] = safe_message(exc)
            logger.error(
                f"Core module load failed: {spec.name} path={module_path or spec.path or '<unresolved>'} error={safe_message(exc)}"
            )
            if fail_fast:
                raise

    _loaded_registry.clear()
    _loaded_registry.update({"core": list(summary.loaded)})
    return summary


def load_agents_from_config(project_root: str) -> List[Dict[str, Any]]:
    """Load agent configuration from language_config.yaml and eco.system.json."""
    agents: List[Dict[str, Any]] = []
    lc_path = os.path.join(project_root, "language_config.yaml")
    eco_path = os.path.join(project_root, "eco.system.json")
    data = {}
    if os.path.isfile(lc_path):
        try:
            with open(lc_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            logger.warn(f"language_config.yaml parsing failed: {lc_path}")
    elif os.path.isfile(eco_path):
        try:
            with open(eco_path, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            logger.warn(f"eco.system.json parsing failed: {eco_path}")

    agents_conf = data.get("agents") if isinstance(data, dict) else None
    if agents_conf and isinstance(agents_conf, dict):
        for name, cfg in agents_conf.items():
            agents.append({"name": name, "config": cfg})
    return agents


def load_core_modules_from_manifest_cached(
    *,
    core_dir: str,
    import_resolver: Callable[[str, str], Optional[str]],
    module_parser: Callable[[str], Any],
    module_executor: Callable[[str, Any], None],
    current_dir: Optional[str] = None,
    fail_fast: bool = False,
    module_registry: Optional[ModuleRegistry] = None,
) -> CoreLoadSummary:

    manifest_path, specs, issues = load_core_manifest(core_dir)
    summary = CoreLoadSummary(
        core_dir=os.path.abspath(core_dir),
        manifest_path=manifest_path,
        modules=[spec.name for spec in specs],
        manifest_errors=list(issues),
    )

    work_dir = current_dir or core_dir
    cache_stats = {"hits": 0, "misses": 0, "saved": 0}

    registry = module_registry or _default_module_registry
    for spec in specs:
        module_path: Optional[str] = None
        try:
            if spec.security == "restricted":
                summary.restricted.append(spec.name)
                logger.warn(f"Skipping restricted core module: {spec.name}")
                continue

            if spec.path:
                candidate = os.path.abspath(os.path.join(core_dir, spec.path))
                module_path = candidate if os.path.isfile(candidate) else None
            if module_path is None:
                module_path = import_resolver(spec.name, work_dir)
            if not module_path or not os.path.isfile(module_path):
                summary.failed[spec.name] = "module_not_found"
                logger.error(f"Core module missing: {spec.name} path={module_path or spec.path}")
                if fail_fast:
                    raise FileNotFoundError(spec.name)
                continue

            if registry.is_loaded_by_name(spec.name) or registry.is_loaded_by_path(module_path):
                logger.info(f"Skipping already-loaded module: {spec.name}")
                continue

            cache_path = _get_cache_path(core_dir, spec.name, module_path)
            ast_node = None

            if _is_cache_valid(cache_path, module_path):
                ast_node = _load_cached_ast(cache_path)
                if ast_node is not None:
                    cache_stats["hits"] += 1
                    logger.info(f"Cache hit: {spec.name}")

            if ast_node is None:
                cache_stats["misses"] += 1
                ast_node = module_parser(module_path)
                if ast_node is not None:
                    if _save_cached_ast(cache_path, ast_node):
                        cache_stats["saved"] += 1
                        logger.info(f"Cached: {spec.name}")

            if ast_node is not None:
                module_executor(spec.name, ast_node)
                summary.loaded.append(spec.name)
                try:
                    registry.register(spec.name, module_path, exports=None)
                except Exception:
                    pass
            else:
                summary.failed[spec.name] = "parse_failed"
                logger.error(f"Failed to parse module: {spec.name}")

        except Exception as exc:
            summary.failed[spec.name] = safe_message(exc)
            logger.error(f"Core module load failed: {spec.name} error={safe_message(exc)}")
            if fail_fast:
                raise

    _loaded_registry.clear()
    _loaded_registry.update({"core": list(summary.loaded)})

    if cache_stats["hits"] > 0:
        cache_dir_path = _get_cache_dir(core_dir)
        logger.warn(
            f"USING COMPILED MODULE CACHE: {cache_stats['hits']} modules from {cache_dir_path}"
        )

    logger.info(
        f"Core cache stats: {cache_stats['hits']} hits, {cache_stats['misses']} misses, {cache_stats['saved']} saved"
    )
    return summary


def get_loaded_modules() -> Dict[str, List[str]]:
    try:
        return deepcopy(_loaded_registry)
    except Exception:
        return {}


def get_default_module_registry() -> ModuleRegistry:
    return _default_module_registry


def clear_module_cache(core_dir: str) -> int:
    cache_dir = os.path.join(core_dir, ".corplang-cache")
    deleted = 0

    if not os.path.isdir(cache_dir):
        return 0

    try:
        for filename in os.listdir(cache_dir):
            if filename.endswith(".ast.pkl"):
                file_path = os.path.join(cache_dir, filename)
                try:
                    os.remove(file_path)
                    deleted += 1
                except Exception as exc:
                    logger.warn(f"Failed to delete cache file: {safe_message(exc)}")
        logger.info(f"Cache cleared: {deleted} files deleted from {cache_dir}")
    except Exception as exc:
        logger.error(f"Failed to clear cache: {safe_message(exc)}")

    return deleted
