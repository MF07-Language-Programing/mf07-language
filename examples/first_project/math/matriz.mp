# --- super() demonstration ---
class Base {
    var x: int = 0
    intent constructor(x: int) {
        this.x = x
    }
    intent getX() { return this.x }
}

class Derived extends Base {
    var y: int = 0
    intent constructor(x: int, y: int) {
        super(x)
        this.y = y
    }
    intent getY() { return this.y }
    intent showBoth() {
        print("x=", this.getX(), "y=", this.getY())
    }
}

intent test_matriz(){
    var rows: int = 20
    var cols: int = 20
    var matrix = new List()

    # Monta a matriz de objetos Derived
    var i: int = 0
    while (i < rows) {
        var row = new List()
        var j: int = 0
        while (j < cols) {
            var obj = new Derived(i + 1, (j + 1) * 2)
            row.append(obj)
            j = j + 1
        }
        matrix.append(row)
        i = i + 1
    }

    # Cabeçalho
    var header = "    "
    var j: int = 0
    while (j < cols) {
        header = header + " " + (j + 1).toString()
        j = j + 1
    }
    print("Matriz (" + rows.toString() + "x" + cols.toString() + "):")
    print(header)

    # Imprime a tabela: em cada célula mostra getX() + getY()
    var i2: int = 0
    while (i2 < rows) {
        var row = matrix.get(i2)
        var line = "["
        var j2: int = 0
        while (j2 < cols) {
            var cell = row.get(j2)
            var value = cell.getX() + cell.getY()
            if (StringHelpers.isEmpty(line)) {
                line = line + value.toString()
            } else {
                line = line + "," + value.toString()
            }
            j2 = j2 + 1
        }
        line = line + "]"
        print(line)
        i2 = i2 + 1
    }

    print("Demo finished")
}

test_matriz()