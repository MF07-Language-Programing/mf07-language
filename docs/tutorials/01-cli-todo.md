# Tutorial 1 — CLI To‑Do (15 min)

Objetivo: construir um gerenciador de tarefas simples via CLI usando Corplang, cobrindo I/O, listas e persistência em JSON.

## 1) Criar projeto
```bash
mf init todo-cli
cd todo-cli
```

## 2) Arquivo principal
Crie `main.mp`:

```
fn load_tasks(path) {
  let exists = file.exists(path)
  if !exists { return [] }
  let content = file.read(path)
  return json.parse(content)
}

fn save_tasks(path, tasks) {
  file.write(path, json.stringify(tasks, pretty=true))
}

fn add(tasks, text) {
  return tasks + [{ id: uuid.v4(), text: text, done: false }]
}

fn list(tasks) {
  for t in tasks { println((t.done ? "[x]" : "[ ]") + " " + t.text) }
}

fn done(tasks, text) {
  return map tasks as t -> (t.text == text ? { ...t, done: true } : t)
}

fn remove(tasks, text) {
  return filter tasks as t -> (t.text != text)
}

let store = "tasks.json"
let args = sys.args()
let cmd = args.get(1, "help")
let tasks = load_tasks(store)

if cmd == "add" {
  let text = args.get(2, "")
  if text == "" { println("usage: mf run main.mp add <text>"); exit(1) }
  tasks = add(tasks, text)
  save_tasks(store, tasks)
  println("added: " + text)
} elif cmd == "list" {
  list(tasks)
} elif cmd == "done" {
  let text = args.get(2, "")
  tasks = done(tasks, text)
  save_tasks(store, tasks)
  println("done: " + text)
} elif cmd == "rm" {
  let text = args.get(2, "")
  tasks = remove(tasks, text)
  save_tasks(store, tasks)
  println("removed: " + text)
} else {
  println("commands: add|list|done|rm")
}
```

## 3) Executar
```bash
mf run main.mp add "Estudar Corplang"
mf run main.mp list
```

## 4) Próximos passos
- Ordenação por data
- Marcar/desmarcar toggle
- Exportar CSV
