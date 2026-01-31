from datetime import date, datetime
from clientes import contar_clientes
from servicios import contar_servicios
from negocio import obtener_negocios

from estadisticas import (
    contar_ventas_por_semana,
    obtener_gastos_por_semana_y_proveedor,
    obtener_total_gastos,
    obtener_total_ingresos,
    obtener_unidades_por_semana,
    obtener_ingresos_por_semana,
    obtener_ventas_con_y_sin_prepago,
    obtener_uso_servicios,
    obtener_ventas_por_dia
)


def dashboard_page_data_service():
    hoy = date.today()

    fecha_inicio = hoy.replace(day=1)
    fecha_fin = hoy

    return {
        "total_clientes": contar_clientes(),
        "total_servicios": contar_servicios(),
        "negocios": obtener_negocios(),
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat()
    }


def dashboard_api_service(args):

    inicio_str = args.get("inicio")
    fin_str = args.get("fin")
    id_negocio = args.get("id_negocio", "all")

    if not inicio_str or not fin_str:
        return None, "Faltan fechas"

    inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
    fin = datetime.strptime(fin_str, "%Y-%m-%d").date()

    if fin < inicio:
        return None, "La fecha fin no puede ser menor a inicio"
    
    ventas_semanales = contar_ventas_por_semana(inicio, fin, id_negocio)
    gastos_semanales = obtener_gastos_por_semana_y_proveedor(inicio, fin, id_negocio)

    total_gastos = obtener_total_gastos(inicio, fin, id_negocio)
    total_ingresos = obtener_total_ingresos(inicio, fin, id_negocio)

    ingresos_semanales = obtener_ingresos_por_semana(inicio, fin, id_negocio)
    unidades_semanales = obtener_unidades_por_semana(inicio, fin, id_negocio)

    ventas_prepago = obtener_ventas_con_y_sin_prepago(inicio, fin, id_negocio)
    uso_servicios = obtener_uso_servicios(inicio, fin, id_negocio)
    ventas_por_dia = obtener_ventas_por_dia(inicio, fin, id_negocio)

    return {
        "ventas_semanales": ventas_semanales,
        "gastos_semanales": gastos_semanales,
        "ingresos_semanales": ingresos_semanales,
        "unidades_semanales": unidades_semanales,
        "ventas_prepago": ventas_prepago,
        "uso_servicios": uso_servicios,
        "ventas_por_dia": ventas_por_dia,
        "kpis": {
            "ingresos": total_ingresos,
            "gastos": total_gastos,
            "ganancia": total_ingresos - total_gastos
        }
    }, None

