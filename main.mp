# main.mp - Corplang Program Entry Point
from core.collections import List

intent matrixBanner() {
    var chars: string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"
    var width: int = 48
    var height: int = 16
    var banner: string = "   MF07 LANGUAGE   "

    for (var offset = height; offset >= -len(banner); offset = offset - 1) {
        mf.console.clear()

        for (var y = 0; y < height; y = y + 1) {
            var line: string = ""

            if (y == offset) {
                var pad: int = (width - len(banner)) / 2
                for (var p = 0; p < pad; p = p + 1)
                    line = line + " "
                line = line + banner
            } else {
                for (var x = 0; x < width; x = x + 1) {
                    var idx: int = (x + y + offset) % len(chars)
                    if (idx < 0)
                        idx = idx + len(chars)
                    line = line + chars[idx]
                }
            }

            mf.console.writeln(line)
        }

        mf.console.flush()

        waitSeconds(0.08)
    }
}

intent main() {
    matrixBanner()
}

main()
