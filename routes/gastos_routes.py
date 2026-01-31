from flask import Blueprint, render_template, request, redirect, flash, url_for, session, jsonify

from services.gastos_service import (
    listar_gastos,
    guardar_gasto_service,
    eliminar_gasto_service,
    obtener_historial_gasto
)

from negocio import obtener_negocios


gastos_bp = Blueprint("gastos", __name__)


@gastos_bp.route("/gastos")
def gastos():

    id_negocio = request.args.get("id_negocio")
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    pagina = request.args.get("pagina", 1, type=int)

    data = listar_gastos(
        id_negocio=id_negocio,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        pagina=pagina
    )

    return render_template(
        "gastos.html",
        gastos=data["gastos"],
        negocios=obtener_negocios(),
        pagina=pagina,
        total_paginas=data["total_paginas"]
    )


@gastos_bp.route("/gastos/guardar", methods=["POST"])
def guardar_gasto():

    id_gasto = request.form.get("id_gasto")

    id_usuario = session["id_usuario"]

    datos = (
        request.form["id_negocio"],
        request.form["descripcion"],
        request.form["proveedor"],
        request.form["total"],
        request.form["fecha_registro"]
    )

    resultado = guardar_gasto_service(id_gasto, datos, id_usuario)

    if resultado == "actualizado":
        flash("✅ Gasto editado correctamente.", "success")
    else:
        flash("✅ Gasto creado correctamente.", "success")

    return redirect(url_for("gastos.gastos"))


@gastos_bp.route("/gastos/eliminar/<int:id_gasto>")
def eliminar_gasto(id_gasto):

    id_usuario = session["id_usuario"]

    eliminar_gasto_service(id_gasto, id_usuario)

    flash("✅ Gasto eliminado correctamente.", "success")
    return redirect(url_for("gastos.gastos"))


@gastos_bp.route("/gastos/<int:id_gasto>/historial")
def historial_gasto(id_gasto):
    data = obtener_historial_gasto(id_gasto)
    return jsonify(data)