# File: test-collision.mp
# Teste de colisão de nomes e imports duplicados

# TESTE 1: Imports do mesmo símbolo de módulos diferentes
import coreDog from MODULE_A.Dog
import businessDog from MODULE_B.Dog

# TESTE 2: Imports duplicados (DEVE GERAR WARNING)
import MODULE_A_Dog from Dog

# TESTE 3: Uso dos imports
let dog1 = new coreDog("Rex", 5)
let dog2 = new businessDog(101, "Buddy", "active")

# Quando usuário clica em "coreDog" aqui e pressiona F12:
# Sistema deve ir para MODULE_A/Dog.mp (NOT MODULE_B!)
let bark = dog1.speak()

# Quando usuário clica em "businessDog" aqui e pressiona F12:
# Sistema deve ir para MODULE_B/Dog.mp (NOT MODULE_A!)
let info = dog2.getBusinessInfo()
