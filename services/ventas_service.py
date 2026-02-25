from datetime import date

from ventas import (
    marcar_entregada,
    obtener_ventas_listas,
    obtener_detalles_venta,
    obtener_entregas_pendientes
)

from pagos import (
    obtener_pagos_venta,
    registrar_pago_final_db
)

from negocio import obtener_negocios


def listar_ventas_listas_service(id_negocio=None):
    ventas = obtener_ventas_listas(id_negocio)
    negocios = obtener_negocios()

    ventas_con_detalles = []

    for v in ventas:
        v["detalles"] = obtener_detalles_venta(v["id_venta"])

        pagos = obtener_pagos_venta(v["id_venta"])
        v["pagos"] = pagos

        total_pagado = sum(float(p["monto"]) for p in pagos)
        total = float(v.get("total") or 0)

        v["total"] = total
        v["total_pagado"] = total_pagado
        v["saldo_pendiente"] = max(total - total_pagado, 0)

        v["tiene_pagos"] = total_pagado > 0
        v["esta_pagada"] = v["saldo_pendiente"] == 0

        ventas_con_detalles.append(v)

    return {
        "ventas": ventas_con_detalles,
        "negocios": negocios,
        "hoy": date.today()
    }


def listar_entregas_pendientes_service(id_negocio=None):
    ventas = obtener_entregas_pendientes(id_negocio)
    negocios = obtener_negocios()

    ventas_con_detalles = []

    for v in ventas:
        v["detalles"] = obtener_detalles_venta(v["id_venta"])
        ventas_con_detalles.append(v)

    return {
        "ventas": ventas_con_detalles,
        "negocios": negocios,
        "hoy": date.today()
    }


def registrar_pago_final_service(data, id_usuario):
    id_venta = data.get("id_venta")
    monto = data.get("monto")
    metodo_pago = data.get("metodo_pago")

    if not id_venta or not monto or not metodo_pago:
        return False, "Datos incompletos para el pago final"

    registrar_pago_final_db(
        id_venta=id_venta,
        monto=monto,
        metodo_pago=metodo_pago,
        id_usuario=id_usuario
    )

    marcar_entregada(id_venta, id_usuario)

    return True, "Pago final registrado y venta marcada como entregada"