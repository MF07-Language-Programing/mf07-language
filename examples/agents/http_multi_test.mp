intent calculate_tax(amount) {
    return amount * 0.2;
}

agent HttpAssistant {
    intelligence { provider auto }
    context { allow intent calculate_tax }
    execution { interactive true }
}

agent Counch {
    intelligence { provider auto }
    context { allow intent calculate_tax }
    execution { interactive true }
}

# Start non-blocking with two agents
serve http port 8350 name httpmulti using HttpAssistant, Counch;
waitSeconds(0.2);

print("POST to Counch...");
var r1 = mf.http.post("http://127.0.0.1:8350/interact/Counch", {"input":"describe"});
print("Counch resp:", r1);

print("POST to HttpAssistant...");
var r2 = mf.http.post("http://127.0.0.1:8350/interact/HttpAssistant", {"input":"describe"});
print("HttpAssistant resp:", r2);

print("Shutting down via HttpAssistant shutdown endpoint...");
var r3 = mf.http.post("http://127.0.0.1:8350/interact/HttpAssistant/shutdown", {});
print("shutdown resp:", r3);

await httpmulti;
print("Server httpmulti confirmed stopped.");
