"""
Pagina web (Flask) para el Sistema de Veterinaria.

NO modifica tu codigo original: lo lee y reutiliza su conexion a la base
de datos, su creacion de tablas y sus clases (clientes, Perro, Gato, pago).

Uso:  1) pon esta carpeta (app.py, templates, static) junto a tu archivo
      2) pip install flask
      3) python app.py   ->   abre http://127.0.0.1:5000 en el navegador
"""
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

CARPETA = Path(__file__).resolve().parent
# Tu codigo abre la base con ruta relativa ("Sistema_Veterinaria.db").
# Trabajando desde esta carpeta, la web y tu version de consola usan la misma.
os.chdir(CARPETA)


# ----------------------------------------------------------------------
# 1. TRAER TU CODIGO ORIGINAL (sin editarlo)
# ----------------------------------------------------------------------
def cargar_codigo_original():
    """Busca tu archivo (el que tiene 'def conectar_base'), lo ejecuta SIN
    su ultima linea main() -que abriria el menu de consola- y devuelve
    todas sus funciones y clases."""
    for archivo in CARPETA.glob("*.py"):
        if archivo.name == Path(__file__).name:
            continue
        texto = archivo.read_text(encoding="utf-8", errors="replace").rstrip()
        if "def conectar_base" in texto:
            if texto.endswith("main()"):
                texto = texto[: -len("main()")]
            espacio = {}
            exec(texto, espacio)
            return espacio
    raise SystemExit("No encontre tu codigo. Pon app.py en la misma carpeta "
                     "que tu programa de la veterinaria.")


ORIGINAL = cargar_codigo_original()
conectar_base = ORIGINAL["conectar_base"]
creacion_tabla = ORIGINAL["creacion_tabla"]
clientes = ORIGINAL["clientes"]
Perro = ORIGINAL["Perro"]
Gato = ORIGINAL["Gato"]
pago = ORIGINAL["pago"]

# Mismos nombres que reconoce tu clase `pago`
SERVICIOS = ["Bano y corte", "Atencion Veterinaria"]


# ----------------------------------------------------------------------
# 2. BASE DE DATOS (el mismo SQL de tus funciones de consola)
# ----------------------------------------------------------------------
def consultar(nombre):
    """Como tu buscar(): trae los registros cuyo cliente contiene `nombre`."""
    conexion = conectar_base()
    conexion.row_factory = sqlite3.Row   # permite usar fila["cliente"]
    filas = conexion.execute(
        """
        SELECT registros.id AS id, registros.nombre AS cliente,
               registros.documento AS documento, mascota.nombre AS mascota,
               mascota.tipo AS tipo, mascota.raza AS raza, mascota.color AS color,
               registros.descripcion AS descripcion, registros.servicio AS servicio,
               registros.precio AS precio, registros.fecha AS fecha
        FROM registros
        INNER JOIN mascota ON mascota.id_persona = registros.id
        WHERE registros.nombre LIKE ?
        """,
        ("%" + nombre + "%",),
    ).fetchall()
    conexion.close()
    return filas


def guardar(cliente, mascota, tipo, descripcion, cobro):
    """Como el final de tu agregar(): inserta el cliente y su mascota."""
    conexion = conectar_base()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO registros (nombre, documento, descripcion, fecha, servicio, precio)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (cliente.nombre, cliente.documento, descripcion,
         cliente.fecha, cobro.servicio, cobro.monto),
    )
    id_persona = cursor.lastrowid
    raza = mascota.raza if isinstance(mascota, Perro) else None
    color = mascota.color if isinstance(mascota, Gato) else None
    cursor.execute(
        """
        INSERT INTO mascota (nombre, tipo, raza, color, id_persona)
        VALUES (?, ?, ?, ?, ?)
        """,
        (mascota.nombre, tipo, raza, color, id_persona),
    )
    conexion.commit()
    conexion.close()


