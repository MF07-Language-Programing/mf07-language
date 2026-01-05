interface MessageBase {
    intent getRole(): string
    intent getContent(): string
}

class UserMessage implements MessageBase {
    var role: string = "user"
    var content: string = ""

    intent constructor(content: string) {
        this.content = content
    }

    intent getContent(): string {
        return this.content
    }

    intent getRole(): string {
        return this.role
    }

    intent toString(): string {
        return "UserMessage(role={this.role}, content={this.content})"
    }
}

class AssistantMessage implements MessageBase {
    var role: string = "assistant"
    var content: string = ""

    intent constructor(content: string) {
        this.content = content
    }

    intent getContent(): string {
        return this.content
    }

    intent getRole(): string {
        return this.role
    }

    intent toString(): string {
        return "AssistantMessage(role={this.role}, content={this.content})"
    }
}

class ChatCompletionRequest {
    var model_id: string = null
    var messages: list = new List()
    var max_tokens: int = 2048
    var temperature: float = 0.7
    var top_p: float = 1.0
    var n: int = 1
    var stream: bool = false
    var stop: any = null
    var presence_penalty: float = 0.0
    var frequency_penalty: float = 0.0
    var logit_bias: any = null
    var user: string = ""

    intent constructor(model_id: string, messages: list) {
        this.model_id = model_id
        this.messages = messages
    }

    intent addMessage(message: any): void {
        this.messages.append(message)
    }
    
    intent toString(): string {
        var s = "ChatCompletionRequest(model={this.model_id}, messages={this.messages}, max_tokens={this.max_tokens}, temperature={this.temperature}, top_p={this.top_p}, n={this.n}, stream={this.stream}, stop={this.stop}, presence_penalty={this.presence_penalty}, frequency_penalty={this.frequency_penalty}, logit_bias={this.logit_bias}, user={this.user})"
        return s
    }
}