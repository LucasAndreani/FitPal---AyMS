from datetime import datetime

class Usuario:
    def __init__(self, nombre, email, password, edad, peso, altura):
        self.id_usuario = None
        self.nombre = nombre
        self.email = email
        self.password = password # Solo para esta entrega y para definir la estructura, el password se manejara con los metodos de seguridad correspondientes
        self.edad = edad
        self.peso = peso
        self.altura = altura
        self.fecha_registro = datetime.now()

    def __str__(self):
        return f"Usuario: {self.nombre} - {self.email}"