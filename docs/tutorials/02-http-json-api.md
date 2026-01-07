# Tutorial 2 — HTTP JSON API (25 min)

Objetivo: criar uma API REST mínima para tarefas utilizando o módulo HTTP da stdlib.

Pré‑requisitos: `mf versions set <versão>` ativo.

## 1) Projeto
```bash
mf init todo-api
cd todo-api
```

## 2) `main.mp`
```
let store = "tasks.json"

fn load() { let ok = file.exists(store); return ok ? json.parse(file.read(store)) : [] }
fn save(t) { file.write(store, json.stringify(t, pretty=true)) }

fn route(method, path, body) {
  let tasks = load()
  if method == "GET" && path == "/tasks" { return { status: 200, json: tasks } }
  if method == "POST" && path == "/tasks" {
    let data = json.parse(body)
    let task = { id: uuid.v4(), text: data.text, done: false }
    save(tasks + [task])
    return { status: 201, json: task }
  }
  if method == "PATCH" && path.startsWith("/tasks/") {
    let id = path.split("/").last()
    let data = json.parse(body)
    let next = map tasks as t -> (t.id == id ? { ...t, ...data } : t)
    save(next)
    return { status: 200, json: { ok: true } }
  }
  if method == "DELETE" && path.startsWith("/tasks/") {
    let id = path.split("/").last()
    let next = filter tasks as t -> (t.id != id)
    save(next)
    return { status: 204 }
  }
  return { status: 404, json: { error: "not found" } }
}

http.listen(8080, (req) -> {
  let res = route(req.method, req.path, req.body)
  http.json(res.status, res.json)
})
```

## 3) Rodar e testar
```bash
mf run main.mp &
curl -s http://localhost:8080/tasks | jq
curl -s -X POST http://localhost:8080/tasks -d '{"text":"Aprender HTTP"}' | jq
```

## 4) Próximos passos
- Paginação e filtros
- Validação de payloads
- Middleware de logs
