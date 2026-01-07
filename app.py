from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import date
from calendar import monthrange
import os
from dotenv import load_dotenv

from db import get_connection

# ================= IMPORTS DE MODULOS =================
from clientes import (
    obtener_clientes,
    contar_clientes,
    crear_cliente,
    actualizar_cliente,
)

from gastos import (
    crear_gasto,
    actualizar_gasto,
    eliminar_gasto,
    obtener_gastos,
    obtener_gastos_por_proveedor
)

from servicios import (
    obtener_servicios,
    crear_servicio,
    actualizar_servicio,
    eliminar_servicio,
    obtener_servicio_por_id,
    contar_servicios
)

from zapatos import (
    obtener_zapatos_cliente,
    crear_zapato,
    actualizar_zapato,
    eliminar_zapato,
    cliente_tiene_zapatos
)

from ventas import (
    crear_venta,
    obtener_ventas_pendientes,
    marcar_entregada,
    agregar_zapato_a_venta,
    asignar_servicio_a_venta_zapato,
    actualizar_total_venta,
    obtener_detalles_venta
)

# ================= APP =================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# ================= UTILIDADES =================
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


# ================= HOME =================
@app.route("/")
def index():
    return render_template(
        "index.html",
        total_clientes=contar_clientes(),
        total_servicios=contar_servicios()
    )


# ================= CLIENTES =================
@app.route("/clientes")
def clientes():
    q = request.args.get("q")
    return render_template("clientes.html", clientes=obtener_clientes(q), q=q)


@app.route("/clientes/guardar", methods=["POST"])
def guardar_cliente():
    id_cliente = request.form.get("id_cliente")

    datos = (
        request.form["nombre"],
        request.form["apellido"],
        request.form["correo"],
        request.form["telefono"],
        request.form["direccion"]
    )

    if id_cliente:
        actualizar_cliente(id_cliente, *datos)
        flash("✅ Cliente actualizado correctamente.", "success")
    else:
        crear_cliente(*datos)
        flash("✅ Cliente creado correctamente.", "success")

    return redirect(url_for("clientes"))


