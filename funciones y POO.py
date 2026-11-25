import sqlite3
def conectar_base():
    conexion = sqlite3.connect("Sistema_Veterinaria.db")
    return conexion

#funcion para crear la tabla de sql
def creacion_tabla():
    conexion = conectar_base()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            servicio TEXT NOT NULL,
            precio REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            raza TEXT,
            color TEXT,
            id_persona INTEGER NOT NULL,
            FOREIGN KEY (id_persona) REFERENCES registros(id)
        )
    """)
    conexion.commit()
    conexion.close()

#creacion de clases
class clientes:
    def __init__(self, nombre, documento, fecha):
        self.nombre = nombre
        self.documento = documento
        self.fecha = fecha


class Animal:
    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion


class Perro(Animal):
    def __init__(self, nombre, descripcion, raza):
        super().__init__(nombre, descripcion)
        self.raza = raza


class Gato(Animal):
    def __init__(self, nombre, descripcion, color):
        super().__init__(nombre, descripcion)
        self.color = color


class pago:
    def __init__(self, servicio):
        self.servicio = servicio
        if servicio == "Bano y corte":
            self.monto = 50.00
        elif servicio == "Atencion Veterinaria":
            self.monto = 100.00
        else:
            self.monto = 0

#funcion para agregar clientes al sistema
def agregar():
    print("\n-----------AGREGAR REGISTRO-----------------")
    nombre = input("Ingrese su nombre: ").strip()
    documento = input("Ingrese su documento de identidad (DNI o PASAPORTE): ").strip()
    while len(documento) < 0 or len(documento) > 9:
        documento = input("Ingrese su documento de identidad (DNI o PASAPORTE): ").strip()
    tipo_animal = input("Ingrese el tipo de animal (perro/gato): ").strip().lower()
    nombre_animal = input("Ingrese el nombre del animal: ").strip()
    descripcion = input("Ingrese detalles adicionales que debamos saber antes de trabajar con su mascota: ").strip()
    if tipo_animal == "perro":
        raza = input("Ingrese la raza del perro: ").strip()
        mascota_obj = Perro(nombre_animal, descripcion, raza)
    elif tipo_animal == "gato":
        color = input("Ingrese el color del gato: ").strip()
        mascota_obj = Gato(nombre_animal, descripcion, color)
    else:
        mascota_obj = Animal(nombre_animal, descripcion)
    print("\n-------SERVICIOS DISPONIBLES---------------")
    print("1. Bano y corte - S/. 50.00")
    print("2. Atencion Veterinaria - S/. 100.00")
    opcion = int(input("Ingrese la opcion que desee: "))
    while opcion <= 0 or opcion >= 3:
        opcion = int(input("Opcion incorrecta. Ingrese de nuevo: "))
    if opcion == 1:
        servicio = "Bano y corte"
    else:
        servicio = "Atencion Veterinaria"
    cobro = pago(servicio)
    print("Ingreso de fecha (Tenga en cuenta que el ingreso debe tener este formato: DD/MM/AA)")
    fecha = input("Ingrese la fecha de trabajo: ").strip()
    cliente = clientes(nombre, documento, fecha)
    conexion = conectar_base()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO registros (nombre, documento, descripcion, fecha, servicio, precio)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente.nombre, cliente.documento, descripcion, cliente.fecha, cobro.servicio, cobro.monto))
    id_persona = cursor.lastrowid
    raza_val = mascota_obj.raza if isinstance(mascota_obj, Perro) else None
    color_val = mascota_obj.color if isinstance(mascota_obj, Gato) else None
    cursor.execute("""
        INSERT INTO mascota (nombre, tipo, raza, color, id_persona)
        VALUES (?, ?, ?, ?, ?)
    """, (mascota_obj.nombre, tipo_animal, raza_val, color_val, id_persona))
    conexion.commit()
    conexion.close()
    print("\nRegistro guardado exitosamente.")
    print(f"  Cliente: {cliente.nombre} | DNI: {cliente.documento}")
    print(f"  Mascota: {mascota_obj.nombre} ({tipo_animal})")
    print(f"  Servicio: {cobro.servicio} - S/. {cobro.monto}")
    print(f"  Fecha: {cliente.fecha}")

#funcion buscar mediante el nombre unicamente
def buscar():
    print("\n-----------BUSCAR REGISTRO-----------------")
    nombre = input("Ingrese el nombre de la persona a buscar: ").strip()
    conexion = conectar_base()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT registros.id, registros.nombre, registros.documento,
               mascota.nombre, mascota.tipo, mascota.raza, mascota.color,
               registros.descripcion, registros.servicio, registros.precio, registros.fecha
        FROM registros
        INNER JOIN mascota ON mascota.id_persona = registros.id
        WHERE registros.nombre LIKE ?
    """, ("%" + nombre + "%",))
    resultados = cursor.fetchall()
    conexion.close()
    if resultados:
        print(f"\nSe encontraron {len(resultados)} registro(s):\n")
        for fila in resultados:
            print(f"  ID: {fila[0]}")
            print(f"  Cliente: {fila[1]} | DNI: {fila[2]}")
            print(f"  Mascota: {fila[3]} ({fila[4]})")
            if fila[5]:
                print(f"  Raza: {fila[5]}")
            if fila[6]:
                print(f"  Color: {fila[6]}")
            print(f"  Descripcion: {fila[7]}")
            print(f"  Servicio: {fila[8]} - S/. {fila[9]}")
            print(f"  Fecha: {fila[10]}")
    else:
        for fila in resultados:
            print(fila)
        print(f"\nNo se encontraron registros para '{nombre}'.")

