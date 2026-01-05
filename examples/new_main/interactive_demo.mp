# Interactive demo: supports MF_INPUTS env var for non-interactive runs
var cols: int = input("Quantas colunas da matrix?", "int")
print("Cols read:", cols)
# union input: try int or float
var threshold: int|float = input("Threshold (int|float):", "int|float")
print("Threshold:", threshold)
# bool
var flag: bool = input("Activate? (y/n):", "bool")
print("Flag:", flag)
