from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass(kw_only=True)
class ASTNode:
    """
    Base class for all Abstract Syntax Tree nodes.

    Attributes:
        line (int): The line number where the node is located in the source code.
        column (int): The column number where the node starts.
        file_path (Optional[str]): The path to the source file containing this node.
        parent (Optional['ASTNode']): The parent node in the AST.
    """
    line: int
    column: int
    file_path: Optional[str] = None
    parent: Optional['ASTNode'] = field(default=None, repr=False)


@dataclass(kw_only=True)
class Program(ASTNode):
    """
    Represents the root of the AST, containing all top-level statements.

    Attributes:
        statements (List[ASTNode]): A list of top-level statements in the program.
        docstring (Optional[str]): An optional docstring for the program.
    """
    statements: List[ASTNode]
    docstring: Optional[str] = None


@dataclass(kw_only=True)
class VarDeclaration(ASTNode):
    """
    Represents a variable declaration statement.

    Attributes:
        name (str): The name of the variable.
        value (ASTNode): The initial value assigned to the variable.
        type_annotation (Optional[str]): The explicit type of the variable, if provided.
    """
    name: str
    value: ASTNode
    type_annotation: Optional[str] = None


@dataclass(kw_only=True)
class FunctionDeclaration(ASTNode):
    """
    Represents a function or procedure declaration.

    Attributes:
        name (str): The name of the function.
        params (List[str]): The list of parameter names.
        body (List[ASTNode]): The sequence of statements in the function body.
        is_async (bool): Whether the function is declared as asynchronous.
        param_types (Optional[Dict[str, Optional[str]]]): Mapping of parameter names to their types.
        param_defaults (Optional[Dict[str, Any]]): Mapping of parameter names to their default values.
        docstring (Optional[str]): An optional docstring for the function.
        return_type (Optional[str]): The declared return type of the function.
        generic_params (Optional[List[str]]): List of generic type parameters.
    """
    name: str
    params: List[str]
    body: List[ASTNode]
    is_async: bool = False
    param_types: Optional[Dict[str, Optional[str]]] = None
    param_defaults: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None
    return_type: Optional[str] = None
    generic_params: Optional[List[str]] = None


@dataclass(kw_only=True)
class LambdaExpression(ASTNode):
    """
    Represents an anonymous function (lambda expression).

    Attributes:
        params (List[str]): The list of parameter names.
        body (List[ASTNode]): The sequence of statements or expression in the lambda body.
        param_types (Optional[Dict[str, Optional[str]]]): Mapping of parameter names to their types.
        param_defaults (Optional[Dict[str, Any]]): Mapping of parameter names to their default values.
        docstring (Optional[str]): An optional docstring for the lambda.
        return_type (Optional[str]): The expected return type.
    """
    params: List[str]
    body: List[ASTNode]
    param_types: Optional[Dict[str, Optional[str]]] = None
    param_defaults: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None
    return_type: Optional[str] = None


@dataclass(kw_only=True)
class Assignment(ASTNode):
    """
    Represents an assignment operation.

    Attributes:
        target (Any): The target being assigned to (usually a name or property/index access).
        value (ASTNode): The value to be assigned.
    """
    target: Any
    value: ASTNode


@dataclass(kw_only=True)
class ClassDeclaration(ASTNode):
    """
    Represents a class definition.

    Attributes:
        name (str): The name of the class.
        body (List[ASTNode]): Members of the class (methods, fields).
        extends (Optional[str]): The name of the base class.
        implements (Optional[List[str]]): List of implemented interfaces or contracts.
        is_abstract (bool): Whether the class is abstract.
        generic_params (Optional[List[str]]): List of generic type parameters.
        type_parameters (Optional[List[str]]): Alias for generic_params for consistency.
        docstring (Optional[str]): An optional docstring for the class.
        is_driver (bool): Whether the class is declared as a driver.
    """
    name: str
    body: List[ASTNode]
    extends: Optional[str] = None
    implements: Optional[List[str]] = None
    is_abstract: bool = False
    generic_params: Optional[List[str]] = None
    type_parameters: Optional[List[str]] = None
    docstring: Optional[str] = None
    is_driver: bool = False


