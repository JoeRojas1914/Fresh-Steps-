from collections import defaultdict
from db import get_connection
from datetime import date, timedelta

def generar_semanas_rango(inicio: date, fin: date):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    def fecha_bonita(d: date):
        return f"{d.day} {meses[d.month - 1]}"

    inicio_lunes = inicio - timedelta(days=inicio.weekday())

    semanas = []
    actual = inicio_lunes
    num_semana = 1

    while actual <= fin:
        semana_fin = actual + timedelta(days=6)

        label = [
            f"Semana {num_semana}",
            f"{fecha_bonita(actual)} - {fecha_bonita(semana_fin)}"
        ]

        semanas.append({
            "inicio": actual,
            "fin": semana_fin,
            "label": label
        })

        actual += timedelta(days=7)
        num_semana += 1

    return semanas



def contar_ventas_por_semana(inicio: date, fin: date, id_negocio: str):
    semanas = generar_semanas_rango(inicio, fin)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    resultados = []

    for s in semanas:
        semana_inicio_real = max(s["inicio"], inicio)
        semana_fin_real = min(s["fin"], fin)

        query = """
            SELECT COUNT(*) AS total
            FROM venta
            WHERE fecha_recibo >= %s
              AND fecha_recibo <= %s
        """
        params = [semana_inicio_real, semana_fin_real]

        if id_negocio != "all":
            query += " AND id_negocio = %s"
            params.append(id_negocio)

        cursor.execute(query, params)
        total = cursor.fetchone()["total"]

        resultados.append({
            "label": s["label"],
            "total": total
        })

    cursor.close()
    conn.close()

    return resultados


def obtener_gastos_por_semana_y_proveedor(inicio: date, fin: date, id_negocio: str):
    semanas = generar_semanas_rango(inicio, fin)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    data_por_proveedor = defaultdict(lambda: [0] * len(semanas))

    for i, s in enumerate(semanas):
        semana_inicio_real = max(s["inicio"], inicio)
        semana_fin_real = min(s["fin"], fin)

        query = """
            SELECT proveedor, SUM(total) AS total
            FROM gastos
            WHERE fecha_registro >= %s
              AND fecha_registro <= %s
        """
        params = [semana_inicio_real, semana_fin_real]

        if id_negocio != "all":
            query += " AND id_negocio = %s"
            params.append(id_negocio)

        query += " GROUP BY proveedor"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for r in rows:
            proveedor = r["proveedor"] or "Sin proveedor"
            total = float(r["total"] or 0)
            data_por_proveedor[proveedor][i] = total

    cursor.close()
    conn.close()

    labels = [s["label"] for s in semanas]

    datasets = []
    for proveedor, valores in data_por_proveedor.items():
        datasets.append({
            "label": proveedor,
            "data": valores
        })

    return {
        "labels": labels,
        "datasets": datasets
    }



def obtener_total_gastos(inicio: date, fin: date, id_negocio: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT COALESCE(SUM(total), 0) AS total
        FROM gastos
        WHERE fecha_registro >= %s
          AND fecha_registro <= %s
    """
    params = [inicio, fin]

    if id_negocio != "all":
        query += " AND id_negocio = %s"
        params.append(id_negocio)

    cursor.execute(query, params)
    total = cursor.fetchone()["total"] or 0

    cursor.close()
    conn.close()

    return float(total)
