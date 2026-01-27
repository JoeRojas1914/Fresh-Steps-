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



def obtener_unidades_por_semana(inicio: date, fin: date, id_negocio: str):
    semanas = generar_semanas_rango(inicio, fin)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    resultados = []

    for s in semanas:
        semana_inicio = max(s["inicio"], inicio)
        semana_fin = min(s["fin"], fin)

        total_unidades = 0


        if id_negocio in ("1", "all"):
            query = """
                SELECT COUNT(a.id_articulo) AS total
                FROM venta v
                JOIN articulo a ON a.id_venta = v.id_venta
                WHERE v.fecha_recibo BETWEEN %s AND %s
                  AND v.id_negocio = 1
            """
            cursor.execute(query, [semana_inicio, semana_fin])
            total_unidades += cursor.fetchone()["total"] or 0


        if id_negocio in ("2", "all"):
            query = """
                SELECT SUM(ac.cantidad) AS total
                FROM venta v
                JOIN articulo a ON a.id_venta = v.id_venta
                JOIN articulo_confeccion ac ON ac.id_articulo = a.id_articulo
                WHERE v.fecha_recibo BETWEEN %s AND %s
                  AND v.id_negocio = 2
            """
            cursor.execute(query, [semana_inicio, semana_fin])
            total_unidades += cursor.fetchone()["total"] or 0


        if id_negocio in ("3", "all"):
            query = """
                SELECT SUM(am.cantidad) AS total
                FROM venta v
                JOIN articulo a ON a.id_venta = v.id_venta
                JOIN articulo_maquila am ON am.id_articulo = a.id_articulo
                WHERE v.fecha_recibo BETWEEN %s AND %s
                  AND v.id_negocio = 3
            """
            cursor.execute(query, [semana_inicio, semana_fin])
            total_unidades += cursor.fetchone()["total"] or 0

        resultados.append({
            "label": s["label"],
            "total": int(total_unidades)
        })

    cursor.close()
    conn.close()

    return resultados


def obtener_total_ingresos(inicio: date, fin: date, id_negocio: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN fecha_entrega IS NOT NULL THEN total
                    ELSE monto_prepago
                END
            ), 0) AS total
        FROM venta
        WHERE fecha_recibo BETWEEN %s AND %s
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


def obtener_ingresos_por_semana(inicio: date, fin: date, id_negocio: str):
    semanas = generar_semanas_rango(inicio, fin)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    resultados = []

    for s in semanas:
        semana_inicio = max(s["inicio"], inicio)
        semana_fin = min(s["fin"], fin)

        query = """
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN fecha_entrega IS NOT NULL THEN total
                        ELSE monto_prepago
                    END
                ), 0) AS total
            FROM venta
            WHERE fecha_recibo BETWEEN %s AND %s
        """
        params = [semana_inicio, semana_fin]

        if id_negocio != "all":
            query += " AND id_negocio = %s"
            params.append(id_negocio)

        cursor.execute(query, params)
        total = cursor.fetchone()["total"] or 0

        resultados.append({
            "label": s["label"],
            "total": float(total)
        })

    cursor.close()
    conn.close()

    return resultados

def ejecutar_query(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or [])
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows



def obtener_uso_servicios(inicio, fin, id_negocio):
    conn = get_connection()
    sql = """
        SELECT s.nombre, COUNT(*) total
        FROM articulo_servicio aps
        JOIN servicio s ON s.id_servicio = aps.id_servicio
        JOIN articulo a ON a.id_articulo = aps.id_articulo
        JOIN venta v ON v.id_venta = a.id_venta
        WHERE DATE(v.fecha_recibo) BETWEEN %s AND %s
    """
    params = [inicio, fin]

    if id_negocio != "all":
        sql += " AND v.id_negocio = %s"
        params.append(id_negocio)

    sql += " GROUP BY s.id_servicio ORDER BY total DESC"

    return ejecutar_query(sql, params)


def obtener_ventas_por_tipo_pago(inicio, fin, id_negocio):
    sql = """
        SELECT tipo_pago, COUNT(*) total
        FROM venta
        WHERE DATE(fecha_recibo) BETWEEN %s AND %s
    """
    params = [inicio, fin]

    if id_negocio != "all":
        sql += " AND id_negocio = %s"
        params.append(id_negocio)

    sql += " GROUP BY tipo_pago"

    return ejecutar_query(sql, params)


def obtener_ventas_por_dia(inicio, fin, id_negocio):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            WEEKDAY(fecha_recibo) AS dia,
            COUNT(*) AS total
        FROM venta
        WHERE DATE(fecha_recibo) BETWEEN %s AND %s
          AND WEEKDAY(fecha_recibo) BETWEEN 0 AND 5
    """
    params = [inicio, fin]

    if id_negocio != "all":
        sql += " AND id_negocio = %s"
        params.append(id_negocio)

    sql += " GROUP BY dia"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    dias = [0, 0, 0, 0, 0, 0]
    for r in rows:
        dias[r["dia"]] = r["total"]

    return dias