@dataclass(kw_only=True)
class MethodDeclaration(ASTNode):
    """
    Represents a method declaration within a class.

    Attributes:
        name (str): The name of the method.
        params (List[str]): The list of parameter names.
        body (List[ASTNode]): The sequence of statements in the method body.
        is_static (bool): Whether the method is static.
        is_private (bool): Whether the method is private.
        is_abstract (bool): Whether the method is abstract.
        is_async (bool): Whether the method is async.
        param_types (Optional[Dict[str, Optional[str]]]): Mapping of parameter names to their types.
        param_defaults (Optional[Dict[str, Any]]): Mapping of parameter names to their default values.
        docstring (Optional[str]): An optional docstring for the method.
        return_type (Optional[str]): The declared return type of the method.
        generic_params (Optional[List[str]]): List of generic type parameters.
    """
    name: str
    params: List[str]
    body: List[ASTNode]
    is_static: bool = False
    is_private: bool = False
    is_abstract: bool = False
    is_async: bool = False
    param_types: Optional[Dict[str, Optional[str]]] = None
    param_defaults: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None
    return_type: Optional[str] = None
    generic_params: Optional[List[str]] = None


@dataclass(kw_only=True)
class FieldDeclaration(ASTNode):
    """
    Represents a field (property) declaration within a class.

    Attributes:
        name (str): The name of the field.
        value (Optional[ASTNode]): The initial value of the field, if any.
        is_private (bool): Whether the field is private.
        is_static (bool): Whether the field is static.
        type_annotation (Optional[str]): The explicit type of the field.
    """
    name: str
    value: Optional[ASTNode] = None
    is_private: bool = False
    is_static: bool = False
    type_annotation: Optional[str] = None


@dataclass(kw_only=True)
class NewExpression(ASTNode):
    """
    Represents an instantiation of a class (e.g., `new MyClass()`).

    Attributes:
        class_name (Any): The name of the class (str or GenericIdentifier).
        type_arguments (Optional[List[TypeAnnotation]]): Explicit type arguments for generics.
        args (List[CallArgument]): Arguments passed to the constructor.
    """
    class_name: Any
    type_arguments: Optional[List["TypeAnnotation"]] = None
    args: List["CallArgument"] = field(default_factory=list)


@dataclass(kw_only=True)
class CallArgument(ASTNode):
    """
    Represents an argument passed in a function or method call.

    Attributes:
        name (Optional[str]): The name of the argument (for named arguments).
        value (ASTNode): The value being passed.
    """
    name: Optional[str]
    value: ASTNode


@dataclass(kw_only=True)
class ThisExpression(ASTNode):
    """
    Represents the 'this' (or 'self') reference to the current instance.
    """
    pass


@dataclass(kw_only=True)
class InterfaceDeclaration(ASTNode):
    """
    Represents an interface definition.

    Attributes:
        name (str): The name of the interface.
        methods (List[MethodDeclaration]): Method signatures defined by the interface.
        extends (Optional[List[str]]): List of interfaces this interface extends.
        generic_params (Optional[List[str]]): List of generic type parameters.
    """
    name: str
    methods: List[MethodDeclaration]
    extends: Optional[List[str]] = None
    generic_params: Optional[List[str]] = None


@dataclass(kw_only=True)
class ContractDeclaration(ASTNode):
    """
    Represents a contract definition (similar to interface but with potentially different semantics).

    Attributes:
        name (str): The name of the contract.
        methods (List[MethodDeclaration]): Method signatures defined by the contract.
        extends (Optional[List[str]]): List of contracts this contract extends.
        generic_params (Optional[List[str]]): List of generic type parameters.
    """
    name: str
    methods: List[MethodDeclaration]
    extends: Optional[List[str]] = None
    generic_params: Optional[List[str]] = None


@dataclass(kw_only=True)
class GenericTypeExpression(ASTNode):
    """
    Represents a type with generic parameters (e.g., `List<string>`).

    Attributes:
        base_type (str): The name of the base generic type.
        type_parameters (List[str]): The list of type arguments.
    """
    base_type: str
    type_parameters: List[str]


