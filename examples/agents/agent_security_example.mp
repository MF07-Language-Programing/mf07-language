
intent test_command(){

}


intent test_command2(){

}


agent MySecureAgent {
    intelligence {
        provider "auto"
        capability "prediction"
    }

    context {
        allow intent test_command
        allow intent test_command2
        allow class User
    }

    execution {
        async false
        cache_context true
    }

    authentication {
        token {
            value "supersecret123"
        }
        location {
            type "header"
            key "Authorization"
        }
        cors {
            enabled true
            origins ["http://localhost:3000", "https://myapp.com"]
        }
        rate_limit {
            enabled true
            requests_per_minute 100
            burst_limit 300
        }
        security {
            block_on_failure true
            max_failures 3
            block_duration_minutes 5
            whitelist_ips ["127.0.0.1", "192.168.1.0/24"]
            blacklist_ips ["10.0.0.1"]
        }
    }
}

# Train the agent
agent train MySecureAgent;

print("-- Agent trained with advanced security --");

# Serve the agent with security features
serve http port 8361 name secureagentserver using MySecureAgent;

print("-- Secure agent server started on port 8361 --");
print("-- Features enabled: Rate limiting (10/min, burst 3), IP security (whitelist, blacklist), failure blocking --");

# Test interaction with valid auth
waitSeconds(0.5);
var resp = mf.http.request({
    "method": "POST",
    "url": "http://127.0.0.1:8361/interact/MySecureAgent",
    "json": {"input": "Hello secure agent"},
    "headers": {"Authorization": "supersecret123"}
});
print("Secure interaction response:", resp);

# Test rate limiting - make multiple requests quickly
print("-- Testing rate limiting --");
var i = 0;
while (i < 5) {
    var rate_resp = mf.http.request({
        "method": "POST",
        "url": "http://127.0.0.1:8361/interact/MySecureAgent",
        "json": {"input": f"Rate limit test {i}"},
        "headers": {"Authorization": "supersecret123"}
    });
    print("Rate test", i, ":", rate_resp.status);
    i = i + 1;
    if i < 4 { waitSeconds(0.1); }  # Small delay between requests
    print(rate_resp.get("json"))
}

print("-- Test completed --");
# mf.http.request({"method": "POST", "url": "http://127.0.0.1:8361/interact/MyAgent/shutdown", "json": {"input": "shutdown"}, "headers": {"Authorization": "supersecret123"}});
