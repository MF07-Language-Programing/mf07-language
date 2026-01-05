from copy import deepcopy
from typing import Optional, Any, Set, Dict, Callable, List, TYPE_CHECKING

from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType, ExecutionError
from src.corplang.core.utils import safe_attr, bind_and_exec
from src.corplang.executor.context import Environment


if TYPE_CHECKING:
    from src.corplang.executor.executor import Executor


class CorpLangFunction:
    def __init__(self, declaration, closure, interpreter):
        self.declaration = declaration
        self.closure = closure
        self.interpreter = interpreter
        self.declaration_file = safe_attr(declaration, "file", "source_file", "filename") or interpreter.current_file

    def __call__(self, *args, **kwargs):
        # For async declarations, return a lazy awaitable that executes the body only when awaited.
        if getattr(self.declaration, "is_async", False):
            fn = self

            class _Awaitable:
                def __init__(self, args, kwargs, closure, declaration, interpreter):
                    self._args = args
                    self._kwargs = kwargs
                    self._closure = closure
                    self._declaration = declaration
                    self._interpreter = interpreter

                def __await__(self):
                    # execute the function body when awaited
                    env = Environment(self._closure)
                    try:
                        result = bind_and_exec(
                            self._interpreter,
                            self._declaration,
                            env,
                            list(self._args),
                            dict(self._kwargs or {}),
                            self._interpreter.root_context,
                        )
                        if False:
                            yield
                        return result
                    except Exception:
                        raise

            return _Awaitable(args, kwargs, self.closure, self.declaration, self.interpreter)

        # Synchronous path (regular functions)
        env = Environment(self.closure)
        result = bind_and_exec(
            self.interpreter,
            self.declaration,
            env,
            args,
            kwargs,
            self.interpreter.root_context,
        )
        return result

# noinspection PyBroadException
class ClassObject:
    def __init__(self, declaration, interpreter, env=None):
        self.declaration = declaration
        self.interpreter = interpreter
        self.name = getattr(declaration, "name", None)
        self._env = env or interpreter.global_env
        self.declaration_file = safe_attr(declaration, "file", "source_file", "filename") or interpreter.current_file

        if self.name:
            self._env.define(self.name, self)

        self.parent = None
        if getattr(declaration, "extends", None):
            try:
                # Try direct lookup first
                self.parent = self._env.get(declaration.extends)
            except Exception:
                # Fallback: try to find symbol inside module namespaces exported to interpreter.global_env
                try:
                    class_name = declaration.extends
                    ge = getattr(self.interpreter, "global_env", None)
                    if ge:
                        for _, val in (ge.variables or {}).items():
                            def find_in_namespace(obj):
                                if isinstance(obj, dict):
                                    if class_name in obj:
                                        return obj[class_name]
                                    for sub in obj.values():
                                        res = find_in_namespace(sub)
                                        if res is not None:
                                            return res
                                return None

                            found = find_in_namespace(val)
                            if found is not None:
                                self.parent = found
                                break
                except Exception:
                    pass

        self.interfaces = [
            getattr(i, "name", i)
            for i in (getattr(declaration, "implements", []) or [])
            if i
        ]

        self.instance_methods = {}
        self.static_methods = {}
        self.instance_fields = {}
        self.static_fields = {}

        from src.corplang.compiler.nodes import MethodDeclaration, FieldDeclaration

        for m in getattr(declaration, "body", []) or []:
            if isinstance(m, MethodDeclaration):
                target = self.static_methods if m.is_static else self.instance_methods
            elif isinstance(m, FieldDeclaration):
                target = self.static_fields if m.is_static else self.instance_fields
            else:
                continue

            target[m.name] = m
            if getattr(m, "file", None) is None:
                m.file = self.declaration_file



        self.static_field_values = {
            k: self._eval_static(v)
            for k, v in self.static_fields.items()
            if getattr(v, "value", None) is not None
        }

    def _eval_static(self, decl):
        try:
            return self.interpreter.execute(decl.value, self.interpreter.root_context)
        except Exception:
            return None

    def __repr__(self):
        if "toString" in self.instance_methods:
            try:
                v = self.get("toString")()
                if isinstance(v, str):
                    return v
            except Exception:
                pass
        return f"<Class {self.name or '<anonymous>'} @{hex(id(self))}>"

    __str__ = __repr__

    def __call__(self, *args, **kwargs):
        generic_env = kwargs.pop('__generic_env__', {})
        inst = InstanceObject(self, self.interpreter)
        
        # Store generics in instance
        if generic_env:
            inst.__generics__ = generic_env

        # Initialize instance fields from this class and parent classes
        # Only initialize fields with explicit initialization values
        # Uninitialized fields remain undefined until set by constructor
        cur = self
        while cur is not None:
            for k, f in cur.instance_fields.items():
                try:
                    val = cur._eval_static(f)
                    # Only populate _fields if evaluation succeeded and returned non-None
                    # This prevents None pollution and allows proper undefined semantics
                    if val is not None:
                        inst._fields[k] = val
                except Exception:
                    # Field evaluation failed - leave undefined, don't populate with None
                    # Constructor will set it later or access will raise proper error
                    pass
            cur = getattr(cur, "parent", None)

        # Call constructor if available (searches parent chain via InstanceObject.get)
        try:
            ctor = inst.get("constructor")
            if callable(ctor):
                ctor(*args, **kwargs)
        except CorpLangRuntimeError as e:
            # Re-raise runtime errors from constructor - don't mask them
            if "not found" not in str(e).lower():
                raise
            # No constructor found - that's fine
            pass
        except AttributeError:
            # No constructor attribute - that's expected for some classes
            pass

        return inst

    def get_static(self, name):
        if name in self.static_field_values:
            return self.static_field_values[name]

        if name in self.static_fields:
            val = self._eval_static(self.static_fields[name])
            self.static_field_values[name] = val
            return val

        if name in self.static_methods:
            declare = self.static_methods[name]

            def call(*a, **kw):
                # Use module environment where class was defined as closure
                # Pass closure_env directly without wrapper
                closure_env = getattr(self, '_env', None) or self.interpreter.global_env
                return bind_and_exec(
                    self.interpreter,
                    declare,
                    closure_env,
                    a,
                    kw,
                    self.interpreter.root_context,
                    class_ref=self,
                )

            return call

        raise CorpLangRuntimeError(
            f"Static property '{name}' not found on class {self.name}",
            RuntimeErrorType.REFERENCE_ERROR,
        )

    @staticmethod
    def get(param):
        """Super method override"""
        raise CorpLangRuntimeError(f"Not implemented: {param}")


