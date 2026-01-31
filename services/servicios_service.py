from servicios import (
    contar_servicios,
    obtener_servicios,
    crear_servicio,
    actualizar_servicio,
    eliminar_servicio
)

def listar_servicios(id_negocio=None, q="", pagina=1, por_pagina=10):
    offset = (pagina - 1) * por_pagina

    total = contar_servicios(id_negocio=id_negocio, q=q)
    total_paginas = (total + por_pagina - 1) // por_pagina

    servicios = obtener_servicios(
        id_negocio=id_negocio,
        q=q,
        limit=por_pagina,
        offset=offset
    )

    return {
        "servicios": servicios,
        "total_paginas": total_paginas,
        "total": total
    }


def guardar_servicio_service(id_servicio, id_negocio, nombre, precio):
    if id_servicio:
        actualizar_servicio(id_servicio, id_negocio, nombre, precio)
        return "actualizado"
    else:
        crear_servicio(id_negocio, nombre, precio)
        return "creado"


def eliminar_servicio_service(id_servicio):
    eliminar_servicio(id_servicio)
