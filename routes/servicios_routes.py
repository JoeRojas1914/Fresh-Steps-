from flask import Blueprint, render_template, request, redirect, flash, jsonify


from services.servicios_service import (
    listar_servicios,
    guardar_servicio_service,
    eliminar_servicio_service
)
from negocio import obtener_negocios

servicios_bp = Blueprint("servicios", __name__)

@servicios_bp.route("/servicios")
def servicios():
    q = request.args.get("q", "")
    id_negocio = request.args.get("id_negocio", type=int)
    pagina = request.args.get("pagina", 1, type=int)

    por_pagina = 10

    data = listar_servicios(
        id_negocio=id_negocio,
        q=q,
        pagina=pagina,
        por_pagina=por_pagina
    )

    negocios = obtener_negocios()

    return render_template(
        "servicios.html",
        servicios=data["servicios"],
        negocios=negocios,
        id_negocio=id_negocio,
        q=q,
        pagina=pagina,
        total_paginas=data["total_paginas"]
    )


@servicios_bp.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    id_servicio = request.form.get("id_servicio")
    id_negocio = request.form["id_negocio"]
    nombre = request.form["nombre"]
    precio = request.form["precio"]

    resultado = guardar_servicio_service(
        id_servicio=id_servicio,
        id_negocio=id_negocio,
        nombre=nombre,
        precio=precio
    )

    if resultado == "actualizado":
        flash("✅ Servicio actualizado correctamente.", "success")
    else:
        flash("✅ Servicio creado correctamente.", "success")

    return redirect("/servicios")


@servicios_bp.route("/servicios/eliminar/<int:id_servicio>")
def eliminar_servicio(id_servicio):
    eliminar_servicio_service(id_servicio)
    flash("✅ Servicio eliminado correctamente.", "success")
    return redirect("/servicios")


@servicios_bp.route("/api/servicios")
def api_servicios():
    id_negocio = request.args.get("id_negocio", type=int)

    data = listar_servicios(
        id_negocio=id_negocio,
        pagina=1,
        por_pagina=1000
    )

    return jsonify(data["servicios"])

