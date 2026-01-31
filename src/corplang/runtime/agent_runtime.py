"""Agent runtime manager for stateful execution without recompilation."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from threading import RLock

from .code_runner import CodeRunner
from .intelligence import get_provider_registry, IntelligenceConfig, ExecutionResult, ExecutionAction


@dataclass
class AgentState:
    """Stateful container for a single agent instance."""

    name: str
    definition: Any  # AgentDefinition AST node
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    is_trained: bool = False
    execution_count: int = 0

    # EXTENSION POINT: AI provider instance placeholder
    # Future: store provider-specific state (e.g., LiteLLM config, model weights)
    provider_state: Optional[Any] = None
    pending_action: Optional[Any] = None


class AgentManager:
    """Singleton manager for agent lifecycle without AST recompilation."""

    _instance = None
    _lock = RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._agents: Dict[str, AgentState] = {}
        self._lock = RLock()
        self._initialized = True

        # PoC code runner used to execute provider actions (python only PoC)
        self._code_runner = CodeRunner()

    def create_agent(self, definition_node: Any, env_snapshot: Optional[Dict[str, Any]] = None) -> None:
        """Register agent from compiled AST node without reparsing.

        Optionally capture a snapshot of the current execution environment so
        providers or runtime can call functions defined in that scope.
        """
        name = getattr(definition_node, "name", None)
        if not name:
            raise ValueError("Agent definition must have a name")

        with self._lock:
            self._agents[name] = AgentState(
                name=name,
                definition=definition_node,
                context_snapshot=env_snapshot or {},
            )

    def get_agent(self, name: str) -> Optional[AgentState]:
        """Retrieve agent state by name."""
        with self._lock:
            return self._agents.get(name)

    def list_agents(self) -> Dict[str, AgentState]:
        """Return all registered agents."""
        with self._lock:
            return self._agents.copy()

    # EXTENSION POINT: AI integration methods (contracts only)

    async def train_agent(self, train_node: Any) -> bool:
        """
        Train agent with provided data.
        """
        agent_name = getattr(train_node, "agent_name", None)
        agent = self.get_agent(agent_name)
        if not agent:
            return False

        cfg = IntelligenceConfig.from_ast(getattr(agent.definition, "intelligence", None))
        provider = get_provider_registry().create(cfg.provider, cfg) or get_provider_registry().create("placeholder", cfg)
        if not provider:
            return False

        # Delegate to provider's train
        success = await provider.train(getattr(train_node, "data", None), cfg)
        if success:
            agent.is_trained = True
        return success

    def _process_execution_result(self, agent: AgentState, exec_result: ExecutionResult) -> ExecutionResult:
        """Process ExecutionResult actions sequentially and produce a final result."""
        result = exec_result
        for action in list(result.actions or []):
            if action.type == "run_code":
                lang = action.language or result.language or "python"
                code = action.code or result.code or ""
                if isinstance(code, dict):
                    # simple heuristic: join files
                    code = "\n\n".join(code.values())
                run = self._code_runner.run(lang, code, context={})
                # attach run output
                result.metadata.setdefault("runs", []).append(run)
                if run.get("status") == "error":
                    result.status = "error"
                    result.output = run
                    # stop on runtime error
                    result.final = True
                    return result
            elif action.type == "log":
                msg = (action.args or {}).get("message")
                result.metadata.setdefault("logs", []).append(msg)
            elif action.type == "request_input":
                # Signal to the caller that input is required
                prompt = (action.args or {}).get("prompt") or "Input required:"
                result.status = "awaiting_input"
                result.final = False
                result.metadata.setdefault("prompts", []).append(prompt)
                # If the request relates to a pending function, store it on agent
                fn = (action.args or {}).get("fn")
                if fn:
                    agent.pending_action = action
                return result
            elif action.type == "call_fn":
                fn_name = (action.args or {}).get("fn")
                params = (action.args or {}).get("params") or {}

                if not fn_name:
                    result.status = "error"
                    result.output = "call_fn missing 'fn' name"
                    result.final = True
                    return result

                func = None
                try:
                    func = agent.context_snapshot.get(fn_name)
                except Exception:
                    func = None

                if not func or not callable(func):
                    result.status = "error"
                    result.output = f"function not found or not callable: {fn_name}"
                    result.final = True
                    return result

                # If no params supplied, mark agent as awaiting input and store pending action
                if not params:
                    agent.pending_action = action
                    prompt = f"Please provide parameters for function '{fn_name}' as 'value:key1=val1,key2=val2'"
                    result.status = "awaiting_input"
                    result.final = False
                    result.metadata.setdefault("prompts", []).append(prompt)
                    return result

                # Call function while capturing stdout/stderr
                import io
                from contextlib import redirect_stdout, redirect_stderr

                stdout_buf = io.StringIO()
                stderr_buf = io.StringIO()
                try:
                    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                        ret = func(**(params or {})) if isinstance(params, dict) else func(*params)
                except Exception as exc:
                    tb = str(exc)
                    run = {
                        "status": "error",
                        "stdout": stdout_buf.getvalue(),
                        "stderr": stderr_buf.getvalue(),
                        "result": None,
                        "error": tb,
                    }
                    result.metadata.setdefault("runs", []).append(run)
                    result.status = "error"
                    result.output = tb
                    result.final = True
                    return result

                run = {
                    "status": "ok",
                    "stdout": stdout_buf.getvalue(),
                    "stderr": stderr_buf.getvalue(),
                    "result": ret,
                    "error": None,
                }
                result.metadata.setdefault("runs", []).append(run)
                result.metadata.setdefault("call_result", []).append({"fn": fn_name, "result": ret})
                result.output = ret
                result.final = True
                return result
            elif action.type == "finalize":
                result.final = True
                # optionally set output
                if (action.args or {}).get("output") is not None:
                    result.output = action.args.get("output")
                return result
            # extend with more action types (read_file, write_file, call_fn)

        return result

    def predict_agent(self, agent_name: str, input_data: Any, context_env: Optional[object] = None) -> Any:
        """
        Execute prediction using an agent: call provider.invoke and process actions.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": "Agent not found"}

        agent.execution_count += 1

        cfg = IntelligenceConfig.from_ast(getattr(agent.definition, "intelligence", None))
        provider = (get_provider_registry().create(cfg.provider, cfg) or
                    get_provider_registry().create("placeholder", cfg))

        if not provider:
            return {"error": "No provider available"}

        # If agent has a pending action (e.g., awaiting params for a call_fn) and
        # the user replied with a 'value:' payload, process the pending action directly.
        if isinstance(input_data, str) and input_data.strip().lower().startswith("value:") and agent.pending_action:
            raw = input_data.split(":", 1)[1].strip()
            # parse simple key=value pairs separated by commas
            params = {}
            for part in raw.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if v.isdigit():
                        v = int(v)
                    params[k] = v
                else:
                    # single positional value stored under key '_val'
                    params.setdefault("_val", raw)

            action = agent.pending_action
            agent.pending_action = None
            exec_result = ExecutionResult(status="ok", final=True, actions=[ExecutionAction(type="call_fn", args={"fn": action.args.get("fn"), "params": params})])
        else:
                # Prepare a rich context for the provider with available functions and their signatures
                env_map = {}
                # Accept both Environment objects and dict-like snapshots
                if context_env is not None:
                    if hasattr(context_env, "variables"):
                        env_map.update(context_env.variables)
                    elif isinstance(context_env, dict):
                        env_map.update(context_env)

        # Build function specs
        functions = []
        import inspect

        for name, val in env_map.items():
            if not name or name.startswith("__"):
                continue
            spec = {"name": name}
            # CorpLang functions have 'declaration' with params/types
            decl = getattr(val, "declaration", None)
            if decl and hasattr(decl, "params"):
                spec["params"] = [
                    {"name": p, "type": (getattr(decl, "param_types", {}) or {}).get(p)} for p in getattr(decl, "params", [])
                ]
                spec["return_type"] = getattr(decl, "return_type", None)
                spec["source_file"] = getattr(decl, "file_path", getattr(decl, "file", None))
            elif callable(val):
                try:
                    sig = inspect.signature(val)
                    spec["params"] = [{"name": p.name, "type": None} for p in sig.parameters.values()]
                except Exception:
                    spec["params"] = []
            else:
                continue
            functions.append(spec)

        messages = [{"role": "user", "content": input_data}]
        exec_result = provider.invoke(messages, context={"agent": agent, "functions": functions})

        # Attach env_map so runtime can resolve call_fn against current environment
        try:
            exec_result.metadata.setdefault("env_map", env_map)
        except Exception:
            pass

        if not isinstance(exec_result, ExecutionResult):
            exec_result = ExecutionResult(status="ok", final=True, output=str(exec_result))

        final = self._process_execution_result(agent, exec_result)
        return final

    def run_agent(self, run_node: Any) -> Any:
        """
        Execute agent with runtime parameters.
        """
        agent_name = getattr(run_node, "agent_name", None)
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": "Agent not found"}

        # Extract input and delegate to predict flow
        input_data = getattr(run_node, "input", "")
        return self.predict_agent(agent_name, input_data)

    def embed_agent(self, agent_name: str, items: list) -> Any:
        """
        Generate embeddings using agent.
        
        PLACEHOLDER: Integrate AI embedding logic here.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": "Agent not found"}

        # TODO: Implement embedding via AI provider
        return {"status": "placeholder", "count": len(items)}

    def run_agent(self, run_node: Any) -> Any:
        """
        Execute agent with runtime parameters.
        
        PLACEHOLDER: Integrate AI execution logic here.
        """
        # TODO: Extract params from run_node and execute
        return {"status": "placeholder"}

    def shutdown_agent(self, agent_name: str, auth_token: Optional[str] = None) -> bool:
        """
        Shutdown agent and cleanup resources.
        
        PLACEHOLDER: Integrate AI provider cleanup here.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return False

        # TODO: Call provider.cleanup() if needed
        with self._lock:
            del self._agents[agent_name]

        return True


# Singleton accessor
def get_agent_manager() -> AgentManager:
    """Get the global AgentManager singleton."""
    return AgentManager()