def borrar(id_registro):
    """Como el final de tu eliminar(): borra la mascota y luego el registro."""
    conexion = conectar_base()
    conexion.execute("DELETE FROM mascota WHERE id_persona = ?", (id_registro,))
    conexion.execute("DELETE FROM registros WHERE id = ?", (id_registro,))
    conexion.commit()
    conexion.close()


# ----------------------------------------------------------------------
# 3. PAGINAS (una ruta por cada opcion de tu menu)
# ----------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "veterinaria"   # Flask lo exige para mostrar mensajes (flash)


@app.route("/")
def inicio():
    return redirect(url_for("agregar"))


def validar(datos):
    """Devuelve un mensaje de error, o None si los datos estan bien."""
    if not datos.get("nombre", "").strip():
        return "Ingrese el nombre del cliente."
    documento = datos.get("documento", "").strip()
    if not (1 <= len(documento) <= 9) or not documento.isalnum():
        return "El documento debe tener entre 1 y 9 letras o numeros."
    if datos.get("tipo") not in ("perro", "gato"):
        return "Elija perro o gato."
    if not datos.get("animal", "").strip():
        return "Ingrese el nombre de la mascota."
    if datos.get("servicio") not in SERVICIOS:
        return "Elija un servicio."
    try:
        datetime.strptime(datos.get("fecha", ""), "%Y-%m-%d")
    except ValueError:
        return "Ingrese una fecha valida."
    return None


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    # Valores con los que aparece el formulario la primera vez
    datos = {"tipo": "perro", "fecha": date.today().isoformat()}

    if request.method == "POST":
        datos = request.form.to_dict()
        error = validar(datos)
        if error:
            flash(error, "error")      # el formulario vuelve con lo escrito
        else:
            # Se usan TUS clases, igual que en tu agregar()
            fecha = datetime.strptime(datos["fecha"], "%Y-%m-%d").strftime("%d/%m/%y")
            cliente = clientes(datos["nombre"].strip(), datos["documento"].strip(), fecha)
            descripcion = datos.get("descripcion", "").strip()
            extra = datos.get("extra", "").strip()
            if datos["tipo"] == "perro":
                mascota = Perro(datos["animal"].strip(), descripcion, extra)
            else:
                mascota = Gato(datos["animal"].strip(), descripcion, extra)
            cobro = pago(datos["servicio"])

            guardar(cliente, mascota, datos["tipo"], descripcion, cobro)
            flash(f"Registro de {cliente.nombre} guardado: {mascota.nombre} "
                  f"({datos['tipo']}) - {cobro.servicio} - S/. {cobro.monto:.2f}", "ok")
            return redirect(url_for("agregar"))

    servicios = [(s, pago(s).monto) for s in SERVICIOS]   # precio sale de tu clase pago
    return render_template("agregar.html", datos=datos, servicios=servicios)


def leer_busqueda():
    """Lee el nombre escrito en el buscador (?nombre=...).
    Devuelve (nombre, resultados); resultados es None si aun no se busco."""
    nombre = request.args.get("nombre")
    resultados = None if nombre is None else consultar(nombre.strip())
    return (nombre or ""), resultados


@app.route("/buscar")
def buscar():
    nombre, resultados = leer_busqueda()
    return render_template("buscar.html", nombre=nombre, resultados=resultados)


@app.route("/eliminar")
def eliminar():
    nombre, resultados = leer_busqueda()
    return render_template("eliminar.html", nombre=nombre, resultados=resultados)


@app.route("/eliminar/<int:id_registro>", methods=["POST"])
def eliminar_registro(id_registro):
    borrar(id_registro)
    flash("Registro eliminado exitosamente.", "ok")
    return redirect(url_for("eliminar", nombre=request.form.get("nombre", "")))


@app.route("/pagar")
def pagar():
    nombre, resultados = leer_busqueda()
    total = sum(fila["precio"] for fila in resultados) if resultados else 0
    return render_template("pagar.html", nombre=nombre, resultados=resultados,
                           total=total)


if __name__ == "__main__":
    creacion_tabla()   # funcion de TU codigo: crea las tablas si no existen
    app.run(debug=True)