# noinspection PyUnusedLocal
class InstanceObject:
    def __init__(self, class_obj, interpreter):
        self._class = class_obj
        self.class_obj = class_obj
        self.class_ref = class_obj
        self._interpreter = interpreter
        self._fields = {}
        self.__generics__ = {}

    @property
    def class_name(self):
        return self._class.name

    def __repr__(self):
        if "toString" in self._class.instance_methods:
            # noinspection PyBroadException
            try:
                v = self.get("toString")()
                if isinstance(v, str):
                    return v
            except Exception:
                pass
        return f"<Instance {self.class_name} @{hex(id(self))}>"

    __str__ = __repr__

    def set(self, name, value, context=None):
        self._fields[name] = value

    def get(self, name, context=None):
        if name in self._fields:
            return self._fields[name]

        # Lookup instance method on class or parent chain
        cur_cls = self._class
        declare = None
        class_ref = None
        while cur_cls is not None:
            if name in cur_cls.instance_methods:
                declare = cur_cls.instance_methods[name]
                class_ref = cur_cls
                break
            cur_cls = getattr(cur_cls, 'parent', None)

        if declare is not None:
            def call(*a, **kw):
                # Prefer explicit _call_context kw arg when provided, otherwise
                # fall back to a temporary pending context attribute set by the caller.
                call_ctx = kw.pop("_call_context", None) or getattr(call, "_pending_call_context", None)
                # If method declared async, validate calling context and return an awaitable.
                if getattr(declare, "is_async", False):
                    if not call_ctx or (not getattr(call_ctx, "is_async", False) and not getattr(call_ctx, "_awaiting", False)):
                        raise CorpLangRuntimeError(
                            f"Cannot call async method '{getattr(declare,'name','<anon>')}' from non-async context; use 'await' or mark caller async",
                            RuntimeErrorType.TYPE_ERROR,
                        )

                    class _AwaitableMethod:
                        def __init__(self, args, kwargs, decl, interpreter, this, class_ref, call_ctx):
                            self._args = args
                            self._kwargs = kwargs
                            self._decl = decl
                            self._interpreter = interpreter
                            self._this = this
                            self._class_ref = class_ref
                            self._call_ctx = call_ctx

                        def __await__(self):
                            # Use module environment where class was defined as closure
                            # bind_and_exec will handle parameter binding and 'this' setup
                            closure_env = getattr(self._class_ref, '_env', None) or self._interpreter.global_env
                            try:
                                # Prefer an explicit call context, then a pending context attached to this awaitable,
                                # then interpreter root context as last resort.
                                ctx = getattr(self, "_call_ctx", None) or getattr(self, "_pending_call_context", None) or self._interpreter.root_context
                                result = bind_and_exec(
                                    self._interpreter,
                                    self._decl,
                                    closure_env,
                                    list(self._args),
                                    dict(self._kwargs or {}),
                                    ctx,
                                    this=self._this,
                                    class_ref=self._class_ref,
                                )
                                if False:
                                    yield
                                return result
                            except Exception:
                                raise

                    return _AwaitableMethod(a, kw, declare, self._interpreter, self, class_ref, call_ctx)

                # Use module environment where class was defined as closure
                closure_env = getattr(class_ref, '_env', None)
                
                if closure_env is None:
                    closure_env = self._interpreter.global_env
                
                # Pass closure_env directly to bind_and_exec
                # Do NOT create intermediate Environment() here
                ctx = call_ctx or self._interpreter.root_context
                
                return bind_and_exec(
                    self._interpreter,
                    declare,
                    closure_env,  # ← pass closure directly
                    a,
                    kw,
                    ctx,
                    this=self,
                    class_ref=class_ref,
                )

            # annotate call for executor-level checks
            try:
                call._is_corplang_method = True
                call._declare = declare
            except Exception:
                pass

            return call

            # annotate call for executor-level checks
            try:
                call._is_corplang_method = True
                call._declare = declare
            except Exception:
                pass

            return call

        raise CorpLangRuntimeError(
            f"Property '{name}' not found on instance of {self.class_name}",
            RuntimeErrorType.REFERENCE_ERROR,
        )

    def get_method(self, name, context=None):
        """Return method wrapper even if a same-named field exists."""
        cur_cls = self._class
        declare = None
        class_ref = None
        while cur_cls is not None:
            if name in cur_cls.instance_methods:
                declare = cur_cls.instance_methods[name]
                class_ref = cur_cls
                break
            cur_cls = getattr(cur_cls, 'parent', None)

        if declare is None:
            raise CorpLangRuntimeError(
                f"Method '{name}' not found on instance of {self.class_name}",
                RuntimeErrorType.REFERENCE_ERROR,
            )

        def call(*a, **kw):
            call_ctx = kw.pop("_call_context", None) or getattr(call, "_pending_call_context", None)
            if getattr(declare, "is_async", False):
                if not call_ctx or (not getattr(call_ctx, "is_async", False) and not getattr(call_ctx, "_awaiting", False)):
                    raise CorpLangRuntimeError(
                        f"Cannot call async method '{getattr(declare,'name','<anon>')}' from non-async context; use 'await' or mark caller async",
                        RuntimeErrorType.TYPE_ERROR,
                    )

                class _AwaitableMethod:
                    def __init__(self, args, kwargs, decl, interpreter, this, class_ref, call_ctx):
                        self._args = args
                        self._kwargs = kwargs
                        self._decl = decl
                        self._interpreter = interpreter
                        self._this = this
                        self._class_ref = class_ref
                        self._call_ctx = call_ctx

                    def __await__(self):
                        env = Environment(self._interpreter.global_env)
                        if self._this is not None:
                            env.define("this", self._this)
                        if self._class_ref is not None:
                            env.define(self._class_ref.name, self._class_ref)
                        try:
                            ctx = getattr(self, "_call_ctx", None) or getattr(self, "_pending_call_context", None) or self._interpreter.root_context
                            result = bind_and_exec(
                                self._interpreter,
                                self._decl,
                                env,
                                list(self._args),
                                dict(self._kwargs or {}),
                                ctx,
                                this=self._this,
                                class_ref=self._class_ref,
                            )
                            if False:
                                yield
                            return result
                        except Exception:
                            raise

                return _AwaitableMethod(a, kw, declare, self._interpreter, self, class_ref, call_ctx)

            # Use class-defined environment, not global
            closure_env = getattr(class_ref, '_env', None) or self._interpreter.global_env
            ctx = call_ctx or self._interpreter.root_context
            return bind_and_exec(
                self._interpreter,
                declare,
                closure_env,
                a,
                kw,
                ctx,
                this=self,
                class_ref=class_ref,
            )

        try:
            call._is_corplang_method = True
            call._declare = declare
        except Exception:
            pass

        return call


