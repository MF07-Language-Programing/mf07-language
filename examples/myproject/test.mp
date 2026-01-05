print("Hello, world!")

var logger = new Logger()

interface EmailValidate {
    intent validate(): bool
}

class EmailStr implements EmailValidate {

    intent constructor(age: int = null, email: Optional<string> = "default_email"){
        print(f"Created statament email! email={email}")
        this.email_raw = email
        this.age = age
    }

    intent validate(): bool {
        return "@gmail" in this.email_raw and this.age >= 18
    }

    intent getEmail(): string {
        return this.email_raw
    }

    intent getAge(): int{
       return this.age 
    }

    private var email_raw: string
    private var age: int = 18
}

# Use 'class' instead of 'model' for data structures
# 'model' is reserved for ML operations (create, train, predict)
class AbstractUser {
    var first_name: string
    var last_name: string
    var email: EmailStr
    
    intent constructor(first_name: string = "DEFAULT_TEST", last_name: string = "", email: EmailStr = null) {
        this.first_name = first_name
        this.last_name = last_name
        this.email_obj = email != null
        if (email != null)
            this.email = email
        else 
            this.email = new EmailStr()
    }
}

# Correct instantiation: new AbstractUser(...)
var abstractUser = new AbstractUser(
    first_name="John",
    last_name="Doe",
    email=new EmailStr(20, email="test@gmail.com")
)

logger.warn(f"email_obj={abstractUser.email_obj}")
logger.warn(abstractUser.email.getEmail())
logger.warn(abstractUser.email.getAge())
logger.warn(f"isValid={abstractUser.email.validate()}")

