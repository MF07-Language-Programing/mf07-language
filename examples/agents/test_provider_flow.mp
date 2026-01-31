# Teste de integração: provider `placeholder` e execução de actions

# Define agente simples que usa o provider placeholder (registrado por padrão)
agent TestAgent {
    intelligence { provider placeholder }
    execution { interactive true }
}

intent main(name: Optional[str]) {
    print("Hello from TestAgent, name=", name);
    return "Response from TestAgent, name=" + (name if name != null else "<no name>");
}

# Predição usando a forma de chamada direta (string)
var resp1 = agent predict TestAgent("Mensagem de teste do .mp");
print("resp1:", resp1);

# Predição usando forma com objeto (map)
var resp2 = agent predict TestAgent with { text: "Outra mensagem de teste" };
print("resp2:", resp2);

# Execução do agente via `run` (PoC)
loop stdin using TestAgent
print("-- after run --");
