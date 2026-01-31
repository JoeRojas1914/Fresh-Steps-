from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime

from services.auth_service import (
    login_password_service,
    login_pin_service
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = login_password_service(
            request.form.get("usuario"),
            request.form.get("password"),
            request.remote_addr
        )

        if not usuario:
            flash("❌ Usuario o contraseña incorrectos", "error")
            return render_template("login.html")

        session["id_usuario"] = usuario["id_usuario"]
        session["usuario"] = usuario["usuario"]
        session["rol"] = usuario["rol"]
        session["ultima_actividad"] = datetime.now().isoformat()

        return redirect(url_for("index"))

    return render_template("login.html")


@auth_bp.route("/pin", methods=["GET", "POST"])
def pin_login():

    if request.method == "POST":

        usuario = login_pin_service(
            request.form.get("pin"),
            request.remote_addr
        )

        if not usuario:
            flash("❌ PIN incorrecto", "error")
            return render_template("pin.html")

        session.clear()

        session["id_usuario"] = usuario["id_usuario"]
        session["usuario"] = usuario["usuario"]
        session["rol"] = "caja"
        session["ultima_actividad"] = datetime.now().isoformat()

        return redirect(url_for("index"))

    return render_template("pin.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
