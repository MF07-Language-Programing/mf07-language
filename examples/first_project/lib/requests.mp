
async intent get(path: str) : str {
    print("Fetching from:", path);
    await waitSeconds(3);
    return "GET response from {path}";
}

async intent post(path: str, data: dict) : str {
    print("Posting to:", path);
    print("Data:", data);
    await waitSeconds(2);
    return "POST response from {path} with data {data}";
}

intent getSync(path: str) : str {
    print("Fetching (sync) from:", path);
    return "SYNC GET response from {path}";
}
