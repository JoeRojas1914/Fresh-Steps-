import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from flask_wtf import CSRFProtect



from routes.servicios_routes import servicios_bp
from routes.gastos_routes import gastos_bp
from routes.clientes_routes import clientes_bp
from routes.estadisticas_routes import estadisticas_bp
from routes.auth_routes import auth_bp
from routes.usuarios_routes import usuarios_bp
from routes.ventas_routes import ventas_bp
from middleware.auth_middleware import init_auth_middleware


# ================= IMPORTS DE MODULOS =================
from pagos import (
    registrar_pago
    )

from ventas import (
    contar_entregas_pendientes,
    crear_venta,
    contar_entregas_listas,
)


# ================= APP =================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
csrf = CSRFProtect()
csrf.init_app(app)
app.register_blueprint(servicios_bp)
app.register_blueprint(gastos_bp)
app.register_blueprint(clientes_bp)
csrf.exempt(clientes_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(ventas_bp)
init_auth_middleware(app)

# ================= HOME =================
@app.route("/")
def index():

    hoy = date.today().isoformat()

    if not session.get("id_usuario"):

        if session.get("pin_habilitado_fecha") == hoy:
            return redirect(url_for("auth.pin_login"))

        return redirect(url_for("auth.login"))


    return render_template(
        "index.html",
        total_entregas = contar_entregas_listas(),
        total_pendientes = contar_entregas_pendientes(),
        nombre_usuario=session.get("usuario")
    )





# ================= VENTAS =================
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



# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
    