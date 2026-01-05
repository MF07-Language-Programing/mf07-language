# File: MODULE_B/Dog.mp
# This file defines a different Dog class in MODULE_B (for business logic)

class Dog {
    private var id: int
    private var businessName: string
    private var status: string

    intent constructor(id: int, name: string, status: string) {
        this.id = id
        this.businessName = name
        this.status = status
    }

    intent getBusinessInfo(): string {
        return "Business Dog #{this.id}: {this.businessName} ({this.status})"
    }

    intent updateStatus(newStatus: string) {
        this.status = newStatus
    }
}
