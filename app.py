from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import date, timedelta, datetime
from calendar import monthrange
import os
from dotenv import load_dotenv
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
    contar_gastos,
)

from servicios import (
    contar_servicios,
    obtener_servicios,
    crear_servicio,
    actualizar_servicio,
    eliminar_servicio,
)

from ventas import (
    crear_venta,
    obtener_venta,
    obtener_ventas_pendientes,
    obtener_detalles_venta,
    marcar_entregada,
    contar_entregas_pendientes,
)

from estadisticas import (
    generar_semanas_rango,
    contar_ventas_por_semana,
    obtener_gastos_por_semana_y_proveedor,
    obtener_total_gastos,
    obtener_unidades_por_semana
)

from negocio import obtener_negocios

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



@app.route("/api/servicios")
def api_servicios():
    id_negocio = request.args.get("id_negocio", type=int)
    return jsonify(obtener_servicios(id_negocio=id_negocio, limit=1000, offset=0))



# ================= HOME =================
@app.route("/")
def index():
    total_entregas = contar_entregas_pendientes()
    return render_template("index.html", total_entregas=total_entregas)




# ================= CLIENTES =================
@app.route("/clientes")
def clientes():
    q = request.args.get("q", "")
    pagina = request.args.get("pagina", 1, type=int)
    por_pagina = 10

    offset = (pagina - 1) * por_pagina

    total_clientes = contar_clientes(q)
    total_paginas = (total_clientes + por_pagina - 1) // por_pagina

    clientes = obtener_clientes(
        q=q,
        limit=por_pagina,
        offset=offset
    )

    return render_template(
        "clientes.html",
        clientes=clientes,
        q=q,
        pagina=pagina,
        total_paginas=total_paginas
    )





