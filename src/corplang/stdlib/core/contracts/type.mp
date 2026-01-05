# Core contract for type metadata

interface TypeContract {
    intent name(): string
    intent isAssignableFrom(other: TypeContract): bool
}
