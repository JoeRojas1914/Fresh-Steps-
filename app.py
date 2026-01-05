from flask import Flask, render_template, request, redirect, url_for, flash
from clientes import *
from servicios import (obtener_servicios, crear_servicio, actualizar_servicio, eliminar_servicio, obtener_servicio_por_id, contar_servicios)
from zapatos import (obtener_zapatos_cliente, crear_zapato, actualizar_zapato, eliminar_zapato)
from ventas import (crear_venta, obtener_ventas_pendientes, marcar_entregada, agregar_zapato_a_venta, actualizar_total_venta)
from clientes import (obtener_clientes)



app = Flask(__name__)


@app.route("/")
def index():
    total_clientes = contar_clientes()
    total_servicios = contar_servicios()
    return render_template("index.html", total_clientes=total_clientes, total_servicios=total_servicios)


# /////////////////////////////////CLIENTES/////////////////////////////////////
@app.route("/clientes")
def clientes():
    lista = obtener_clientes()
    return render_template("clientes.html", clientes=lista)

@app.route("/clientes/guardar", methods=["POST"])
def guardar_cliente():
    id_cliente = request.form.get("id_cliente")
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    correo = request.form["correo"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]

    if id_cliente:  
        actualizar_cliente(id_cliente, nombre, apellido, correo, telefono, direccion)
    else:           
        crear_cliente(nombre, apellido, correo, telefono, direccion)

    return redirect("/clientes")


@app.route("/clientes/eliminar/<int:id_cliente>")
def eliminar(id_cliente):
    eliminar_cliente(id_cliente)
    return redirect("/clientes")


# /////////////////////////////////SERVICIOS/////////////////////////////////////
@app.route("/servicios")
def servicios():
    lista = obtener_servicios()
    return render_template("servicios.html", servicios=lista)

@app.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    id_servicio = request.form.get("id_servicio")
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]

    if id_servicio:
        actualizar_servicio(id_servicio, nombre, descripcion, precio)
    else:
        crear_servicio(nombre, descripcion, precio)

    return redirect("/servicios")


@app.route("/servicios/eliminar/<int:id_servicio>")
def borrar_servicio(id_servicio):
    eliminar_servicio(id_servicio)
    return redirect("/servicios")


# /////////////////////////////////ZAPATOS/////////////////////////////////////
@app.route("/zapatos")
def buscar_cliente():
    q = request.args.get("q", "")
    clientes = []

    if q:
        clientes = buscar_clientes_por_nombre(q)

    return render_template("zapatos_buscar.html", clientes=clientes, q=q)


def buscar_clientes_por_nombre(texto):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM cliente
        WHERE nombre LIKE %s OR apellido LIKE %s
    """, (f"%{texto}%", f"%{texto}%"))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

@app.route("/zapatos/<int:id_cliente>")
def zapatos_cliente(id_cliente):
    zapatos = obtener_zapatos_cliente(id_cliente)
    cliente = obtener_cliente_por_id(id_cliente)

    return render_template(
        "zapatos_cliente.html",
        zapatos=zapatos,
        cliente=cliente
    )

def obtener_cliente_por_id(id_cliente):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
    cliente = cursor.fetchone()

    cursor.close()
    conn.close()
    return cliente


@app.route("/zapatos/guardar", methods=["POST"])
def guardar_zapato():
    id_zapato = request.form.get("id_zapato")
    id_cliente = request.form["id_cliente"]
    color_base = request.form["color_base"]
    color_secundario = request.form["color_secundario"]
    material = request.form["material"]

    if id_zapato:
        actualizar_zapato(id_zapato, color_base, color_secundario, material)
    else:
        crear_zapato(id_cliente, color_base, color_secundario, material)

    return redirect(f"/zapatos/{id_cliente}")


@app.route("/zapatos/eliminar/<int:id_zapato>/<int:id_cliente>")
def borrar_zapato(id_zapato, id_cliente):
    eliminar_zapato(id_zapato)
    return redirect(f"/zapatos/{id_cliente}")



# /////////////////////////////////VENTAS/////////////////////////////////////
@app.route("/ventas")
def ventas():
    clientes = obtener_clientes()
    return render_template("ventas_crear.html", clientes=clientes)

@app.route("/ventas/pendientes")
def ventas_pendientes():
    ventas = obtener_ventas_pendientes()
    return render_template("ventas_pendientes.html", ventas=ventas)


@app.route("/ventas/entregar/<int:id_venta>")
def entregar_venta(id_venta):
    marcar_entregada(id_venta)
    return redirect("/ventas/pendientes")

@app.route("/api/clientes")
def api_clientes():
    q = request.args.get("q", "")
    if not q:
        return []

    clientes = buscar_clientes_por_nombre(q)
    return clientes

@app.route("/ventas/guardar", methods=["POST"])
def guardar_venta():
    id_cliente = request.form["id_cliente"]
    tipo_pago = request.form["tipo_pago"]

    venta_id = crear_venta(id_cliente, tipo_pago)

    total = 0
    form = request.form.to_dict(flat=False)

    i = 0
    while f"zapatos[{i}][id_zapato]" in form:
        id_zapato = form[f"zapatos[{i}][id_zapato]"][0]
        id_servicio = form[f"zapatos[{i}][id_servicio]"][0]

        vz_id = agregar_zapato_a_venta(venta_id, id_zapato)

        servicio = obtener_servicio_por_id(id_servicio)
        agregar_servicio_a_zapato(vz_id, id_servicio,)

        total += float(servicio["precio"])
        i += 1

    actualizar_total_venta(venta_id, total)

    return redirect("/ventas/pendientes")








if __name__ == "__main__":
    app.run(debug=True)
