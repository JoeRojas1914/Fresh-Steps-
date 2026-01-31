from gastos import (
    crear_gasto,
    actualizar_gasto,
    obtener_gastos,
    eliminar_gasto,
    contar_gastos,
    obtener_historial_gasto
)


def listar_gastos(id_negocio=None, fecha_inicio=None, fecha_fin=None, pagina=1, por_pagina=10):
    offset = (pagina - 1) * por_pagina

    total = contar_gastos(
        id_negocio=id_negocio,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

    total_paginas = (total + por_pagina - 1) // por_pagina

    gastos = obtener_gastos(
        id_negocio=id_negocio,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=por_pagina,
        offset=offset
    )

    return {
        "gastos": gastos,
        "total": total,
        "total_paginas": total_paginas
    }


def guardar_gasto_service(id_gasto, datos, id_usuario):
    if id_gasto:
        actualizar_gasto(id_gasto, *datos, id_usuario)
        return "actualizado"
    else:
        crear_gasto(*datos, id_usuario)
        return "creado"



def eliminar_gasto_service(id_gasto, id_usuario):
    eliminar_gasto(id_gasto, id_usuario)

def obtener_historial_gasto_service(id_gasto):
    return obtener_historial_gasto(id_gasto)

