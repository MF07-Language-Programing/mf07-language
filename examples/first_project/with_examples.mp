# Mini Sistema de Configuração com JSON e .env
# Demonstra: leitura/escrita de arquivos, parsing JSON, variáveis de ambiente, validação

class ConfigManager {
    var configPath: string
    var envPath: string
    var config: dict
    var env: dict
    
    intent __init__(rootDir: string) {
        # Usar concatenação de paths com f-string
        this.configPath = f"{rootDir}/config.json"
        this.envPath = f"{rootDir}/.env"
        this.config = {}
        this.env = {}
    }
    
    # Criar configuração padrão
    async intent createDefaultConfig() {
        var defaultConfig = {
            "app": {
                "name": "MiniSystem",
                "version": "1.0.0",
                "debug": false
            },
            "database": {
                "host": "${DB_HOST}",
                "port": "${DB_PORT}",
                "name": "${DB_NAME}",
                "pool_size": 10
            },
            "api": {
                "base_url": "${API_URL}",
                "timeout": 30,
                "retry_count": 3
            },
            "features": {
                "enable_cache": true,
                "enable_logging": true,
                "max_upload_size": 10485760
            }
        }
        
        try {
            with open(this.configPath, "w") as f {
                var jsonString = JSON.stringify(defaultConfig, indent=2)
                await f.writeText(jsonString, null)
            }
            
            print(f"✓ Config padrão criado: {this.configPath}")
        } catch (e: Exception) {
            print(f"ERRO ao criar config: {e}")
            print(f"ERRO tipo: {type(e)}")
            throw e
        }
        
        return defaultConfig
    }
    
    # Criar arquivo .env padrão
    async intent createDefaultEnv() {
        var envContent = "# Database Configuration\nDB_HOST=localhost\nDB_PORT=5432\nDB_NAME=minisystem_db\n\n# API Configuration\nAPI_URL=https://api.example.com\nAPI_KEY=your_secret_key_here\n\n# Environment\nENV=development\nLOG_LEVEL=debug\n"
        
        with open(this.envPath, "w") as f {
            await f.writeText(envContent, null)
        }
        
        print(f"✓ Arquivo .env criado: {this.envPath}")
    }
    
    # Carregar variáveis do .env
    async intent loadEnv() {
        try {
            with open(this.envPath, "r") as f {
                var content = await f.readText("")
                
                # Parse simples: dividir em linhas e processar
                var normalized = content.replace("\r\n", "\n").replace("\r", "\n")
                var parts = normalized.split("\n")
                
                for (var line in parts) {
                    # Ignorar comentários e linhas vazias
                    if (type(line) == "string" and line != "" and not line.startsWith("#")) {
                        if (line.contains("=")) {
                            var eqPos = line.indexOf("=")
                            if (eqPos > 0) {
                                var k = line.substring(0, eqPos)
                                var v = line.substring(eqPos + 1, len(line))
                                this.env[k] = v
                            }
                        }
                    }
                }
            }
            
            print(f"✓ Variáveis de ambiente carregadas: {len(this.env.keys())} vars")
            return true
        } catch (e: Exception) {
            print(f"✗ Erro ao carregar .env: {e}")
            return false
        }
    }
    
    # Carregar e interpolar configuração JSON
    async intent loadConfig() {
        try {
            with open(this.configPath, "r") as f {
                var content = await f.readText("")
                this.config = JSON.parse(content)
            }
            
            # Interpolar variáveis de ambiente
            this.config = this._interpolateEnvVars(this.config)
            
            print(f"✓ Configuração carregada e interpolada")
            return this.config
        } catch (e: Exception) {
            print(f"✗ Erro ao carregar config: {e}")
            return null
        }
    }
    
    # Interpolar ${VAR} com valores do .env
    intent _interpolateEnvVars(obj) {
        if (type(obj) == "string") {
            # Substituir ${VAR} por valor do env
            var result = obj
            for (var key in this.env.keys()) {
                var placeholder = f"${{{key}}}"
                if (result.contains(placeholder)) {
                    result = result.replace(placeholder, this.env[key])
                }
            }
            return result
        } else if (type(obj) == "dict") {
            var newDict = {}
            for (var key in obj.keys()) {
                newDict[key] = this._interpolateEnvVars(obj[key])
            }
            return newDict
        } else if (type(obj) == "list") {
            var newList = []
            for (var item in obj) {
                newList.append(this._interpolateEnvVars(item))
            }
            return newList
        } else {
            return obj
        }
    }
    
    # Obter valor de configuração por caminho (ex: "database.host")
    intent get(path: string) {
        var parts = path.split(".")
        var current = this.config
        
        for (var part in parts) {
            if (type(current) == "dict" and current.hasKey(part)) {
                current = current[part]
            } else {
                return null
            }
        }
        
        return current
    }
    
