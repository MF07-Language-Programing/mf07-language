# Tutorial 4 — Agente no Console (20 min)

Objetivo: criar um agente de conversa simples que usa regras locais (sem modelo externo) para responder comandos básicos.

## 1) Projeto
```bash
mf init console-agent
cd console-agent
```

## 2) `main.mp`
```
fn respond(input) {
  let t = text.lower(input)
  if text.contains(t, "hora") { return "Agora: " + sys.time() }
  if text.contains(t, "data") { return "Hoje: " + sys.date() }
  if text.contains(t, "ajuda") { return "Comandos: hora, data, sair" }
  return "Não entendi. Digite 'ajuda'."
}

while true {
  print("> ")
  let line = sys.read_line()
  if line == null || text.lower(line) == "sair" { break }
  println(respond(line))
}
```

## 3) Executar
```bash
mf run main.mp
```

## 4) Próximos passos
- Plugins para comandos
- Persistência de contexto
- Integração HTTP