@dataclass(kw_only=True)
class JsonObject(ASTNode):
    """
    Represents a literal JSON-like object.

    Attributes:
        value (Dict[str, Any]): The key-value pairs of the object.
    """
    value: Dict[str, Any]


@dataclass(kw_only=True)
class JsonArray(ASTNode):
    """
    Represents a literal JSON-like array.

    Attributes:
        value (List[Any]): The items in the array.
    """
    value: List[Any]


@dataclass(kw_only=True)
class NullLiteral(ASTNode):
    """
    Represents a null or none value literal.
    """
    pass


@dataclass(kw_only=True)
class ImportDeclaration(ASTNode):
    """
    Represents a simple module import (e.g., `import math`).

    Attributes:
        module (str): The name or path of the module to import.
    """
    module: str


@dataclass(kw_only=True)
class FromImportDeclaration(ASTNode):
    """
    Represents an import from a specific module (e.g., `from math import sin, cos`).

    Attributes:
        module (str): The name or path of the module.
        items (List[str]): The specific items to import.
        aliases (Optional[Dict[str, str]]): Mapping of imported items to their local aliases.
    """
    module: str
    items: List[str]
    aliases: Optional[Dict[str, str]] = None


@dataclass(kw_only=True)
class Await(ASTNode):
    """
    Represents an await expression for asynchronous operations.

    Attributes:
        expression (ASTNode): The asynchronous expression to wait for.
    """
    expression: ASTNode


@dataclass(kw_only=True)
class BinaryOp(ASTNode):
    """
    Represents a binary operation (e.g., `a + b`).

    Attributes:
        left (ASTNode): The left-hand side operand.
        operator (str): The operator symbol (e.g., '+', '-', '*', '/').
        right (ASTNode): The right-hand side operand.
    """
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass(kw_only=True)
class UnaryOp(ASTNode):
    """
    Represents a unary operation (e.g., `-a`, `!b`).

    Attributes:
        operator (str): The operator symbol.
        operand (ASTNode): The operand.
    """
    operator: str
    operand: ASTNode


@dataclass(kw_only=True)
class FunctionCall(ASTNode):
    """
    Represents a function or method call.

    Attributes:
        callee (Any): The expression being called (str, PropertyAccess, etc.).
        args (List[CallArgument]): The arguments passed to the call.
    """
    callee: Any
    args: List[CallArgument]


@dataclass(kw_only=True)
class PropertyAccess(ASTNode):
    """
    Represents access to an object property (e.g., `obj.prop`).

    Attributes:
        obj (ASTNode): The object being accessed.
        prop (str): The name of the property.
    """
    obj: ASTNode
    prop: str


@dataclass(kw_only=True)
class IndexAccess(ASTNode):
    """
    Represents access to an array or dictionary by index (e.g., `arr[0]`).

    Attributes:
        obj (ASTNode): The object being indexed.
        index (ASTNode): The index expression.
    """
    obj: ASTNode
    index: ASTNode


@dataclass(kw_only=True)
class SuperExpression(ASTNode):
    """
    Represents a 'super' reference to the base class.
    """
    pass


@dataclass(kw_only=True)
class IfStatement(ASTNode):
    """
    Represents an if-else conditional statement.

    Attributes:
        condition (ASTNode): The condition expression.
        then_stmt (List[ASTNode]): Statements to execute if the condition is true.
        else_stmt (Optional[List[ASTNode]]): Statements to execute if the condition is false.
    """
    condition: ASTNode
    then_stmt: List[ASTNode]
    else_stmt: Optional[List[ASTNode]] = None


@dataclass(kw_only=True)
class WhileStatement(ASTNode):
    """
    Represents a while loop statement.

    Attributes:
        condition (ASTNode): The loop condition.
        body (List[ASTNode]): Statements to execute in each iteration.
    """
    condition: ASTNode
    body: List[ASTNode]


