intent calculate_tax(amount) {
    return amount * 0.2;
}

agent MyAgent {
    intelligence { provider local }
    context { 
        allow intent calculate_tax
    }
    execution { interactive true }
    authentication {
        token { value "secret123" }
        location { type header, key "Authorization" }
        cors { enabled true, origins ["http://localhost:3000", "https://myapp.com"] }
    }
}

agent ApiAgent {
    intelligence { provider api }
    context { allow intent calculate_tax }
    execution { interactive true }
}

# Train MyAgent (dataset auto-generated or provided by 'on')
agent train MyAgent on dataset0;
waitSeconds(0.5);
print("-- after train --");

# Generate embeddings for some items
agent embed MyAgent with { items: ["doctext one", "doctext two"] };
print("-- after embed --");

# Predict using agent
agent predict MyAgent with { text: "Is this good?" };
print("-- after predict --");

# Start HTTP server to expose agent
serve http port 8360 name myagentserver using MyAgent;
print("-- after serve --");
# Example: test agent interaction with authentication
waitSeconds(0.8);
var resp = mf.http.request({"method": "POST", "url": "http://127.0.0.1:8360/interact/MyAgent", "json": {"input": "test message"}, "headers": {"Authorization": "secret123"}});
print("interact resp:", resp);
print("-- after interact --");

# Example: test agent interaction without token (should fail)
var resp_fail = mf.http.request({"method": "POST", "url": "http://127.0.0.1:8360/interact/MyAgent", "json": {"input": "test message"}});
print("interact resp (no auth):", resp_fail);
print("-- after interact fail --");

# Shutdown server (with auth)
var resp_shutdown = mf.http.request({"method": "POST", "url": "http://127.0.0.1:8360/interact/MyAgent/shutdown", "json": {"input": "shutdown"}, "headers": {"Authorization": "secret123"}});
print("shutdown resp (with auth):", resp_shutdown);
print("-- after shutdown with auth --");
