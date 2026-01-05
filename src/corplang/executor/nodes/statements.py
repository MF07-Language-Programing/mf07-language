"""Statement-level node executors.

Provides executors for program structure, imports, agents and server statements.
Trace hooks were removed for simplicity; observability should be handled centrally.
"""

from __future__ import annotations

from typing import Any

from src.corplang.executor.node import NodeExecutor
from src.corplang.executor.context import ExecutionContext
from src.corplang.executor.helpers import get_node_attr, resolve_node_value, type_check
from src.corplang.executor.interpreter import ExecutorRegistry
from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType, ReturnException
from src.corplang.executor.objects import InstanceObject, ClassObject


class ProgramExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "Program"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        result = None
        statements = get_node_attr(node, "statements", "body", default=[]) or []
        with context.frame(
            context.current_file, getattr(node, "line", None) or 1, "<module>", node=node
        ):
            for stmt in statements:
                result = context.interpreter.execute(stmt, context)
        return result


class ModelDeclNoOpExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ in ("ModelDeclaration", "MigrationDeclaration")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Model/migration declarations are compile-time only in this scaffold.
        return None


class ModelOperationNoOpExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ModelOperation"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Model operations are DSL constructs not executed in this runtime
        return None


class DatasetOperationNoOpExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "DatasetOperation"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Dataset operations are DSL constructs not executed in this runtime
        return None


class AgentDefinitionExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AgentDefinition"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.agent_runtime import get_agent_manager

        mgr = get_agent_manager()
        mgr.create_agent(node)
        return None


class AgentTrainExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AgentTrain"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.agent_runtime import get_agent_manager
        import threading

        mgr = get_agent_manager()

        def _t():
            # Best-effort background training (non-blocking)
            try:
                import asyncio

                res = asyncio.run(mgr.train_agent(node))
                try:
                    context.interpreter._builtin_print(
                        f"agent train completed: {{'agent': '{node.agent_name}', 'ok': {res}}}"
                    )
                except Exception:
                    pass
            except Exception:
                try:
                    # fallback to sync
                    import asyncio as _a

                    _a.run(mgr.train_agent(node))
                    try:
                        context.interpreter._builtin_print(
                            f"agent train completed: {{'agent': '{node.agent_name}', 'ok': True}}"
                        )
                    except Exception:
                        pass
                except Exception:
                    pass

        threading.Thread(target=_t, daemon=True).start()
        return None


class AgentEmbedExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AgentEmbed"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.agent_runtime import get_agent_manager

        mgr = get_agent_manager()
        raw_agent = getattr(node, "agent_name", None)
        agent_name = (
            raw_agent
            if isinstance(raw_agent, str)
            else getattr(raw_agent, "name", None) or getattr(raw_agent, "value", None)
        )
        items = getattr(node, "items", None) or []
        res = mgr.embed_agent(agent_name, items)
        context.interpreter._builtin_print(f"embed result: {res}")
        return res


class AgentPredictExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AgentPredict"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.agent_runtime import get_agent_manager

        mgr = get_agent_manager()
        agent_name = getattr(node, "agent_name", None)
        raw_agent = getattr(node, "agent_name", None)
        # Normalize name without resolving Identifier nodes (avoid trying to evaluate user vars)
        agent_name = (
            raw_agent
            if isinstance(raw_agent, str)
            else getattr(raw_agent, "name", None) or getattr(raw_agent, "value", None)
        )
        # Normalized agent_name computed above; avoid printing debug traces here
        input_data = getattr(node, "input_data", None)
        res = mgr.predict_agent(agent_name, input_data)
        context.interpreter._builtin_print(f"predict result: {res}")
        return res


class AgentShutdownExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AgentShutdown"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.agent_runtime import get_agent_manager

        mgr = get_agent_manager()
        agent_name = getattr(node, "agent_name", None)
        # shutdown via DSL is local and needs to respect ACLs; we don't have token here,
        # so require agent context to allow shutdown without token (or design auth separately)
        # For now, attempt shutdown with no token; agent ACL can leave allow_tokens empty to permit this.
        ok = mgr.shutdown_agent(agent_name, auth_token=None)
        context.interpreter._builtin_print(f"shutdown {agent_name}: {ok}")
        return ok


class AgentRunExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AgentRun"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.agent_runtime import get_agent_manager

        mgr = get_agent_manager()
        return mgr.run_agent(node)


class LoopExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "LoopStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Lazy imports to avoid cycles
        from src.corplang.runtime.interaction import StdinAdapter, choose_target_agent
        from src.corplang.runtime.agent_runtime import get_agent_manager

        adapter_name = getattr(node, "adapter", "stdin")
        # agent_names may be a list of agent names or None
        agent_names = getattr(node, "agent_names", None)
        adapter = None
        if adapter_name == "stdin":
            adapter = StdinAdapter()
        else:
            # Fallback to stdin for unknown adapters for now
            adapter = StdinAdapter()

        mgr = get_agent_manager()

        # Simple loop: read lines and dispatch to agent; exit on EOF or 'exit'
        try:
            while True:
                line = adapter.read()
                if line is None:
                    break
                if line.strip().lower() in ("exit", "quit"):
                    adapter.write("Exiting interaction loop.")
                    break
                if not agent_names:
                    adapter.write("No agent specified for loop; use 'loop stdin using <AgentName>'")
                    continue

                target_agent, routed_input = choose_target_agent(agent_names, line)
                if not target_agent:
                    adapter.write("No agent available to handle input.")
                    continue

                resp = mgr.interact(target_agent, routed_input)
                # Write a simple structured output
                if isinstance(resp, dict):
                    # Display structured response clearly
                    prefix = f"[{target_agent}] " if agent_names and len(agent_names) > 1 else ""
                    if "text" in resp and len(resp) == 1:
                        adapter.write(prefix + resp["text"])
                    else:
                        # show text plus metadata
                        txt = resp.get("text", "")
                        meta = {k: v for k, v in resp.items() if k != "text"}
                        adapter.write(prefix + (f"{txt} {meta}" if txt else f"{meta}"))
                else:
                    adapter.write(str(resp))
        finally:
            adapter.close()
        return None


class ServeExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ServeStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.server_manager import get_server_registry

        adapter = getattr(node, "adapter", "http")
        name = getattr(node, "name", None) or f"{adapter}_{getattr(node,'port',0)}"
        host = getattr(node, "host", None) or "127.0.0.1"
        port = getattr(node, "port", 8000)
        agent_names = getattr(node, "agent_names", None)

        registry = get_server_registry()
        if adapter == "http":
            try:
                handle = registry.start_http(name, host, port, agent_names=agent_names)
            except Exception as exc:
                import traceback
                import sys

                # Observability trace removed — emit traceback and re-raise
                traceback.print_exc(file=sys.stderr)
                raise
            # If blocking flag is set, wait until the server stops
            if getattr(node, "blocking", False):
                try:
                    if agent_names:
                        context.interpreter._builtin_print(
                            f"Server '{name}' is running at http://{host}:{port}/ (agents={agent_names})"
                        )
                    else:
                        context.interpreter._builtin_print(
                            f"Server '{name}' is running at http://{host}:{port}/"
                        )
                    context.interpreter._builtin_print(
                        f"Press Ctrl+C to stop, or call `stop {name};` from another .mp, or POST /interact/<agent>/shutdown"
                    )
                    handle.wait()
                except KeyboardInterrupt:
                    # Graceful shutdown on first Ctrl+C
                    context.interpreter._builtin_print(
                        f"Interrupt received: stopping server '{name}'..."
                    )
                    # Observability trace removed
                    try:
                        registry.stop(name)
                    except Exception:
                        pass
                    context.interpreter._builtin_print(f"Server '{name}' stopped.")
                finally:
                    # Ensure we removed server from registry if still present
                    try:
                        registry.stop(name)
                    except Exception:
                        pass
            return handle
        else:
            raise RuntimeError(f"Unknown adapter type: {adapter}")


class StopExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "StopStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.server_manager import get_server_registry

        target = getattr(node, "target", None)
        if not target:
            return None
        registry = get_server_registry()
        context.interpreter._builtin_print(f"Stopping server '{target}'...")
        ok = registry.stop(target)
        if ok:
            context.interpreter._builtin_print(f"Server '{target}' stopped.")
        else:
            context.interpreter._builtin_print(f"Server '{target}' not found.")
        return ok


class AwaitExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AwaitStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.runtime.server_manager import get_server_registry

        target = getattr(node, "target", None)
        if not target:
            return None
        registry = get_server_registry()
        handle = registry.get(target)
        if not handle:
            # nothing to await
            return None
        handle.wait()
        return None


class VarDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "VarDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        value_node = get_node_attr(node, "value", "initializer")
        annotation = getattr(node, "type_annotation", None)

        # Special-case: if initializer is a call to `input(...)` and the caller did not
        # provide an explicit expected type, inject the variable's annotation so input
        # can cast appropriately and support `raise` kwarg for trace control.
        value = None
        if value_node is not None and getattr(value_node, "__class__", None) and getattr(value_node, "__class__", None).__name__ == "FunctionCall":
            callee_node = get_node_attr(value_node, "callee", "func", "name")
            if isinstance(callee_node, str) and callee_node == "input":
                # Build positional and keyword args from the call node
                args_list = get_node_attr(value_node, "args", "arguments", default=[]) or []
                positional = []
                keyword = {}
                for arg in args_list:
                    name = getattr(arg, "name", None)
                    value_n = getattr(arg, "value", arg)
                    if name:
                        keyword[name] = resolve_node_value(value_n, context)
                    else:
                        positional.append(resolve_node_value(value_n, context))

                # If no expected_type provided, use the annotation (string form)
                if "expected_type" not in keyword and len(positional) < 2 and annotation is not None:
                    positional = positional[:1] + [str(annotation)]

                # Call the builtin directly (will handle raise/retry semantics)
                func = context.get_var("input")
                if not callable(func):
                    raise CorpLangRuntimeError("input is not callable", RuntimeErrorType.TYPE_ERROR)
                value = func(*positional, **keyword)

        # Fallback to normal resolution
        if value_node is not None and value is None:
            value = resolve_node_value(value_node, context)

        type_check(value, annotation, context.interpreter.strict_types, CorpLangRuntimeError)
        name = getattr(node, "name", None)
        if not name:
            raise CorpLangRuntimeError("VarDeclaration missing name", RuntimeErrorType.SYNTAX_ERROR)
        context.define_var(name, value, annotation)
        return value


class ModuleNamespace(dict):
    """Dict-like module namespace tagged with corplang type 'module'.

    Behaves like a normal dict for nested namespaces and property access,
    but passes type checks for annotated 'module'.
    """

    __corplang_type__ = "module"


class ImportDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ImportDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        module_name = getattr(node, "module", None)
        if not module_name:
            raise CorpLangRuntimeError(
                "ImportDeclaration missing module name", RuntimeErrorType.SYNTAX_ERROR
            )

        exports = context.interpreter._import_module(module_name, context.current_file)

        parts = module_name.split(".") if isinstance(module_name, str) else [str(module_name)]
        root = parts[0] if parts else module_name
        existing = context.get_var(root) if context.has_var(root) else None
        module_obj = existing if isinstance(existing, ModuleNamespace) else ModuleNamespace()

        current = module_obj
        for part in parts[1:-1]:
            if part not in current or not isinstance(current.get(part), dict):
                current[part] = ModuleNamespace()
            current = current[part]

        final_key = parts[-1] if parts else module_name
        # Leaf also tagged as module for type consistency
        current[final_key] = ModuleNamespace(exports) if isinstance(exports, dict) else exports

        if context.has_var(root):
            context.set_var(root, module_obj)
        else:
            context.define_var(root, module_obj, "module")
        return exports


class FromImportDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "FromImportDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        module_name = getattr(node, "module", None)
        items = getattr(node, "items", None) or []
        aliases = getattr(node, "aliases", None) or {}

        if not module_name:
            raise CorpLangRuntimeError(
                "FromImportDeclaration missing module name", RuntimeErrorType.SYNTAX_ERROR
            )

        exports = context.interpreter._import_module(module_name, context.current_file)

        for item in items:
            alias = aliases.get(item, item) if isinstance(aliases, dict) else item
            value = exports.get(item) if isinstance(exports, dict) else None
            context.define_var(alias, value, None)
        return None


class AssignmentExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "Assignment"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        value = resolve_node_value(get_node_attr(node, "value", "initializer"), context)
        target = get_node_attr(node, "target", "name")
        if isinstance(target, str):
            context.set_var(target, value)
            return value
        if hasattr(target, "name"):
            context.set_var(getattr(target, "name"), value)
            return value
        # Assignments like obj[idx] = value
        if hasattr(target, "obj") and hasattr(target, "index"):
            obj = resolve_node_value(target.obj, context)
            idx = resolve_node_value(get_node_attr(target, "index", "key", "property"), context)

            if isinstance(obj, list):
                if not isinstance(idx, int):
                    raise CorpLangRuntimeError(
                        f"List index must be integer, got {type(idx).__name__}",
                        RuntimeErrorType.TYPE_ERROR,
                        node=node,
                    )
                if idx < 0 or idx >= len(obj):
                    raise CorpLangRuntimeError(
                        f"Index {idx} out of range",
                        RuntimeErrorType.TYPE_ERROR,
                        node=node,
                    )
                obj[idx] = value
                return value

            if isinstance(obj, dict):
                obj[idx] = value
                return value

            if isinstance(obj, InstanceObject):
                try:
                    setter = obj.get("set")
                    if callable(setter):
                        setter(idx, value)
                        return value
                except Exception:
                    pass
                try:
                    raw_fn = obj.get("__raw__")
                    if callable(raw_fn):
                        raw = raw_fn()
                        if isinstance(raw, (list, tuple, dict)):
                            raw[idx] = value
                            return value
                except Exception:
                    pass

            if hasattr(obj, "__setitem__"):
                obj[idx] = value
                return value
        if hasattr(target, "obj") and hasattr(target, "prop"):
            obj = resolve_node_value(target.obj, context)
            prop = get_node_attr(target, "prop", "property")
            if isinstance(obj, dict) and "__dict__" in obj:
                obj["__dict__"][prop] = value
                return value
            if isinstance(obj, InstanceObject):
                # Pass context for private member access validation
                obj.set(prop, value, context=context)
                return value
            if isinstance(obj, ClassObject):
                # Set static field on class
                obj.static_field_values[prop] = value
                return value
            if hasattr(obj, prop):
                setattr(obj, prop, value)
                return value
        if hasattr(node, "name"):
            context.set_var(getattr(node, "name"), value)
        return value


class ReturnExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ReturnStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        val_node = get_node_attr(node, "value", "argument")
        val = resolve_node_value(val_node, context) if val_node is not None else None
        raise ReturnException(val)


def register(registry: ExecutorRegistry):
    from src.corplang.compiler.nodes import (
        Program,
        ModelDeclaration,
        MigrationDeclaration,
        ModelOperation,
        DatasetOperation,
        AgentDefinition,
        AgentTrain,
        AgentEmbed,
        AgentPredict,
        AgentShutdown,
        AgentRun,
        LoopStatement,
        ServeStatement,
        StopStatement,
        AwaitStatement,
        VarDeclaration,
        ImportDeclaration,
        FromImportDeclaration,
        Assignment,
        ReturnStatement,
    )

    registry.register(Program, ProgramExecutor())
    registry.register(ModelDeclaration, ModelDeclNoOpExecutor())
    registry.register(MigrationDeclaration, ModelDeclNoOpExecutor())
    registry.register(ModelOperation, ModelOperationNoOpExecutor())
    registry.register(DatasetOperation, DatasetOperationNoOpExecutor())
    registry.register(AgentDefinition, AgentDefinitionExecutor())
    registry.register(AgentTrain, AgentTrainExecutor())
    registry.register(AgentEmbed, AgentEmbedExecutor())
    registry.register(AgentPredict, AgentPredictExecutor())
    registry.register(AgentShutdown, AgentShutdownExecutor())
    registry.register(AgentRun, AgentRunExecutor())
    registry.register(LoopStatement, LoopExecutor())
    registry.register(ServeStatement, ServeExecutor())
    registry.register(StopStatement, StopExecutor())
    registry.register(AwaitStatement, AwaitExecutor())
    registry.register(VarDeclaration, VarDeclarationExecutor())
    registry.register(ImportDeclaration, ImportDeclarationExecutor())
    registry.register(FromImportDeclaration, FromImportDeclarationExecutor())
    registry.register(Assignment, AssignmentExecutor())
    registry.register(ReturnStatement, ReturnExecutor())
