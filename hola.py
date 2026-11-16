#Creacion de la clase Clientes
class clientes:
    def __init__(self, nombre, documento, animal, descripcion):
        self.nombre = nombre
        self.documento = documento
        self.animal = animal
        self.descripcion = descripcion

#Definir la funcion para el pago respectivo
def obtener_servicio(servicio):
    if servicio == "Baño y corte":
        return 50.00
    elif servicio == "Atencion Veterinaria":
        return 100.00
    else:
        return 0

#Definir la funcion para gregar clientes, falta conectar el SQLite y crear las tablas 
def agregar():
    print("\n-----------AGREGAR REGISTRO-----------------")
    nombre = input("Ingrese su nombre").strip()
    documento = input("Ingrese su documento de identidad (DNI o PASAPORTE): ").strip()
    animal = input("Ingrese el tipo de animal a atender: ").strip()
    print("\n-------SERVICIOS DISPONIBLES---------------")
    print("1. Baño y corte - S/. 50.00")
    print("2. Atencion Veterinaria - S/. 100.00")
    opcion = int(input("Ingrese la opcion que desee: "))
    while opcion <= 0 or opcion >= 3:
        opcion = int(input("Opcion incorrecta. Ingrese de nuevo: "))
    if opcion == 1:
        servicio = "Baño y corte"
    else:
        servicio == "Atencion Veterinaria"
    descripcion = input("Ingrese detalles adicionales que debamos saber antes de trabajar con su mascota: ").strip()

    precio = obtener_servicio(servicio)
    Persona = clientes(nombre, documento, animal, descripcion)
