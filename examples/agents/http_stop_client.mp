# Start server non-blocking
serve http port 8340 name httpstop using HttpAssistant;
waitSeconds(0.2);
print("Stopping via 'stop' statement...");
stop httpstop;
await httpstop;
print("Server httpstop stopped via stop statement.");
