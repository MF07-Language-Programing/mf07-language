# Tutorial 3 — CRUD com SQLite (30 min)

Objetivo: persistir tarefas em SQLite usando runtime de DB.

## 1) Projeto
```bash
mf init todo-db
cd todo-db
```

## 2) `main.mp`
```
import db

fn ensure_schema(conn) {
  db.exec(conn, "CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, text TEXT, done INTEGER)")
}

fn list(conn) { return db.query(conn, "SELECT id, text, done FROM tasks ORDER BY rowid DESC") }

fn add(conn, text) {
  let id = uuid.v4()
  db.exec(conn, "INSERT INTO tasks (id, text, done) VALUES (?, ?, 0)", [id, text])
  return id
}

fn set_done(conn, id, done) {
  db.exec(conn, "UPDATE tasks SET done = ? WHERE id = ?", [done ? 1 : 0, id])
}

let conn = db.connect("sqlite", "todo.db")
ensure_schema(conn)

let a = sys.args()
if a.get(1, "") == "add" { println(add(conn, a.get(2, ""))) }
elif a.get(1, "") == "list" { println(json.stringify(list(conn))) }
elif a.get(1, "") == "done" { set_done(conn, a.get(2, ""), true); println("ok") }
else { println("usage: add|list|done") }
```

## 3) Executar
```bash
mf run main.mp add "Banco de dados"
mf run main.mp list | jq
```

## 4) Próximos passos
- Índices e migrações
- Conexão com PostgreSQL
- Transações