#funcion eliminar registros
def eliminar():
    print("\n-----------ELIMINAR REGISTRO-----------------")
    nombre = input("Ingrese el nombre de la persona a eliminar: ").strip()
    conexion = conectar_base()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT registros.id, registros.nombre, mascota.nombre, registros.servicio, registros.precio
        FROM registros
        INNER JOIN mascota ON mascota.id_persona = registros.id
        WHERE registros.nombre LIKE ?
    """, ("%" + nombre + "%",))
    resultados = cursor.fetchall()
    if not resultados:
        print(f"\nNo se encontraron registros para '{nombre}'.")
        conexion.close()
        return
    print("\nRegistros encontrados:")
    for fila in resultados:
        print(f"  ID: {fila[0]} | {fila[1]} | Mascota: {fila[2]} | {fila[3]} - S/. {fila[4]}")
    id_eliminar = int(input("\nIngrese el ID del registro a eliminar: "))
    cursor.execute("DELETE FROM mascota WHERE id_persona = ?", (id_eliminar,))
    cursor.execute("DELETE FROM registros WHERE id = ?", (id_eliminar,))
    conexion.commit()
    conexion.close()
    print("Registro eliminado exitosamente.")

#funcion pagar
def pagar():
    print("\n-----------PAGAR-----------------")
    nombre = input("Ingrese el nombre de la persona: ").strip()
    conexion = conectar_base()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT registros.nombre, mascota.nombre, registros.servicio, registros.precio
        FROM registros
        INNER JOIN mascota ON mascota.id_persona = registros.id
        WHERE registros.nombre LIKE ?
    """, ("%" + nombre + "%",))
    resultados = cursor.fetchall()
    conexion.close()
    if not resultados:
        print(f"\nNo se encontraron registros para '{nombre}'.")
        return
    print(f"\nServicios de {resultados[0][0]}:\n")
    total = 0
    for fila in resultados:
        print(f"  - {fila[2]} (Mascota: {fila[1]}): S/. {fila[3]}")
        total = total + fila[3]

    print(f"\n  TOTAL A PAGAR: S/. {total}")

#funcion menu
def mostrar_menu():
    print("\n===== SISTEMA VETERINARIA =====")
    print("1. Agregar")
    print("2. Buscar")
    print("3. Eliminar")
    print("4. Pagar")
    print("5. Salir")


def main():
    creacion_tabla()
    while True:
        mostrar_menu()
        opcion = input("Elija una opcion: ").strip()
        if opcion == "1":
            agregar()
        elif opcion == "2":
            buscar()
        elif opcion == "3":
            eliminar()
        elif opcion == "4":
            pagar()
        elif opcion == "5":
            print("Hasta luego.")
            break
        else:
            print("Opcion no valida.")
