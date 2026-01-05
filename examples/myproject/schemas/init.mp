interface AbstractUser {
   intent isAuthenticated(session_id: string): bool 
   intent login(email: string): any 
}

class User implements AbstractUser {
   
   private var name: string
   private var role: string


   intent constructor(name: string, role: string = "guest") {
      print(f"name={name}")
      this.name = name;  
      this.role = role;
   }

   intent login(email: string): any {
      return f"login not implemented for {email}";
   }

   intent isAuthenticated(session_id: string): bool {
      return false;
   }

}