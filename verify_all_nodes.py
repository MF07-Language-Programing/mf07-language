from src.corplang.compiler.lexer import Lexer
from src.corplang.compiler.parser import Parser
import sys

code = """
# import sys;
# from os import path;
# 
# # Test Type Annotations & Generic identifiers
# var list: List<str> = ["a", "b"];
# var map: Map<str, int> = {"key": 10};
# 
# # Test Agents
# agent MyAgent {
#     intelligence {
#         provider: "openai"
#         capability: "vision"
#         model: "gpt-4"
#     }
#     context {
#         allow: "read_file"
#         deny: ["rm", "rf"]
#     }
#     execution {
#         async: true
#         timeout: 30
#     }
# }
# 
# agent train MyAgent with { source: "data.csv" };
# agent run MyAgent(task="process");
# agent predict MyAgent("hello");
# stop MyAgent;
# 
# # Test OOP
# class Base<T> {
#     var id: int = 1;
# }
# 
# class MyClass extends Base<T> implements IRunnable {
#     private static var count: int = 0;
#     
#     intent constructor(name: str){
#     }
#     
#     async intent start(name: str): void {
#         await this.id;
#     }
# }
# 
# interface IRunnable {
#     intent run(): void;
# }
# 
# # Test Loops and Control
# loop {
#     if (true) { break; }
# }
# 
# for (var x in [1, 2]) { print(x); }
# for (var y of {a: 1}) { print(y); }
# 
# with (open("file") as f) {
#     f.read();
# }
# 
# try {
#     throw Error("fail");
# } catch (e: Exception) {
#     print(e);
# } catch (e: CustomException) {
#     print(name="CustomName", e);
# } finally {
#     print("done");
# }

# Test DB/ORM
model User {
    id: int
    name: str
}

migration Initial {
    create_table(name="users", engine="innodb")
}

serve http port 8300 name http1 using HttpAssistant, Counch blocking;
"""

try:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_file="full_test.corp")
    program = parser.parse()
    
    print(f"Compilation Successful! Nodes created: {len(program.statements)}")
    
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

    check_parents(program)
    print(parser.as_view())
    print("Parent hierarchy check finished.")
    
except Exception as e:
    print(f"Compilation Failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