class Scope:
    """Variable scope with parent chaining and constants."""

    def __init__(self, parent: Optional["Scope"] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.constants: Set[str] = set()

    def define(self, name: str, value: Any, is_constant: bool = False):
        """Define a variable in this scope."""
        self.variables[name] = value
        if is_constant:
            self.constants.add(name)

    def assign(self, name: str, value: Any):
        """Assign a variable, respecting constants."""
        scope = self
        while scope:
            if name in scope.constants:
                raise ExecutionError(f"Cannot reassign to constant '{name}'")
            if name in scope.variables:
                scope.variables[name] = value
                return
            scope = scope.parent

        self.variables[name] = value

    def lookup(self, name: str) -> Optional[Any]:
        """Look up a variable in the scope chain."""
        if name in self.variables:
            return self.variables[name]
        return self.parent.lookup(name) if self.parent else None

    def exists(self, name: str) -> bool:
        """Check if a variable exists."""
        return name in self.variables or (self.parent.exists(name) if self.parent else False)

    def has_local(self, name: str) -> bool:
        """Check if a variable exists locally."""
        return name in self.variables

    def is_constant(self, name: str) -> bool:
        """Check if a variable is constant."""
        return name in self.constants or (self.parent.is_constant(name) if self.parent else False)


class CorpLangObject:
    """Base object for CorpLang runtime."""

    def __init__(self, class_name: str):
        self.class_name = class_name
        self.fields: Dict[str, Any] = {}
        self.methods: Dict[str, Callable] = {}

    def get_field(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        raise ExecutionError(f"Field '{name}' not found in {self.class_name}")

    def set_field(self, name: str, value: Any):
        self.fields[name] = value

    def call_method(
            self,
            name: str,
            args: List[Any],
            executor: "Executor",
            kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if name not in self.methods:
            raise ExecutionError(f"Method '{name}' not found in {self.class_name}")

        fn = self.methods[name]
        try:
            if isinstance(fn, UserFunction):
                return fn(args, executor, kwargs or {})
            return fn(*args, **(kwargs or {}))
        except Exception:
            raise


# noinspection PyBroadException
class UserFunction:
    """Wrapper for user-defined function closures."""

    def __init__(
            self,
            fn: Callable[..., Any],
            origin_file: Optional[str] = None,
            origin_line: Optional[int] = None,
    ):
        self.fn = fn
        self.origin_file = origin_file
        self.origin_line = origin_line

    def __call__(
            self,
            args: List[Any],
            executor: Optional["Executor"] = None,
            kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if executor and hasattr(executor, "push_frame"):
            self._push_frame(executor)
            try:
                return self.fn(args, executor, kwargs or {})
            except Exception as e:
                self._attach_stack(e, executor)
                raise
            finally:
                self._pop_frame(executor)

        return self.fn(args, executor, kwargs or {})

    def _push_frame(self, executor: "Executor"):
        try:
            executor.push_frame(
                getattr(executor, "current_module_path", None)
                or getattr(executor, "runtime_source_root", None),
                self.origin_line or 1,
                getattr(self.fn, "__name__", "<function>"),
                getattr(executor.current_scope, "variables", {}),
                origin_file=self.origin_file,
                origin_line=self.origin_line,
            )
        except Exception:
            pass

    @staticmethod
    def _attach_stack(exc: Exception, executor):
        try:
            setattr(exc, "mp_stack", deepcopy(getattr(executor, "call_stack", [])))
        except Exception:
            pass

    @staticmethod
    def _pop_frame(executor: "Executor"):
        try:
            executor.pop_frame()
        except Exception:
            pass