@dataclass(kw_only=True)
class ForStatement(ASTNode):
    """
    Represents a traditional for loop: `for (init; condition; update) { body }`.

    Attributes:
        init (Optional[ASTNode]): The initialization expression or statement.
        condition (Optional[ASTNode]): The loop continuation condition.
        update (Optional[ASTNode]): The iteration update expression.
        body (List[ASTNode]): Statements to execute in the loop body.
    """
    init: Optional[ASTNode]  # var i = 0
    condition: Optional[ASTNode]  # i < 10
    update: Optional[ASTNode]  # i++
    body: List[ASTNode]


@dataclass(kw_only=True)
class ForInStatement(ASTNode):
    """
    Represents a for-in loop: `for (var item in collection) { body }`.

    Attributes:
        variable (str): The name of the iteration variable.
        iterable (ASTNode): The object to iterate over.
        body (List[ASTNode]): Statements to execute in the loop body.
        type_annotation (Optional[str]): Optional type for the iteration variable.
    """
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    type_annotation: Optional[str] = None


@dataclass(kw_only=True)
class ForOfStatement(ASTNode):
    """
    Represents a for-of loop: `for (var item of collection) { body }`.

    Attributes:
        variable (str): The name of the iteration variable.
        iterable (ASTNode): The object to iterate over.
        body (List[ASTNode]): Statements to execute in the loop body.
        type_annotation (Optional[str]): Optional type for the iteration variable.
    """
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    type_annotation: Optional[str] = None


@dataclass(kw_only=True)
class CatchClause(ASTNode):
    """
    Represents a catch block in a try-catch statement.

    Attributes:
        exception_type (Optional[str]): The type of exception to catch.
        exception_var (Optional[str]): The variable name for the caught exception.
        body (List[ASTNode]): Statements to execute if the exception matches.
    """
    exception_type: Optional[str]
    exception_var: Optional[str]
    body: List[ASTNode]


@dataclass(kw_only=True)
class TryStatement(ASTNode):
    """
    Represents a try-catch-finally statement.

    Attributes:
        try_block (List[ASTNode]): The block of code to monitor for exceptions.
        catch_clauses (List[CatchClause]): One or more catch blocks.
        finally_block (Optional[List[ASTNode]]): The finally block of code.
    """
    try_block: List[ASTNode]
    catch_clauses: List[CatchClause]
    finally_block: Optional[List[ASTNode]] = None


@dataclass(kw_only=True)
class WithItem(ASTNode):
    """
    Represents an item in a 'with' statement.

    Attributes:
        context_expr (ASTNode): The expression providing the context.
        target (Optional[str]): The optional variable name for the context.
    """
    context_expr: ASTNode
    target: Optional[str] = None


@dataclass(kw_only=True)
class WithStatement(ASTNode):
    """
    Represents a 'with' statement for context management.

    Attributes:
        items (List[WithItem]): List of context items.
        body (List[ASTNode]): Statements to execute within the context.
        is_async (bool): Whether the context is asynchronous.
    """
    items: List[WithItem]
    body: List[ASTNode]
    is_async: bool = False


@dataclass(kw_only=True)
class ThrowStatement(ASTNode):
    """
    Represents a 'throw' (or 'raise') statement.

    Attributes:
        expression (Optional[ASTNode]): The exception expression to throw.
    """
    expression: Optional[ASTNode]


@dataclass(kw_only=True)
class DeleteStatement(ASTNode):
    """
    Represents a statement to delete a property or index (e.g., `delete obj.prop`).

    Attributes:
        target (ASTNode): The target expression to delete.
    """
    target: ASTNode


@dataclass(kw_only=True)
class ReturnStatement(ASTNode):
    """
    Represents a 'return' statement from a function or method.

    Attributes:
        value (Optional[ASTNode]): The value to return.
    """
    value: Optional[ASTNode] = None


@dataclass(kw_only=True)
class BreakStatement(ASTNode):
    """
    Represents a 'break' statement to exit a loop.
    """
    pass


@dataclass(kw_only=True)
class ContinueStatement(ASTNode):
    """
    Represents a 'continue' statement to skip to the next loop iteration.
    """
    pass


@dataclass(kw_only=True)
class Literal(ASTNode):
    """
    Represents a literal value (e.g., number, string, boolean).

    Attributes:
        value (Union[int, float, str, bool]): The actual value of the literal.
    """
    value: Union[int, float, str, bool, None]


