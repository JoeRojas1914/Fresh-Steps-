from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import date
from calendar import monthrange
import os
from dotenv import load_dotenv
from datetime import date, timedelta
from calendar import monthrange


from db import get_connection

# ================= IMPORTS DE MODULOS =================
from clientes import (
    contar_clientes,
    obtener_clientes,
    crear_cliente,
    actualizar_cliente,
)

from gastos import (
    crear_gasto,
    actualizar_gasto,
    obtener_gastos,
    eliminar_gasto,
    obtener_gastos_por_proveedor,
)

from servicios import (
    contar_servicios,
    obtener_servicios,
    crear_servicio,
    actualizar_servicio,
    eliminar_servicio,
    obtener_servicio_por_id,
)

from zapatos import (
    obtener_zapatos_cliente,
    crear_zapato,
    eliminar_zapato,
    cliente_tiene_zapatos
)

from ventas import (
    contar_entregas_pendientes,
    crear_venta,
    obtener_ventas_pendientes,
    marcar_entregada,
    agregar_zapato_a_venta,
    asignar_servicio_a_venta_zapato,
    actualizar_total_venta,
    obtener_detalles_venta,
    obtener_ingresos_por_semana
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
        total_entregas=contar_entregas_pendientes()  
    )



# ================= CLIENTES =================
@app.route("/clientes")
def clientes():
    q = request.args.get("q", "")
    pagina = request.args.get("pagina", 1, type=int)  
    por_pagina = 10 

    todos_los_clientes = obtener_clientes(q)

    total_clientes = len(todos_los_clientes)
    total_paginas = (total_clientes + por_pagina - 1) // por_pagina  

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    clientes_pagina = todos_los_clientes[inicio:fin]

    return render_template(
        "clientes.html",
        clientes=clientes_pagina,
        q=q,
        pagina=pagina,
        total_paginas=total_paginas
    )




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

@app.route("/clientes/<int:id_cliente>")
def ver_cliente(id_cliente):
    pagina = request.args.get("pagina", 1, type=int)
    pedidos_por_pagina = 5

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *, DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro_fmt
        FROM cliente
        WHERE id_cliente = %s
    """, (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM venta WHERE id_cliente = %s", (id_cliente,))
    total_pedidos = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    total_paginas = (total_pedidos + pedidos_por_pagina - 1) // pedidos_por_pagina

    inicio = (pagina - 1) * pedidos_por_pagina

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            v.id_venta, 
            v.fecha_recibo, 
            v.fecha_entrega,
            v.total, 
            v.tipo_pago
        FROM venta v
        WHERE v.id_cliente = %s
        ORDER BY v.fecha_recibo DESC
        LIMIT %s OFFSET %s
    """, (id_cliente, pedidos_por_pagina, inicio))
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()

    for p in pedidos:
        p['detalles'] = obtener_detalles_venta(p['id_venta'])

    return render_template(
        "cliente_perfil.html",
        cliente=cliente,
        total_pedidos=total_pedidos,
        pedidos=pedidos,
        pagina=pagina,
        total_paginas=total_paginas
    )




# ================= SERVICIOS =================
@app.route("/servicios")
def servicios_page():
    q = request.args.get("q")
    pagina = request.args.get("pagina", 1, type=int)  
    servicios_por_pagina = 10

    todos_servicios = obtener_servicios(q)

    total_servicios = len(todos_servicios)
    total_paginas = (total_servicios + servicios_por_pagina - 1) // servicios_por_pagina

    inicio = (pagina - 1) * servicios_por_pagina
    fin = inicio + servicios_por_pagina
    servicios = todos_servicios[inicio:fin]

    return render_template(
        "servicios.html",
        servicios=servicios,
        q=q,
        pagina=pagina,
        total_paginas=total_paginas
    )



