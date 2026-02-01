from flask import session, redirect, url_for, flash, render_template, request
from datetime import datetime, timedelta

RUTAS_PUBLICAS = [
    "auth.login",
    "static"
]

RUTAS_CAJA = [
    "index",
    "ventas",
    "guardar_venta",
    "ventas_pendientes",
    "entregar_venta",
    "auth.logout",
    "registrar_pago_final",
    "venta_ticket",
    "clientes.api_clientes",
    "clientes.api_crear_cliente",
    "servicios.api_servicios",
]

TIMEOUT_CAJA = 20
TIMEOUT_ADMIN = 15


def init_auth_middleware(app):

    @app.before_request
    def control_acceso():

        endpoint = request.endpoint

        if endpoint is None:
            return

        if endpoint.startswith("static"):
            return


        hoy = datetime.now().date().isoformat()


        if endpoint == "auth.pin_login":

            if session.get("pin_habilitado_fecha") == hoy:
                return

            return redirect(url_for("auth.login"))


        if endpoint == "auth.login" and not request.args.get("admin"):

            if session.get("pin_habilitado_fecha") == hoy:
                return redirect(url_for("auth.pin_login"))


        if endpoint in RUTAS_PUBLICAS:
            return


        if not session.get("id_usuario"):
            return redirect(url_for("auth.pin_login"))


        ultima = session.get("ultima_actividad")

        if ultima:
            ultima = datetime.fromisoformat(ultima)
            ahora = datetime.now()

            limite = (
                TIMEOUT_ADMIN if session.get("rol") == "admin"
                else TIMEOUT_CAJA
            )

            if ahora - ultima > timedelta(minutes=limite):
                session.clear()

                if session.get("pin_habilitado_fecha") == hoy:
                    return redirect(url_for("auth.pin_login"))

                return redirect(url_for("auth.login"))

        session["ultima_actividad"] = datetime.now().isoformat()

        if session.get("rol") == "admin":
            return

        if session.get("rol") == "caja" and endpoint in RUTAS_CAJA:
            return

        return render_template("403.html"), 403
