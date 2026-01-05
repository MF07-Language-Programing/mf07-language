// Debug script to test split() functionality

print("🔧 Debug: Testando split() básico\n")

// Test 1: Simple split
print("1️⃣ Teste simples de split:")
var text = "a,b,c"
var result = text.split(",")
print(f"   Input: {text}")
print(f"   Type: {type(result)}")
print(f"   Result: {result}")

// Test 2: Split with newlines
print("\n2️⃣ Teste de split com quebras:")
var multiline = "linha1\nlinha2\nlinha3"
var lines = multiline.split("\n")
print(f"   Input: {multiline}")
print(f"   Type: {type(lines)}")
print(f"   Result: {lines}")

// Test 3: Try to get individual items
print("\n3️⃣ Teste de acesso a itens:")
try {
    print(f"   Item 0: {lines[0]}")
    print(f"   Item 1: {lines[1]}")
    print(f"   Item 2: {lines[2]}")
} catch (e: Exception) {
    print(f"   ❌ Erro ao acessar itens: {e}")
}

// Test 4: Try to iterate (THIS IS THE FAILING CASE)
print("\n4️⃣ Teste de iteração com for-in:")
try {
    for (var line in lines) {
        print(f"   - {line}")
    }
} catch (e: Exception) {
    print(f"   ❌ Erro na iteração: {e}")
}

// Test 5: Try to iterate over literal list
print("\n5️⃣ Teste de iteração com lista literal:")
try {
    var literal = ["x", "y", "z"]
    for (var item in literal) {
        print(f"   - {item}")
    }
} catch (e: Exception) {
    print(f"   ❌ Erro na iteração literal: {e}")
}

print("\n✅ Testes concluídos")