@dataclass(kw_only=True)
class InterpolatedString(ASTNode):
    """
    Represents a string with embedded expressions (e.g., `f"hello {name}"`).

    Attributes:
        parts (List[Any]): List of strings and AST nodes.
    """
    parts: List[Any]  # List[str or AST expression nodes]


@dataclass(kw_only=True)
class Identifier(ASTNode):
    """
    Represents a name/identifier in the source code.

    Attributes:
        name (str): The name of the identifier.
    """
    name: str


@dataclass(kw_only=True)
class GenericIdentifier(ASTNode):
    """
    Represents an identifier with generic type arguments (e.g., `Map<string, int>`).

    Attributes:
        name (str): The base name of the identifier.
        type_args (List[Any]): The list of generic type arguments.
    """
    name: str
    type_args: List[Any]

    def __eq__(self, other):
        if not isinstance(other, GenericIdentifier):
            return False
        return self.name == other.name and self.type_args == other.type_args

    def __hash__(self):
        # Hash by name and tuple of type_args (recursively hashable)
        return hash((self.name, tuple(self.type_args)))


@dataclass(kw_only=True)
class TypeAnnotation(ASTNode):
    """
    Represents a type annotation in the source code.

    Attributes:
        base (str): The base type name.
        args (Optional[List["TypeAnnotation"]]): Generic type arguments, if any.
    """
    base: str
    args: Optional[List["TypeAnnotation"]] = None

    def __repr__(self):
        if not self.args:
            return self.base
        return f"{self.base}<" + ",".join(repr(a) for a in self.args) + ">"

    def __eq__(self, other):
        if not isinstance(other, TypeAnnotation):
            return False
        return self.base == other.base and self.args == other.args

    def __hash__(self):
        if self.args is None:
            return hash(self.base)
        return hash((self.base, tuple(self.args)))


@dataclass(kw_only=True)
class DatasetOperation(ASTNode):
    """
    Represents an operation on a dataset (e.g., load, save, filter).

    Attributes:
        operation (str): The name of the operation.
        target (str): The target dataset identifier.
        params (Dict[str, Any]): Parameters for the operation.
    """
    operation: str  # 'load', 'save', 'filter', etc.
    target: str
    params: Dict[str, Any]


@dataclass(kw_only=True)
class ModelArgument(ASTNode):
    """
    Represents a named argument for a model operation.

    Attributes:
        key (str): The name of the argument.
        value (ASTNode): The value of the argument.
    """
    key: str
    value: ASTNode


@dataclass(kw_only=True)
class ModelConfigBlock(ASTNode):
    """
    Represents a configuration block for a model or agent.

    Attributes:
        entries (Dict[str, ASTNode]): Configuration entries as key-value pairs.
    """
    entries: Dict[str, ASTNode] = field(default_factory=dict)


@dataclass(kw_only=True)
class ModelOperation(ASTNode):
    """
    Represents an operation related to a machine learning model.

    Attributes:
        operation (str): The type of operation (e.g., create, train, predict).
        model_name (Optional[str]): The name of the model.
        params (Dict[str, ASTNode]): Named parameters.
        args (List[ModelArgument]): Positional or named arguments.
        block (Optional[ModelConfigBlock]): A nested configuration block.
        response_model (Optional[str]): The expected response model name.
        init_function (Optional[str]): A function to initialize the model.
        permissions (Optional[ModelConfigBlock]): Permission configuration.
    """
    operation: str
    model_name: Optional[str]
    params: Dict[str, ASTNode] = field(default_factory=dict)
    args: List[ModelArgument] = field(default_factory=list)
    block: Optional[ModelConfigBlock] = None
    response_model: Optional[str] = None
    init_function: Optional[str] = None
    permissions: Optional[ModelConfigBlock] = None