@app.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    id_servicio = request.form.get("id_servicio")

    datos = (
        request.form["nombre"],
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
    from servicios import servicio_tiene_ventas

    if servicio_tiene_ventas(id_servicio):
        flash("❌ No se puede eliminar este servicio porque ya está asociado a una venta.", "error")
        return redirect("/servicios")

    eliminar_servicio(id_servicio)
    flash("✅ Servicio eliminado correctamente.", "success")
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

    datos = (
        request.form["id_cliente"],
        request.form["color_base"],
        request.form["color_secundario"],
        request.form["material"],
        request.form["tipo"],
        request.form["marca"]
    )


    crear_zapato(*datos)
    flash("✅ Zapato añadido correctamente.", "success")

    return redirect(f"/zapatos/{datos[0]}")


@app.route("/zapatos/eliminar/<int:id_zapato>/<int:id_cliente>")
def borrar_zapato(id_zapato, id_cliente):
    from zapatos import zapato_tiene_ventas

    if zapato_tiene_ventas(id_zapato):
        flash("❌ No se puede eliminar este calzado porque ya está asociado a una venta.", "error")
        return redirect(f"/zapatos/{id_cliente}")

    eliminar_zapato(id_zapato)
    flash("✅ Zapato eliminado correctamente.", "success")
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

@app.route("/api/zapatos/crear", methods=["POST"])
def api_crear_zapato():
    id_cliente = request.form["id_cliente"]
    color_base = request.form["color_base"]
    color_secundario = request.form["color_secundario"]
    material = request.form["material"]
    tipo = request.form["tipo"]
    marca = request.form["marca"]

    crear_zapato(id_cliente, color_base, color_secundario, material, tipo, marca)

    zapatos = obtener_zapatos_cliente(id_cliente)
    nuevo_zapato = zapatos[-1]

    return jsonify(nuevo_zapato)


@app.route("/api/estadisticas/gastos")
def api_estadisticas_gastos():
    mes = request.args.get("mes", type=int)
    año = request.args.get("año", type=int)
    if not mes:
        mes = date.today().month
    if not año:
        año = date.today().year

    inicio = date(año, mes, 1)
    fin = date(año, mes, monthrange(año, mes)[1])

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT proveedor, fecha_registro, SUM(total) AS total
        FROM gastos
        WHERE fecha_registro BETWEEN %s AND %s
        GROUP BY proveedor, fecha_registro
    """, (inicio, fin))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    semanas = []
    semana_actual = inicio
    semana_map = []

    meses_nombres = ["", "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                     "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    while semana_actual <= fin:
        start = semana_actual
        end = min(semana_actual + timedelta(days=6), fin)
        semanas.append(f"{start.day}-{end.day} {meses_nombres[start.month]}")
        semana_map.append((start, end))
        semana_actual = end + timedelta(days=1)

    proveedores_set = set(r["proveedor"] for r in rows)
    data_proveedores = {prov: [0]*len(semanas) for prov in proveedores_set}

    for r in rows:
        for i, (start, end) in enumerate(semana_map):
            if start <= r["fecha_registro"] <= end:
                data_proveedores[r["proveedor"]][i] += float(r["total"])
                break

    return jsonify({
        "semanas": semanas,
        "proveedores": data_proveedores
    })




@app.route("/api/estadisticas/ingresos")
def api_estadisticas_ingresos():
    hoy = date.today()
    mes = request.args.get("mes", hoy.month, type=int)
    año = request.args.get("año", hoy.year, type=int)

    return jsonify(obtener_ingresos_por_semana(mes, año))

@app.route("/api/estadisticas/gastos/años")
def años_gastos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT DISTINCT YEAR(fecha_registro) AS año
        FROM gastos
        ORDER BY año DESC
    """)
    data = [r["año"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)



@app.route("/api/estadisticas/gastos/meses")
def meses_gastos():
    año = request.args.get("año", type=int)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT DISTINCT MONTH(fecha_registro) AS mes
        FROM gastos
        WHERE YEAR(fecha_registro) = %s
        ORDER BY mes
    """, (año,))
    data = [r["mes"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)



@app.route("/api/estadisticas/ingresos/años")
def años_ingresos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT DISTINCT YEAR(fecha_recibo) AS año
        FROM venta
        ORDER BY año DESC
    """)
    data = [r["año"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)



@app.route("/api/estadisticas/ingresos/meses")
def meses_ingresos():
    año = request.args.get("año", type=int)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT DISTINCT MONTH(fecha_recibo) AS mes
        FROM venta
        WHERE YEAR(fecha_recibo) = %s
        ORDER BY mes
    """, (año,))
    data = [r["mes"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)


@app.route("/api/estadisticas/totales-mes")
def totales_mes():
    mes = request.args.get("mes", type=int)
    año = request.args.get("año", type=int)

    if not mes:
        mes = date.today().month
    if not año:
        año = date.today().year

    inicio = date(año, mes, 1)
    fin = date(año, mes, monthrange(año, mes)[1])

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT IFNULL(SUM(total),0) AS total_ventas
        FROM venta
        WHERE fecha_recibo BETWEEN %s AND %s
    """, (inicio, fin))
    total_ventas = cur.fetchone()["total_ventas"]

    cur.execute("""
        SELECT IFNULL(SUM(total),0) AS total_gastos
        FROM gastos
        WHERE fecha_registro BETWEEN %s AND %s
    """, (inicio, fin))
    total_gastos = cur.fetchone()["total_gastos"]

    cur.close()
    conn.close()

    ganancia = total_ventas - total_gastos

    return jsonify({
        "ventas": total_ventas,
        "gastos": total_gastos,
        "ganancia": ganancia
    })





# ================= VENTAS =================
@app.route("/ventas")
def ventas():
    return render_template("ventas_crear.html")


@app.route("/ventas/pendientes")
def ventas_pendientes():
    ventas = obtener_ventas_pendientes()
    ventas_con_detalles = []

    for v in ventas:
        detalles = obtener_detalles_venta(v['id_venta'])
        v['detalles'] = detalles
        ventas_con_detalles.append(v)

    return render_template(
        "ventas_pendientes.html",
        ventas=ventas_con_detalles
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
    flash("✅ Venta creada correctamente.", "success")
    return redirect("/ventas/pendientes")


# ================= GASTOS =================
@app.route("/gastos")
def gastos():
    proveedor = request.args.get("proveedor", "")
    pagina = request.args.get("pagina", 1, type=int)  
    por_pagina = 10 

    todos_los_gastos = obtener_gastos(proveedor)

    # Calcular total de páginas
    total_gastos = len(todos_los_gastos)
    total_paginas = (total_gastos + por_pagina - 1) // por_pagina

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    gastos_pagina = todos_los_gastos[inicio:fin]

    return render_template(
        "gastos.html",
        gastos=gastos_pagina,
        proveedor=proveedor,
        pagina=pagina,
        total_paginas=total_paginas
    )




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
        flash("✅ Gasto editado correctamente.", "success")
    else:
        crear_gasto(*datos)
        flash("✅ Gasto creado correctamente.", "success")

    return redirect("/gastos")

@app.route("/gastos/eliminar/<int:id_gasto>")
def borrar_gasto(id_gasto):
    eliminar_gasto(id_gasto) 
    flash("✅ Gasto eliminado correctamente.", "success")
    return redirect("/gastos")





# ================= ESTADISTICAS =================
@app.route("/estadisticas")
def estadisticas():
    hoy = date.today()
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    return render_template(
        "estadisticas.html",
        meses=meses,
        año_actual=hoy.year,
        mes_gastos=hoy.month,
        mes_ingresos=hoy.month,
        total_clientes=contar_clientes(),
        total_servicios=contar_servicios()
    )




# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
