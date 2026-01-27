from db import get_connection


def crear_gasto(id_negocio, descripcion, proveedor, total, fecha_registro):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO gastos (id_negocio, descripcion, proveedor, total, fecha_registro)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (id_negocio, descripcion, proveedor, total, fecha_registro))
    conn.commit()

    cursor.close()
    conn.close()


def actualizar_gasto(id_gasto, id_negocio, descripcion, proveedor, total, fecha_registro):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gastos
        SET id_negocio=%s,
            descripcion=%s,
            proveedor=%s,
            total=%s,
            fecha_registro=%s
        WHERE id_gasto=%s
    """, (id_negocio, descripcion, proveedor, total, fecha_registro, id_gasto))

    conn.commit()
    cursor.close()
    conn.close()


def eliminar_gasto(id_gasto):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM gastos WHERE id_gasto=%s",
        (id_gasto,)
    )

    conn.commit()
    cursor.close()
    conn.close()


def obtener_gastos(
    id_negocio=None,
    fecha_inicio=None,
    fecha_fin=None,
    limit=10,
    offset=0
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT 
            g.id_gasto,
            g.id_negocio,
            n.nombre AS negocio,
            g.descripcion,
            g.proveedor,
            g.total,
            g.fecha_registro
        FROM gastos g
        JOIN Negocio n ON g.id_negocio = n.id_negocio
    """

    params = []
    where = []

    if id_negocio:
        where.append("g.id_negocio = %s")
        params.append(id_negocio)

    if fecha_inicio:
        where.append("g.fecha_registro >= %s")
        params.append(fecha_inicio)

    if fecha_fin:
        where.append("g.fecha_registro <= %s")
        params.append(fecha_fin)

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY g.fecha_registro DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(sql, params)
    gastos = cursor.fetchall()

    cursor.close()
    conn.close()
    return gastos




def obtener_gastos_por_proveedor(id_negocio, fecha_inicio, fecha_fin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT proveedor, SUM(total) AS total
        FROM gastos
        WHERE id_negocio = %s
          AND fecha_registro BETWEEN %s AND %s
        GROUP BY proveedor
        ORDER BY total DESC
    """, (id_negocio, fecha_inicio, fecha_fin))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados


def contar_gastos(id_negocio=None, fecha_inicio=None, fecha_fin=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT COUNT(*) FROM gastos WHERE 1=1"
    params = []

    if id_negocio:
        sql += " AND id_negocio = %s"
        params.append(id_negocio)

    if fecha_inicio:
        sql += " AND fecha_registro >= %s"
        params.append(fecha_inicio)

    if fecha_fin:
        sql += " AND fecha_registro <= %s"
        params.append(fecha_fin)

    cursor.execute(sql, params)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total