# --- AGENTS (new unified abstraction replacing model/dataset primitives) ---
@dataclass(kw_only=True)
class AgentIntelligenceBlock(ASTNode):
    """
    Represents the intelligence (AI) configuration of an agent.

    Attributes:
        provider (Optional[str]): The AI provider (e.g., 'openai', 'anthropic').
        capability (Optional[str]): The primary capability (e.g., 'vision', 'chat').
        training (Optional[str]): Training-related configuration.
        entries (Dict[str, Any]): Additional intelligence settings.
    """
    provider: Optional[str] = None  # 'auto' or explicit provider id
    capability: Optional[str] = None  # e.g., 'prediction', 'training'
    training: Optional[str] = None  # 'auto' or config
    entries: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AgentContextBlock(ASTNode):
    """
    Represents the context and security constraints of an agent.

    Attributes:
        allow_functions (List[str]): Functions the agent is allowed to call.
        allow_classes (List[str]): Classes the agent is allowed to instantiate.
        deny (List[str]): Explicitly denied entities.
        allow_tokens (List[str]): Tokens allowed for the agent's context.
    """
    allow_functions: List[str] = field(default_factory=list)
    allow_classes: List[str] = field(default_factory=list)
    deny: List[str] = field(default_factory=list)
    allow_tokens: List[str] = field(default_factory=list)


@dataclass(kw_only=True)
class AgentExecutionBlock(ASTNode):
    """
    Represents the execution strategy of an agent.

    Attributes:
        async_exec (bool): Whether the agent executes asynchronously.
        cache_context (bool): Whether to cache the agent's context.
        entries (Dict[str, Any]): Additional execution settings.
    """
    async_exec: bool = False
    cache_context: bool = True
    entries: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AgentAuthenticationBlock(ASTNode):
    """
    Represents authentication and security settings for an agent endpoint.

    Attributes:
        token (Optional[str]): Authentication token or secret.
        token_source (Optional[str]): Source of the token ('static' or 'env').
        location (Optional[str]): Where the token is expected ('header', 'query', etc.).
        key (Optional[str]): The field name for the token.
        cors_enabled (bool): Whether CORS is enabled.
        cors_origins (List[str]): Allowed CORS origins.
        rate_limit_enabled (bool): Whether rate limiting is active.
        requests_per_minute (int): Rate limit threshold.
        burst_limit (int): Maximum burst size for requests.
        block_on_failure (bool): Whether to block IPs after multiple failures.
        max_failures (int): Failure threshold before blocking.
        block_duration_minutes (int): How long an IP remains blocked.
        whitelist_ips (List[str]): Explicitly allowed IP addresses.
        blacklist_ips (List[str]): Explicitly blocked IP addresses.
    """
    # Token configuration
    token: Optional[str] = None  # static token or env var name
    token_source: Optional[str] = None  # 'static' or 'env'

    # Location configuration
    location: Optional[str] = None  # 'header', 'query', 'body'
    key: Optional[str] = None  # key name like 'Authorization' or 'api_key'

    # CORS configuration
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)

    # Rate limiting configuration
    rate_limit_enabled: bool = False
    requests_per_minute: int = 60
    burst_limit: int = 10

    # Security configuration
    block_on_failure: bool = False
    max_failures: int = 5
    block_duration_minutes: int = 15
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)
    entries: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AgentResourcesBlock(ASTNode):
    """
    Represents resource allocations for an agent.

    Attributes:
        entries (Dict[str, Any]): Resource settings (e.g., CPU, memory).
    """
    entries: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AgentObservabilityBlock(ASTNode):
    """
    Represents monitoring and logging configuration for an agent.

    Attributes:
        stream (bool): Whether to stream observability data.
        entries (Dict[str, Any]): Additional observability settings.
    """
    stream: bool = False
    entries: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AgentDefinition(ASTNode):
    """
    Represents the definition of an agent, encompassing its intelligence,
    context, execution, authentication, and other properties.

    Attributes:
        name (str): The name of the agent.
        intelligence (Optional[AgentIntelligenceBlock]): Intelligence configuration.
        context (Optional[AgentContextBlock]): Security and context constraints.
        execution (Optional[AgentExecutionBlock]): Execution strategy.
        authentication (Optional[AgentAuthenticationBlock]): Authentication settings.
        resources (Optional[AgentResourcesBlock]): Resource allocations.
        observability (Optional[AgentObservabilityBlock]): Monitoring configuration.
        permissions (Optional[Dict[str, Any]]): Explicit permission settings.
        hallucination (Optional[Dict[str, Any]]): Hallucination control settings.
        docstring (Optional[str]): An optional docstring for the agent.
    """
    name: str
    intelligence: Optional[AgentIntelligenceBlock] = None
    context: Optional[AgentContextBlock] = None
    execution: Optional[AgentExecutionBlock] = None
    authentication: Optional[AgentAuthenticationBlock] = None
    resources: Optional[AgentResourcesBlock] = None
    observability: Optional[AgentObservabilityBlock] = None
    permissions: Optional[Dict[str, Any]] = None
    hallucination: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None


