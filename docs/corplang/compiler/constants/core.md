# Módulo: core.py

Sem descrição.

## Classe: `SyntaxException`
Sem descrição.

### Método: `SyntaxException.__init__(self, line, column, position, expected, found)`
Sem descrição.

## Classe: `TokenStream`
Sem descrição.

### Método: `TokenStream.__init__(self, tokens)`
Sem descrição.

### Método: `TokenStream.current(self)`
Sem descrição.

### Método: `TokenStream.peek(self, offset)`
Sem descrição.

### Método: `TokenStream.advance(self)`
Sem descrição.

### Método: `TokenStream.match(self)`
Sem descrição.

### Método: `TokenStream.expect_identifier_like(self)`
Sem descrição.

### Método: `TokenStream.expect(self)`
Sem descrição.

### Método: `TokenStream.eof(self)`
Sem descrição.

## Classe: `PositionTracker`
Sem descrição.

### Método: `PositionTracker.__init__(self, stream, source_file)`
Sem descrição.

### Método: `PositionTracker.clone_position(self)`
Sem descrição.

### Método: `PositionTracker.error(self, message)`
Sem descrição.

## Função: `parse_block(ctx, parent)`
Sem descrição.

## Função: `separated(ctx, parse_item, separator)`
Sem descrição.
