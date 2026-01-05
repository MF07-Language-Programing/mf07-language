agent SalesAgent {
    intelligence {
        provider auto
        capability prediction
        training auto
        mode conversational
    }
    context {
        allow function calculate_tax
        allow class OrderService
        deny filesystem
    }
    execution {
        async true
        cache_context true
    }
}

agent train SalesAgent on sales_dataset;

agent run SalesAgent with { order_id: 123 };

loop stdin using SalesAgent
print("test")