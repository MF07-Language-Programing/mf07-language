# Mini Sistema de Configuração Simplificado com JSON e .env

async intent main() {
    print("🚀 Mini Sistema de Configuração\n")
    
    # Setup diretório
    var root = f"{Path.cwd()}/tests/config_demo"
    var workdir = new Directory(root)
    if (not workdir.exists()) {
        workdir.ensure()
    }
    
    # 1. Criar configuração JSON
    print("📝 Etapa 1: Criando config.json...")
    var config = {
        "app": {
            "name": "MiniSystem",
            "version": "1.0.0",
            "debug": false
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "minisystem_db"
        },
        "features": {
            "cache_enabled": true,
            "max_upload_mb": 10
        }
    }
    
    var configPath = f"{root}/config.json"
    with open(configPath, "w") as f {
        var jsonStr = JSON.stringify(config, indent=2)
        await f.writeText(jsonStr, null)
    }
    print(f"✓ Config salvo em: {configPath}")
    
    # 2. Criar arquivo .env
    print("\n📝 Etapa 2: Criando .env...")
    var envPath = f"{root}/.env"
    var envContent = "# Database\nDB_HOST=localhost\nDB_PORT=5432\n\n# App\nAPP_ENV=development\nDEBUG=true\n"
    with open(envPath, "w") as f {
        await f.writeText(envContent, null)
    }
    print(f"✓ .env salvo em: {envPath}")
    
    # 3. Ler configuração
    print("\n📝 Etapa 3: Lendo config.json...")
    with open(configPath, "r") as f {
        var content = await f.readText("")
        var loadedConfig = JSON.parse(content)
        print("✓ Configuração carregada:")
        print(JSON.stringify(loadedConfig, indent=2))
    }
    
    # 4. Ler variáveis .env
    print("\n📝 Etapa 4: Lendo .env...")
    var envVars = {}
    with open(envPath, "r") as f {
        var envLines = await f.readText("")
        print(f"✓ Variáveis de ambiente carregadas")
        print(envLines)
    }
    
    # 5. Demonstrar uso de break em loop
    print("\n📝 Etapa 5: Testando break em while...")
    var count = 0
    while (count < 100) {
        count = count + 1
        if (count == 5) {
            print(f"✓ Break funcionou! Saindo no count={count}")
            break
        }
    }
    
    print("\n✅ Sistema de configuração concluído com sucesso!")
}

print("=" * 60)
await main()
print("=" * 60)