@app.route("/clientes/guardar", methods=["POST"])
def guardar_cliente():
    id_cliente = request.form.get("id_cliente")

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    correo = request.form.get("correo", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()

    if not nombre or not apellido or not telefono:
        flash("❌ Nombre, apellido y teléfono son obligatorios.", "alert-error")
        return redirect(url_for("clientes"))

    if not telefono.isdigit() or len(telefono) != 10:
        flash("❌ El teléfono debe contener exactamente 10 números.", "alert-error")
        return redirect(url_for("clientes"))

    datos = (nombre, apellido, correo, telefono, direccion)

    if id_cliente:
        actualizar_cliente(id_cliente, *datos)
        flash("✅ Cliente actualizado correctamente.", "success")
    else:
        crear_cliente(*datos)
        flash("✅ Cliente creado correctamente.", "success")

    return redirect(url_for("clientes"))



@app.route("/clientes/eliminar/<int:id_cliente>")
def eliminar_cliente(id_cliente):
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
    inicio = (pagina - 1) * pedidos_por_pagina


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


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            v.id_venta, 
            v.fecha_recibo, 
            v.fecha_entrega,
            v.total, 
            v.tipo_pago,
            v.cantidad_descuento,
            n.nombre AS negocio
        FROM venta v
        LEFT JOIN negocio n ON v.id_negocio = n.id_negocio
        WHERE v.id_cliente = %s
        ORDER BY v.fecha_recibo DESC
        LIMIT %s OFFSET %s
    """, (id_cliente, pedidos_por_pagina, inicio))
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()


    for p in pedidos:
        p["detalles"] = obtener_detalles_venta(p["id_venta"])

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
def servicios():
    q = request.args.get("q", "")
    id_negocio = request.args.get("id_negocio", type=int)
    pagina = request.args.get("pagina", 1, type=int)

    por_pagina = 10
    offset = (pagina - 1) * por_pagina

    negocios = obtener_negocios()

    total_servicios = contar_servicios(id_negocio=id_negocio, q=q)
    total_paginas = (total_servicios + por_pagina - 1) // por_pagina

    servicios = obtener_servicios(
        id_negocio=id_negocio,
        q=q,
        limit=por_pagina,
        offset=offset
    )

    return render_template(
        "servicios.html",
        servicios=servicios,
        negocios=negocios,
        id_negocio=id_negocio,
        q=q,
        pagina=pagina,
        total_paginas=total_paginas
    )



@app.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    id_servicio = request.form.get("id_servicio")
    id_negocio = request.form["id_negocio"]

    datos = (
        id_negocio,
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

    eliminar_servicio(id_servicio)
    flash("✅ Servicio eliminado correctamente.", "success")
    return redirect("/servicios")


# ================= VENTAS =================
@app.route("/ventas")
def ventas():
    return render_template("ventas_crear.html")


@app.route("/ventas/pendientes")
def ventas_pendientes():
    id_negocio = request.args.get("id_negocio") or None
    ventas = obtener_ventas_pendientes(id_negocio)
    negocios = obtener_negocios()  

    ventas_con_detalles = []
    for v in ventas:
        detalles = obtener_detalles_venta(v["id_venta"])
        v["detalles"] = detalles

        v["monto_prepago"] = v.get("monto_prepago", 0) or 0
        v["prepago"] = v.get("prepago", 0) or 0
        v["total"] = v.get("total", 0) or 0

        ventas_con_detalles.append(v)

    return render_template(
        "ventas_pendientes.html",
        ventas=ventas_con_detalles,
        negocios=negocios,  
        hoy=date.today()
    )




@app.route("/ventas/entregar/<int:id_venta>")
def entregar_venta(id_venta):
    ok = marcar_entregada(id_venta)

    if ok:
        flash("✅ Venta entregada correctamente.", "success")
    else:
        flash("⚠️ No se pudo entregar (ya estaba entregada o no existe).", "warning")

    return redirect("/ventas/pendientes")


@app.route("/ventas/guardar", methods=["POST"])
def guardar_venta():
    try:
        id_negocio = int(request.form["id_negocio"])
        id_cliente = request.form.get("id_cliente") or None
        fecha_estimada = request.form.get("fecha_estimada") or None
        tipo_pago = request.form.get("tipo_pago")
        fecha_recibo = datetime.now()

        prepago = request.form.get("prepago") == "si"
        monto_prepago = request.form.get("monto_prepago") if prepago else None

        aplica_descuento = request.form.get("aplica_descuento") == "si"
        cantidad_descuento = int(request.form.get("cantidad_descuento") or 0) if aplica_descuento else 0

        tipos_por_negocio = {
            1: "calzado",
            2: "confeccion",
            3: "maquila"
        }
        tipo_permitido = tipos_por_negocio.get(id_negocio)

        articulos = []
        i = 0

        while True:
            tipo_articulo = request.form.get(f"articulos[{i}][tipo_articulo]")
            if not tipo_articulo:
                break

            if tipo_permitido and tipo_articulo != tipo_permitido:
                return jsonify({
                    "ok": False,
                    "error": f"Este negocio solo permite artículos tipo: {tipo_permitido}"
                }), 400

            comentario = request.form.get(f"articulos[{i}][comentario]")

            if tipo_articulo == "calzado":
                datos = {
                    "tipo": request.form.get(f"articulos[{i}][tipo]"),
                    "marca": request.form.get(f"articulos[{i}][marca]"),
                    "material": request.form.get(f"articulos[{i}][material]"),
                    "color_base": request.form.get(f"articulos[{i}][color_base]"),
                    "color_secundario": request.form.get(f"articulos[{i}][color_secundario]"),
                    "color_agujetas": request.form.get(f"articulos[{i}][color_agujetas]")
                }

                servicios = []
                j = 0
                while True:
                    id_serv = request.form.get(f"articulos[{i}][servicios][{j}][id_servicio]")
                    if not id_serv:
                        break

                    precio_ap = request.form.get(f"articulos[{i}][servicios][{j}][precio_aplicado]") or 0

                    servicios.append({
                        "id_servicio": int(id_serv),
                        "precio_aplicado": float(precio_ap)
                    })

                    j += 1

                articulos.append({
                    "tipo_articulo": "calzado",
                    "datos": datos,
                    "servicios": servicios,
                    "comentario": comentario
                })

            elif tipo_articulo == "confeccion":
                datos = {
                    "tipo": request.form.get(f"articulos[{i}][tipo]"),
                    "marca": request.form.get(f"articulos[{i}][marca]"),
                    "material": request.form.get(f"articulos[{i}][material]"),
                    "color_base": request.form.get(f"articulos[{i}][color_base]"),
                    "color_secundario": request.form.get(f"articulos[{i}][color_secundario]"),
                    "cantidad": int(request.form.get(f"articulos[{i}][cantidad]") or 1),
                    "agujetas": request.form.get(f"articulos[{i}][agujetas]") == "1"
                }

                servicios = []
                j = 0
                while True:
                    id_serv = request.form.get(f"articulos[{i}][servicios][{j}][id_servicio]")
                    if not id_serv:
                        break

                    precio_ap = request.form.get(f"articulos[{i}][servicios][{j}][precio_aplicado]") or 0

                    servicios.append({
                        "id_servicio": int(id_serv),
                        "precio_aplicado": float(precio_ap)
                    })

                    j += 1

                articulos.append({
                    "tipo_articulo": "confeccion",
                    "datos": datos,
                    "servicios": servicios,
                    "comentario": comentario
                })

            elif tipo_articulo == "maquila":
                datos = {
                    "tipo": request.form.get(f"articulos[{i}][tipo]"),
                    "cantidad": int(request.form.get(f"articulos[{i}][cantidad]") or 1),
                    "precio_unitario": float(request.form.get(f"articulos[{i}][precio_unitario]") or 0),
                }

                articulos.append({
                    "tipo_articulo": "maquila",
                    "datos": datos,
                    "comentario": comentario
                })

            i += 1

        if not id_cliente or not tipo_pago or not fecha_estimada:
            return jsonify({
                "ok": False,
                "error": "Faltan datos obligatorios (cliente, negocio, fecha estimada o tipo de pago)."
            }), 400

        if len(articulos) == 0:
            return jsonify({
                "ok": False,
                "error": "Debes agregar al menos 1 artículo."
            }), 400

        if id_negocio in (1, 2):
            for a in articulos:
                if not a.get("servicios") or len(a["servicios"]) == 0:
                    return jsonify({
                        "ok": False,
                        "error": "Cada artículo debe tener al menos 1 servicio."
                    }), 400

                for s in a["servicios"]:
                    if not s.get("id_servicio"):
                        return jsonify({
                            "ok": False,
                            "error": "Servicio inválido (sin id)."
                        }), 400

                    if float(s.get("precio_aplicado") or 0) <= 0:
                        return jsonify({
                            "ok": False,
                            "error": "El precio aplicado debe ser mayor a 0."
                        }), 400

        if id_negocio == 3:
            for a in articulos:
                if a.get("servicios"):
                    return jsonify({
                        "ok": False,
                        "error": "Maquila no permite servicios."
                    }), 400

        id_venta = crear_venta(
            id_negocio=id_negocio,
            id_cliente=id_cliente,
            fecha_estimada=fecha_estimada,
            tipo_pago=tipo_pago,
            prepago=prepago,
            monto_prepago=monto_prepago,
            aplica_descuento=aplica_descuento,
            cantidad_descuento=cantidad_descuento,
            articulos=articulos
        )

        return jsonify({
            "ok": True,
            "id_venta": id_venta
        }), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": f"Error al guardar venta: {str(e)}"
        }), 500


@app.route("/ventas/ticket/<int:id_venta>")
def venta_ticket(id_venta):
    venta = obtener_venta(id_venta) 
    detalles = obtener_detalles_venta(id_venta)

    return render_template("ticket_venta.html", venta=venta, detalles=detalles)



# ================= GASTOS =================
@app.route("/gastos")
def gastos():
    proveedor = request.args.get("proveedor", "")
    pagina = request.args.get("pagina", 1, type=int)

    por_pagina = 10
    offset = (pagina - 1) * por_pagina

    negocios = obtener_negocios()

    total_gastos = contar_gastos(None, proveedor)
    total_paginas = (total_gastos + por_pagina - 1) // por_pagina

    gastos = obtener_gastos(
        id_negocio=None,
        q=proveedor,
        limit=por_pagina,
        offset=offset
    )

    return render_template(
        "gastos.html",
        gastos=gastos,
        negocios=negocios,
        proveedor=proveedor,
        pagina=pagina,
        total_paginas=total_paginas
    )





@app.route("/gastos/guardar", methods=["POST"])
def guardar_gasto():
    id_gasto = request.form.get("id_gasto")
    id_negocio = request.form["id_negocio"]

    datos = (
        id_negocio,
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
    negocios = obtener_negocios() 

    return render_template(
        "estadisticas.html",
        total_clientes=contar_clientes(),
        total_servicios=contar_servicios(),
        negocios=negocios,
        hoy=hoy
    )


@app.route("/api/estadisticas/dashboard")
def api_estadisticas_dashboard():
    inicio_str = request.args.get("inicio")
    fin_str = request.args.get("fin")
    id_negocio = request.args.get("id_negocio", "all")

    if not inicio_str or not fin_str:
        return jsonify({"error": "Faltan fechas"}), 400

    inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
    fin = datetime.strptime(fin_str, "%Y-%m-%d").date()

    if fin < inicio:
        return jsonify({"error": "La fecha fin no puede ser menor a inicio"}), 400

    ventas_semanales = contar_ventas_por_semana(inicio, fin, id_negocio)
    gastos_semanales = obtener_gastos_por_semana_y_proveedor(inicio, fin, id_negocio)
    total_gastos = obtener_total_gastos(inicio, fin, id_negocio)
    unidades_semanales = obtener_unidades_por_semana(inicio, fin, id_negocio)



    return jsonify({
        "ventas_semanales": ventas_semanales,
        "gastos_semanales": gastos_semanales,
        "unidades_semanales": unidades_semanales,
        "kpis": {
            "ventas": 0,
            "gastos": total_gastos,
            "ganancia": 0
        }
    })






# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
    