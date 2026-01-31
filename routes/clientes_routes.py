from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from services.clientes_service import (
    listar_clientes_service,
    guardar_cliente_service,
    eliminar_cliente_service,
    buscar_clientes_service,
    obtener_cliente_detalle_service
)

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/clientes")
def clientes():
    q = request.args.get("q", "")
    pagina = request.args.get("pagina", 1, type=int)

    data = listar_clientes_service(q, pagina)

    return render_template(
        "clientes.html",
        clientes=data["clientes"],
        q=q,
        pagina=pagina,
        total_paginas=data["total_paginas"]
    )

@clientes_bp.route("/clientes/guardar", methods=["POST"])
def guardar_cliente():
    resultado = guardar_cliente_service(request.form)

    if resultado == "actualizado":
        flash("✅ Cliente actualizado correctamente.", "success")
    else:
        flash("✅ Cliente creado correctamente.", "success")

    return redirect(url_for("clientes.clientes"))

@clientes_bp.route("/clientes/eliminar/<int:id_cliente>")
def eliminar_cliente(id_cliente):
    eliminar_cliente_service(id_cliente)
    flash("✅ Cliente eliminado correctamente.", "success")
    return redirect(url_for("clientes.clientes"))


@clientes_bp.route("/api/clientes")
def api_clientes():
    q = request.args.get("q", "")
    return jsonify(buscar_clientes_service(q))


@clientes_bp.route("/api/clientes/crear", methods=["POST"])
def api_crear_cliente():
    cliente = guardar_cliente_service(request.form, api=True)
    return jsonify(cliente)

@clientes_bp.route("/clientes/<int:id_cliente>")
def ver_cliente(id_cliente):
    filtros = request.args
    data = obtener_cliente_detalle_service(id_cliente, filtros)

    return render_template("cliente_perfil.html", **data)
