// Example that demonstrates starting an HTTP server non-blocking and shutting it down
serve http port 8300 name http1 using HttpAssistant;

# give server a moment to start
waitSeconds(0.2);

print("Sending shutdown request to server http1...");
var resp = mf.http.post("http://127.0.0.1:8300/interact/HttpAssistant/shutdown", {});
print("shutdown response:", resp);

# await server stop
await http1;
print("Server http1 confirmed stopped.");
