import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv
from db import get_connection
from werkzeug.security import check_password_hash


from routes.servicios_routes import servicios_bp
from routes.gastos_routes import gastos_bp
from routes.clientes_routes import clientes_bp
from routes.estadisticas_routes import estadisticas_bp
from routes.auth_routes import auth_bp
from routes.usuarios_routes import usuarios_bp
from middleware.auth_middleware import init_auth_middleware


# ================= IMPORTS DE MODULOS =================
from pagos import (
    obtener_pagos_venta, 
    registrar_pago
    )

from ventas import (
    crear_venta,
    marcar_entregada,
    obtener_venta,
    obtener_ventas_pendientes,
    obtener_detalles_venta,
    contar_entregas_pendientes,
)

from negocio import obtener_negocios

# ================= APP =================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.register_blueprint(servicios_bp)
app.register_blueprint(gastos_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
init_auth_middleware(app)

# ================= HOME =================
@app.route("/")
def index():
    if not session.get("id_usuario"):
        return redirect(url_for("login"))

    total_entregas = contar_entregas_pendientes()

    return render_template(
        "index.html",
        total_entregas=total_entregas,
        nombre_usuario=session.get("usuario") 
    )



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
        v["detalles"] = obtener_detalles_venta(v["id_venta"])

        pagos = obtener_pagos_venta(v["id_venta"])
        v["pagos"] = pagos

        total_pagado = sum(float(p["monto"]) for p in pagos)

        v["total"] = float(v.get("total") or 0)
        v["total_pagado"] = total_pagado
        v["saldo_pendiente"] = max(v["total"] - total_pagado, 0)

        v["tiene_pagos"] = total_pagado > 0
        v["esta_pagada"] = v["saldo_pendiente"] == 0

        ventas_con_detalles.append(v)

    return render_template(
        "ventas_pendientes.html",
        ventas=ventas_con_detalles,
        negocios=negocios,
        hoy=date.today()
    )


@app.route("/ventas/entregar/<int:id_venta>", methods=["POST"])
def entregar_venta(id_venta):

    id_usuario = session["id_usuario"]

    try:
        if marcar_entregada(id_venta, id_usuario):
            flash("✅ Venta entregada correctamente", "success")
        else:
            flash("⚠️ La venta ya fue entregada o no existe", "warning")

    except Exception as e:
        flash(f"❌ Error: {e}", "error")

    return redirect(url_for("ventas_pendientes"))


@app.route("/ventas/pago-final", methods=["POST"])
def registrar_pago_final():
    data = request.json

    id_usuario = session["id_usuario"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO pago_venta (
                id_venta,
                monto,
                tipo_pago,
                tipo_pago_venta,
                fecha_pago,
                id_usuario_cobro
            )
            VALUES (%s, %s, %s, 'final', NOW(), %s)
        """, (
            data["id_venta"],
            data["monto"],
            data["metodo_pago"],
            id_usuario
        ))

        conn.commit()

        marcar_entregada(data["id_venta"], id_usuario)

        return jsonify({"ok": True})

    except Exception as e:
        conn.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@app.route("/ventas/guardar", methods=["POST"])
def guardar_venta():
    try:
        id_negocio = int(request.form["id_negocio"])
        id_cliente = request.form.get("id_cliente") or None
        fecha_estimada = request.form.get("fecha_estimada") or None
        tipo_pago = request.form.get("tipo_pago")
        id_usuario_creo = session.get("id_usuario")


        prepago = request.form.get("prepago") == "si"
        monto_prepago = (
            float(request.form.get("monto_prepago") or 0)
            if prepago
            else 0
        )


        aplica_descuento = request.form.get("aplica_descuento") == "si"
        cantidad_descuento = (
            float(request.form.get("cantidad_descuento") or 0)
            if aplica_descuento
            else 0
        )


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

        if not id_cliente or not fecha_estimada:
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
            aplica_descuento=aplica_descuento,
            cantidad_descuento=cantidad_descuento,
            articulos=articulos,
            id_usuario_creo=id_usuario_creo
        )

        if prepago and monto_prepago > 0:
            if not tipo_pago:
                return jsonify({
                    "ok": False,
                    "error": "Debes seleccionar el tipo de pago del prepago."
                }), 400

            registrar_pago(
                id_venta=id_venta,
                monto=monto_prepago,
                tipo_pago=tipo_pago,
                id_usuario_cobro=session.get("id_usuario")
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

    return render_template(
        "ticket_venta.html",
        venta=venta,
        detalles=detalles
    )


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
    