# Demo de conexao e ORM

from core.database import set_default_driver, set_default_config, connect, execute, disconnect, register_driver, InMemoryDriver
from core.map import Map
from core.orm import Field, Model, Relation, register_model


var logger = new Logger(LogLevel.INFO, "db_demo")

# Pequenos helpers para formatar registros e listas de forma legível
intent stringify_map(m: any): string {
    if (m == null) { return "<null>" }
    var keys = m.keys()
    if (keys == null) { return f"{m}" }
    var i = 0
    var parts = ""
    while (i < len(keys)) {
        var k = keys[i]
        var v = m.get(k)
        parts = parts + k + "=" + f"{v}"
        if (i < len(keys) - 1) {
            parts = parts + ", "
        }
        i = i + 1
    }
    return "{ " + parts + " }"
}

intent stringify_list(lst: any): string {
    if (lst == null) { return "[]" }
    var i = 0
    var parts = "["
    while (i < len(lst)) {
        parts = parts + stringify_map(lst[i])
        if (i < len(lst) - 1) {
            parts = parts + ", "
        }
        i = i + 1
    }
    parts = parts + "]"
    return parts
}

# Configura driver padrao (usar in-memory) e conecta
intent main() {
    try {
        logger.info("start demo")
        register_driver("memory", new InMemoryDriver())
        logger.info("driver registered")
        set_default_driver("memory")
        logger.info("default driver set")
        var default_cfg = new Map<string, any>()
        logger.info("default_cfg created")
        default_cfg.put("dsn", "memory")
        logger.info("default_cfg populated")
        set_default_config(default_cfg)
        logger.info("config applied")
        connect(new Map<string, any>())
        logger.info("connected")

        # Definicao simples de modelo User
        var user_fields = new Map<string, Field>()
        user_fields.put("id", new Field("int", nullable=false, pk=true))
        user_fields.put("name", new Field("string", nullable=false))
        user_fields.put("email", new Field("string", nullable=false, unique=true))

        logger.info("TESTE")
        logger.info(f"Relation={Relation}")
        var user_relations = new Map<string, Relation>()
        register_model("User", user_fields, user_relations)
        logger.info("model registered")

        # Cria tabela (opcional; insert tambem cria no driver in-memory)
        var empty_params = new List<any>()
        # Use the same table identifier as the model name to avoid missing-key errors in the in-memory driver
        execute("create table User", empty_params)
        logger.info("table created")

        # Usa QuerySet do ORM
        var qs = Model.queryset_for("User")
        logger.info("queryset ready")
        var created_values = new Map<string, any>()
        created_values.put("id", 1)
        created_values.put("name", "Alice")
        created_values.put("email", "alice@example.com")
        var created = qs.create(created_values)
        logger.info("=== Created user ===")
        logger.info(stringify_map(created))

        var all_users = qs.filter(new Map<string, any>())
        logger.info("=== All users ===")
        logger.info(stringify_list(all_users))

        var criteria = new Map<string, any>()
        criteria.put("id", 1)
        var first = qs.get(criteria)
        logger.info("=== First user ===")
        logger.info(stringify_map(first))

        disconnect()
    } catch (err: Exception) {
        logger.error("demo error:")
        logger.error(err)
        logger.error(f"message.type={type(err.message)}")
        logger.error(f"message.value={err.message}")
    }
}

await main()
