intent calculate_tax(amount) {
    return amount * 0.2;
}

class User {

    var name: string

    intent constructor(name: string){
        this.name = name;
    }

}

class UserGroup {

    var name: string
    var permissions: List<string>

    intent constructor(name: string, permissions: List<string>){
        this.name = name;
        this.permissions = permissions
    }

}


agent HttpAssistant {
    intelligence { provider nltk }  // Agora com instalação automática
    context { 
        allow intent calculate_tax 
        allow class User 
        allow class UserGroup 
    }
    resources {
        tracking_enabled true
        max_resources 100
        dynamic_execution true
        variable_modification true
        function_execution true
        class_creation true
    }
    observability {
        stream true
        log_level "debug"
    }
    execution { interactive true }
}

agent Counch {
    intelligence { provider nltk }
    context { 
        allow intent calculate_tax 
    }
    resources {
        tracking_enabled false
    }
    observability {
        stream false
    }
    execution { interactive true }
}

# Start an HTTP server named 'http1' on port 8300 using HttpAssistant and block until it stops
serve http port 8300 name http1 using HttpAssistant, Counch blocking;

# new User("Lucas")
# new UserGroup("Ler Diretório", ["read_dir"])

# Alternatively: start non-blocking and await separately
# serve http port 8301 name http2 using HttpAssistant;
# await http2;
