# Mini Sistema com JSON e File I/O

async intent main() {
    print("=" * 60)
    print("🚀 Mini Sistema de Configuração CorpLang")
    print("=" * 60)
    
    # 1. Criar JSON
    print("\n📝 Etapa 1: Criando estrutura JSON...")
    var config = {
        "app": {
            "name": "CorpSystem",
            "version": "1.0.0"
        },
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }
    print("✓ JSON criado com sucesso")
    
    # 2. Converter para string com indent
    print("\n📝 Etapa 2: Formatando JSON com indent=2...")
    var jsonString = JSON.stringify(config, indent=2)
    print(jsonString)
    
    # 3. Salvar em arquivo
    print("\n📝 Etapa 3: Salvando JSON em arquivo...")
    var filePath = "test_config.json"
    with open(filePath, "w") as f {
        await f.writeText(jsonString, null)
    }
    print(f"✓ JSON salvo em: {filePath}")
    
    # 4. Ler arquivo
    print("\n📝 Etapa 4: Lendo arquivo de volta...")
    with open(filePath, "r") as f {
        var content = await f.readText("")
        var loaded = JSON.parse(content)
        print(f"✓ Config carregada: {loaded['app']['name']}")
    }
    
    # 5. Split test
    print("\n📝 Etapa 5: Testando split() em string...")
    var text = "DB_HOST=localhost\nDB_PORT=5432\nDB_NAME=test"
    var lines = text.split("\n")
    print(f"✓ Split retornou {type(lines)} com items:")
    for (var line in lines) {
        print(f"  - {line}")
    }
    
    print("\n" + "=" * 60)
    print("✅ Todos os testes completados com sucesso!")
    print("=" * 60)
}

await main()