@app.route("/clientes/eliminar/<int:id_cliente>")
def eliminar_cliente(id_cliente):
    if cliente_tiene_zapatos(id_cliente):
        flash("❌ No se puede eliminar el cliente porque tiene zapatos registrados.", "error")
        return redirect(url_for("clientes"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Cliente eliminado correctamente.", "success")
    return redirect(url_for("clientes"))


# ================= SERVICIOS =================
@app.route("/servicios")
def servicios_page():
    q = request.args.get("q")
    return render_template("servicios.html", servicios=obtener_servicios(q), q=q)


@app.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    id_servicio = request.form.get("id_servicio")

    datos = (
        request.form["nombre"],
        request.form["descripcion"],
        request.form["precio"]
    )

    if id_servicio:
        actualizar_servicio(id_servicio, *datos)
        flash("✅ Servicio actualizado correctamente.", "success")
    else:
        crear_servicio(*datos)
        flash("✅ Servicio creado correctamente.", "success")

    return redirect("/servicios")


@app.route("/servicios/eliminar/<int:id_servicio>")
def borrar_servicio(id_servicio):
    eliminar_servicio(id_servicio)
    return redirect("/servicios")


# ================= ZAPATOS =================
@app.route("/zapatos")
def buscar_cliente_zapatos():
    q = request.args.get("q", "")
    clientes = buscar_clientes_por_nombre(q) if q else []
    return render_template("zapatos_buscar.html", clientes=clientes, q=q)


@app.route("/zapatos/<int:id_cliente>")
def zapatos_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template(
        "zapatos_cliente.html",
        zapatos=obtener_zapatos_cliente(id_cliente),
        cliente=cliente
    )


@app.route("/zapatos/guardar", methods=["POST"])
def guardar_zapato():
    id_zapato = request.form.get("id_zapato")

    datos = (
        request.form["id_cliente"],
        request.form["color_base"],
        request.form["color_secundario"],
        request.form["material"],
        request.form["tipo"],
        request.form["marca"]
    )

    if id_zapato:
        actualizar_zapato(id_zapato, *datos[1:])
    else:
        crear_zapato(*datos)

    return redirect(f"/zapatos/{datos[0]}")


@app.route("/zapatos/eliminar/<int:id_zapato>/<int:id_cliente>")
def borrar_zapato(id_zapato, id_cliente):
    eliminar_zapato(id_zapato)
    return redirect(f"/zapatos/{id_cliente}")


# ================= API =================
@app.route("/api/clientes")
def api_clientes():
    q = request.args.get("q", "")
    return jsonify(buscar_clientes_por_nombre(q)) if q else jsonify([])


@app.route("/api/clientes/crear", methods=["POST"])
def api_crear_cliente():
    id_cliente = crear_cliente(
        request.form["nombre"],
        request.form["apellido"],
        request.form.get("correo"),
        request.form.get("telefono"),
        request.form.get("direccion")
    )

    return jsonify({
        "id_cliente": id_cliente,
        "nombre": request.form["nombre"],
        "apellido": request.form["apellido"]
    })


@app.route("/api/clientes/<int:id_cliente>/zapatos")
def api_zapatos_cliente(id_cliente):
    return jsonify(obtener_zapatos_cliente(id_cliente))


@app.route("/api/servicios")
def api_servicios():
    return jsonify(obtener_servicios())


# ================= VENTAS =================
@app.route("/ventas")
def ventas():
    return render_template("ventas_crear.html")


@app.route("/ventas/pendientes")
def ventas_pendientes():
    ventas = obtener_ventas_pendientes()

    for v in ventas:
        v['detalles'] = obtener_detalles_venta(v['id_venta'])

    return render_template(
        "ventas_pendientes.html",
        ventas=ventas
    )


@app.route("/ventas/entregar/<int:id_venta>")
def entregar_venta(id_venta):
    marcar_entregada(id_venta)
    flash("✅ Venta entregada correctamente.", "success")

    return redirect("/ventas/pendientes")


@app.route("/ventas/guardar", methods=["POST"])
def guardar_venta():
    prepago = request.form.get("prepago") == "si"
    monto_prepago = request.form.get("monto_prepago") if prepago else None

    venta_id = crear_venta(
        request.form["id_cliente"],
        request.form["tipo_pago"],
        prepago,
        monto_prepago
    )

    total = 0
    form = request.form.to_dict(flat=False)
    i = 0

    while f"zapatos[{i}][id_zapato]" in form:
        id_zapato = form[f"zapatos[{i}][id_zapato]"][0]
        id_servicio = form[f"zapatos[{i}][id_servicio]"][0]

        vz_id = agregar_zapato_a_venta(venta_id, id_zapato)

        servicio = obtener_servicio_por_id(id_servicio)
        precio = float(servicio["precio"])

        asignar_servicio_a_venta_zapato(
            vz_id,
            id_servicio,
            precio
        )

        total += precio

        i += 1

    actualizar_total_venta(venta_id, total)
    return redirect("/ventas/pendientes")


# ================= GASTOS =================
@app.route("/gastos")
def gastos():
    q = request.args.get("q")
    return render_template("gastos.html", gastos=obtener_gastos(q), q=q)


@app.route("/gastos/guardar", methods=["POST"])
def guardar_gasto():
    id_gasto = request.form.get("id_gasto")

    datos = (
        request.form["descripcion"],
        request.form["proveedor"],
        request.form["total"],
        request.form["fecha_registro"]
    )

    if id_gasto:
        actualizar_gasto(id_gasto, *datos)
    else:
        crear_gasto(*datos)

    return redirect("/gastos")


# ================= ESTADISTICAS =================
@app.route("/estadisticas", methods=["GET", "POST"])
def estadisticas():
    hoy = date.today()
    inicio = hoy.replace(day=1)
    fin = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])

    if request.method == "POST":
        inicio = date.fromisoformat(request.form["fecha_inicio"])
        fin = date.fromisoformat(request.form["fecha_fin"])

    return render_template(
        "estadisticas.html",
        gastos=obtener_gastos_por_proveedor(
            inicio.strftime("%Y-%m-%d"),
            fin.strftime("%Y-%m-%d")
        ),
        fecha_inicio=inicio.strftime("%Y-%m-%d"),
        fecha_fin=fin.strftime("%Y-%m-%d")
    )


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
