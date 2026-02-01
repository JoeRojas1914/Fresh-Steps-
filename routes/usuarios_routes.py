from flask import Blueprint, render_template, request, redirect, session, jsonify
from services.usuarios_service import (
    listar_usuarios_service,
    guardar_usuario_service,
    toggle_usuario_service,
    obtener_historial_usuario_service
)

usuarios_bp = Blueprint("usuarios", __name__)


def admin_required():
    return session.get("rol") == "admin"


@usuarios_bp.route("/usuarios")
def listar_usuarios():

    if not admin_required():
        return redirect("/")

    usuarios = listar_usuarios_service()

    return render_template("usuarios.html", usuarios=usuarios)




@usuarios_bp.route("/usuarios/guardar", methods=["POST"])
def guardar_usuario():

    if not admin_required():
        return redirect("/")

    guardar_usuario_service(
        request.form.get("id_usuario"),
        request.form.get("usuario"),
        request.form.get("password"),
        request.form.get("rol"),
        request.form.get("pin")
    )

    return redirect("/usuarios")



@usuarios_bp.route("/usuarios/toggle/<int:id>")
def toggle_usuario(id):

    if not admin_required():
        return redirect("/")

    toggle_usuario_service(id)

    return redirect("/usuarios")


@usuarios_bp.route("/usuarios/<int:id>/historial")
def historial_usuario(id):

    if not admin_required():
        return jsonify([])

    historial = obtener_historial_usuario_service(id)

    return jsonify(historial)

