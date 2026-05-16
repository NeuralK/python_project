class Usuario:

    def __init__(self, nombre, apellido, age):
        
        self.nombre = nombre

        self.apellido = apellido

        self.age = int(age)

        self.intentos_inicios = 0

    def describir_usuario(self):

        print(f"\nAsí que usted se llama {self.nombre}.")
        print(f"\nMmmh te apellidas {self.apellido} raro apellido.") 
        print(f"\nAsí que tienes {self.age} es curioso.")
    

    def saludar(self):

        self.saludo = "\nBienvenido"

        print(self.saludo.title())

    def incrementar_intentos_inicios(self):

        self.intentos_inicios += 1
        print(f"Numero de intentos: {self.intentos_inicios}")

    def restablecer_intentos_inicio(self):
        
        self.intentos_inicios = 0
        print(f"Numero de intentos: {self.intentos_inicios}")


class Admin(Usuario):
    def __init__(self, nombre, email, age): # O los parámetros que pida Usuario
        super().__init__(nombre, email, age) # Esto conecta con la clase padre
            
               # Atributo específico de Admin

        self.privilegios = Privilegios()



class Privilegios:
    def __init__(self):
        self.privilegios = ["Puede eliminar usuarios", "Puede añadir comentarios", "Puede borrar comentarios"]
    def show_privileges(self):

        for pri in self.privilegios:
            print(pri)