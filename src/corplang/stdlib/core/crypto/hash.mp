"""Hash helpers wrapping runtime algorithms."""

class Hash {
    static intent apply(algorithm: string, data) {
        try {
            return mf.hash.apply_hash_algorithm(algorithm, data)
        } catch (e: Exception) {
            return ""
        }
    }
}