@dataclass(kw_only=True)
class AgentTrain(ASTNode):
    """
    Represents an instruction to train an agent.

    Attributes:
        agent_name (str): The name of the agent to train.
        dataset_source (Optional[DatasetOperation]): The source dataset for training.
        params (Dict[str, Any]): Training parameters.
    """
    agent_name: str
    dataset_source: Optional[DatasetOperation] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AgentEmbed(ASTNode):
    """
    Represents an instruction to generate embeddings using an agent.

    Attributes:
        agent_name (str): The name of the agent.
        items (Optional[list]): The items to embed.
    """
    agent_name: str
    items: Optional[list] = None


@dataclass(kw_only=True)
class AgentPredict(ASTNode):
    """
    Represents an instruction to perform a prediction using an agent.

    Attributes:
        agent_name (str): The name of the agent.
        input_data (Optional[Any]): The input data for prediction.
    """
    agent_name: str
    input_data: Optional[Any] = None


@dataclass(kw_only=True)
class AgentShutdown(ASTNode):
    """
    Represents an instruction to shut down an agent.

    Attributes:
        agent_name (str): The name of the agent to shut down.
    """
    agent_name: str


@dataclass(kw_only=True)
class AgentRun(ASTNode):
    """
    Represents an instruction to run an agent task.

    Attributes:
        agent_name (str): The name of the agent.
        args (Dict[str, Any]): Arguments for the run operation.
    """
    agent_name: str
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class Ternary(ASTNode):
    """
    Represents a ternary conditional expression (e.g., `condition ? true_expr : false_expr`).

    Attributes:
        condition (ASTNode): The condition expression.
        true_expr (ASTNode): Expression to evaluate if true.
        false_expr (ASTNode): Expression to evaluate if false.
    """
    condition: ASTNode
    true_expr: ASTNode
    false_expr: ASTNode


@dataclass(kw_only=True)
class LoopStatement(ASTNode):
    """
    Represents a specialized loop statement for agents or adapters.

    Attributes:
        adapter (Optional[str]): The adapter being used for the loop (e.g., 'stdin').
        agent_names (Optional[list]): List of agents involved in the loop.
        body (List[ASTNode]): The sequence of statements in the loop body.
    """
    adapter: Optional[str] = None
    agent_names: Optional[list] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass(kw_only=True)
class ServeStatement(ASTNode):
    """
    Represents a statement to start a service/server.

    Attributes:
        adapter (str): The server adapter (e.g., 'http', 'grpc').
        port (Optional[int]): The port number to listen on.
        host (Optional[str]): The host address to bind to.
        name (Optional[str]): The name of the service.
        agent_names (Optional[list]): List of agents exposed by the service.
        blocking (bool): Whether the server should block execution.
    """
    adapter: str
    port: Optional[int] = None
    host: Optional[str] = None
    name: Optional[str] = None
    agent_names: Optional[list] = None  # list of allowed agent names
    blocking: bool = False


@dataclass(kw_only=True)
class StopStatement(ASTNode):
    """
    Represents an instruction to stop a service or process.

    Attributes:
        target (str): The identifier of the target to stop.
    """
    target: str


@dataclass(kw_only=True)
class AwaitStatement(ASTNode):
    """
    Represents a statement-level await.

    Attributes:
        target (str): The identifier or task to wait for.
    """
    target: str