    # Atualizar configuração e salvar
    async intent set(path: string, value) {
        var parts = path.split(".")
        var current = this.config
        
        # Navegar até o penúltimo nível
        for (var i = 0; i < len(parts) - 1; i = i + 1) {
            var part = parts[i]
            if (not current.hasKey(part)) {
                current[part] = {}
            }
            current = current[part]
        }
        
        # Definir o valor
        current[parts[len(parts) - 1]] = value
        
        # Salvar no arquivo
        with open(this.configPath, "w") as f {
            var jsonString = JSON.stringify(this.config, indent=2)
            await f.writeText(jsonString, null)
        }
        
        print(f"✓ Configuração atualizada: {path} = {value}")
    }
    
    # Validar configuração
    intent validate() {
        var errors = []
        
        # Verificar se config foi carregado
        if (this.config == null or type(this.config) != "dict") {
            errors.append("Configuração não foi carregada")
            return {
                "valid": false,
                "errors": errors
            }
        }
        
        # Validar campos obrigatórios
        if (not this.config.hasKey("app")) {
            errors.append("Campo 'app' é obrigatório")
        }
        
        if (not this.config.hasKey("database")) {
            errors.append("Campo 'database' é obrigatório")
        } else {
            var db = this.config["database"]
            if (not db.hasKey("host") or db["host"] == "") {
                errors.append("database.host não pode ser vazio")
            }
            if (not db.hasKey("port")) {
                errors.append("database.port é obrigatório")
            }
        }
        
        # Validar tipos
        if (this.config.hasKey("features")) {
            var features = this.config["features"]
            if (features.hasKey("max_upload_size")) {
                if (type(features["max_upload_size"]) != "int") {
                    errors.append("features.max_upload_size deve ser um número")
                }
            }
        }
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    }
    
    # Exibir configuração atual
    intent display() {
        print("\n=== CONFIGURAÇÃO ATUAL ===")
        print(JSON.stringify(this.config, indent=2))
        print("\n=== VARIÁVEIS DE AMBIENTE ===")
        for (var key in this.env.keys()) {
            var value = this.env[key]
            # Mascarar valores sensíveis
            if (key.contains("KEY") or key.contains("SECRET") or key.contains("PASSWORD")) {
                value = "***HIDDEN***"
            }
            print(f"{key}: {value}")
        }
    }
}

# Sistema principal
async intent main() {
    print("🚀 Mini Sistema de Configuração\n")
    
    # Setup
    var root = Path.join(Path.cwd(), "tests", "config_system")
    var workdir = new Directory(root)
    if (not workdir.exists()) {
        workdir.ensure()
        print(f"✓ Diretório criado: {root}\n")
    }
    
    var configMgr = new ConfigManager(root)
    
    # 1. Criar arquivos de configuração
    print("📝 Etapa 1: Criando arquivos de configuração...")
    await configMgr.createDefaultConfig()
    await configMgr.createDefaultEnv()
    
    # 2. Carregar variáveis de ambiente
    print("\n📝 Etapa 2: Carregando variáveis de ambiente...")
    await configMgr.loadEnv()
    
    # 3. Carregar e interpolar configuração
    print("\n📝 Etapa 3: Carregando configuração...")
    var config = await configMgr.loadConfig()
    
    # 4. Validar configuração
    print("\n📝 Etapa 4: Validando configuração...")
    var validation = configMgr.validate()
    if (validation["valid"]) {
        print("✓ Configuração válida!")
    } else {
        print("✗ Erros encontrados:")
        for (var error in validation["errors"]) {
            print(f"  - {error}")
        }
    }
    
    # 5. Acessar valores específicos
    print("\n📝 Etapa 5: Acessando valores...")
    print(f"App Name: {configMgr.get('app.name')}")
    print(f"Database Host: {configMgr.get('database.host')}")
    print(f"Database Port: {configMgr.get('database.port')}")
    print(f"API URL: {configMgr.get('api.base_url')}")
    print(f"Cache Enabled: {configMgr.get('features.enable_cache')}")
    
    # 6. Atualizar configuração
    print("\n📝 Etapa 6: Atualizando configuração...")
    await configMgr.set("app.debug", true)
    await configMgr.set("features.max_upload_size", 20971520)
    
    # 7. Recarregar e exibir
    print("\n📝 Etapa 7: Recarregando configuração atualizada...")
    await configMgr.loadConfig()
    configMgr.display()
    
    print("\n✅ Sistema de configuração concluído!")
}

print("=" * 60)
await main()
print("=" * 60)
