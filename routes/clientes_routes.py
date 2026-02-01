from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session

from services.clientes_service import (
    listar_clientes_service,
    guardar_cliente_service,
    eliminar_cliente_service,
    restaurar_cliente_service,
    buscar_clientes_service,
    obtener_cliente_detalle_service,
    obtener_historial_cliente_service
)

clientes_bp = Blueprint("clientes", __name__)



@clientes_bp.route("/clientes")
def clientes():

    q = request.args.get("q", "")
    pagina = request.args.get("pagina", 1, type=int)
    incluir_eliminados = request.args.get("eliminados") == "1"

    data = listar_clientes_service(
        q=q,
        pagina=pagina,
        incluir_eliminados=incluir_eliminados
    )

    return render_template(
        "clientes.html",
        clientes=data["clientes"],
        q=q,
        pagina=pagina,
        total_paginas=data["total_paginas"],
        incluir_eliminados=incluir_eliminados
    )



@clientes_bp.route("/clientes/guardar", methods=["POST"])
def guardar_cliente():

    id_usuario = session["id_usuario"]

    resultado = guardar_cliente_service(request.form, id_usuario)

    flash(
        "✅ Cliente actualizado correctamente." if resultado == "actualizado"
        else "✅ Cliente creado correctamente.",
        "success"
    )

    return redirect(url_for("clientes.clientes"))



@clientes_bp.route("/clientes/eliminar/<int:id_cliente>")
def eliminar_cliente(id_cliente):

    id_usuario = session["id_usuario"]

    ok = eliminar_cliente_service(id_cliente, id_usuario)

    if not ok:
        flash("❌ No puedes eliminar el cliente porque ya tiene ventas registradas.", "error")
    else:
        flash("🗑️ Cliente eliminado correctamente.", "success")

    return redirect(url_for("clientes.clientes"))



@clientes_bp.route("/clientes/restaurar/<int:id_cliente>")
def restaurar_cliente(id_cliente):

    id_usuario = session["id_usuario"]

    restaurar_cliente_service(id_cliente, id_usuario)

    flash("♻️ Cliente restaurado correctamente.", "success")

    return redirect(request.referrer or url_for("clientes.clientes"))



@clientes_bp.route("/clientes/<int:id_cliente>/historial")
def historial_cliente(id_cliente):
    return jsonify(obtener_historial_cliente_service(id_cliente))



@clientes_bp.route("/api/clientes")
def api_clientes():
    q = request.args.get("q", "")
    return jsonify(buscar_clientes_service(q))


@clientes_bp.route("/clientes/<int:id_cliente>")
def ver_cliente(id_cliente):
    filtros = request.args
    data = obtener_cliente_detalle_service(id_cliente, filtros)
    return render_template("cliente_perfil.html", **data)