# --- ORM/DB/Migrations extension nodes ---
@dataclass(kw_only=True)
class ModelField(ASTNode):
    """
    Represents a field definition within a database model.

    Attributes:
        name (str): The name of the field.
        type_annotation (Optional[str]): The data type of the field.
        default (Optional[ASTNode]): The default value.
        constraints (Optional[Dict[str, Any]]): Field constraints (e.g., unique, nullable).
    """
    name: str
    type_annotation: Optional[str]
    default: Optional[ASTNode] = None
    constraints: Optional[Dict[str, Any]] = None  # nullable, unique, index, pk, check, etc.


@dataclass(kw_only=True)
class RelationDeclaration(ASTNode):
    """
    Represents a relationship between database models.

    Attributes:
        kind (str): The type of relationship (e.g., OneToOne, OneToMany, ManyToMany).
        target (str): The target model name.
        options (Optional[Dict[str, Any]]): Additional options for the relation.
    """
    kind: str  # OneToOne, OneToMany, ManyToMany
    target: str
    options: Optional[Dict[str, Any]] = None  # backref, through, on_delete, etc.


@dataclass(kw_only=True)
class ModelDeclaration(ASTNode):
    """
    Represents a database model declaration.

    Attributes:
        name (str): The name of the model.
        fields (List[Union[ModelField, RelationDeclaration]]): Fields and relations.
        docstring (Optional[str]): An optional docstring for the model.
    """
    name: str
    fields: List[Union[ModelField, RelationDeclaration]]
    docstring: Optional[str] = None


@dataclass(kw_only=True)
class MigrationOperation(ASTNode):
    """
    Represents an operation within a database migration.

    Attributes:
        op (str): The operation name (e.g., 'create_table', 'add_column').
        args (Dict[str, Any]): Arguments for the migration operation.
    """
    op: str
    args: Dict[str, Any]


@dataclass(kw_only=True)
class MigrationDeclaration(ASTNode):
    """
    Represents a database migration definition.

    Attributes:
        name (str): The name of the migration.
        up (List[MigrationOperation]): Operations to apply the migration.
        down (Optional[List[MigrationOperation]]): Operations to revert the migration.
        docstring (Optional[str]): An optional docstring for the migration.
    """
    name: str
    up: List[MigrationOperation]
    down: Optional[List[MigrationOperation]] = None
    docstring: Optional[str] = None


__all__ = [
    "ASTNode",
    "Program",
    "VarDeclaration",
    "FunctionDeclaration",
    "MethodDeclaration",
    "FieldDeclaration",
    "ClassDeclaration",
    "InterfaceDeclaration",
    "ContractDeclaration",
    "Assignment",
    "JsonObject",
    "JsonArray",
    "NullLiteral",
    "ImportDeclaration",
    "FromImportDeclaration",
    "Await",
    "BinaryOp",
    "UnaryOp",
    "FunctionCall",
    "CallArgument",
    "PropertyAccess",
    "IndexAccess",
    "NewExpression",
    "ThisExpression",
    "SuperExpression",
    "LambdaExpression",
    "IfStatement",
    "WhileStatement",
    "ForStatement",
    "ForInStatement",
    "ForOfStatement",
    "CatchClause",
    "TryStatement",
    "ThrowStatement",
    "ReturnStatement",
    "BreakStatement",
    "ContinueStatement",
    "Literal",
    "Identifier",
    "GenericIdentifier",
    "TypeAnnotation",
    "DatasetOperation",
    "ModelOperation",
    "ModelArgument",
    "ModelConfigBlock",
    "GenericTypeExpression",
    "Ternary",
    "InterpolatedString",
    "ModelField",
    "RelationDeclaration",
    "ModelDeclaration",
    "MigrationOperation",
    "MigrationDeclaration",
    "AgentDefinition",
    "AgentTrain",
    "AgentContextBlock",
    "AgentRun",
    "AgentEmbed",
    "AgentPredict",
    "AgentShutdown",
    "AgentAuthenticationBlock",
    "AgentExecutionBlock",
    "AgentIntelligenceBlock",
    "AgentResourcesBlock",
    "AgentObservabilityBlock",
    "AwaitStatement",
    "LoopStatement",
    "ServeStatement",
    "StopStatement",
    "WithStatement",
    "WithItem"
]
