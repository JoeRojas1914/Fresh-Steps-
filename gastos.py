from db import get_connection

def crear_gasto(descripcion, proveedor, total, fecha_registro):
    conn = get_connection()
    cursor = conn.cursor()


    sql = """
    INSERT INTO gastos (descripcion, proveedor, total, fecha_registro)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (descripcion, proveedor, total, fecha_registro))
    conn.commit()

    cursor.close()
    conn.close()


def actualizar_gasto(id_gasto, descripcion, proveedor, total, fecha_registro):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gastos
        SET descripcion=%s, proveedor=%s, total=%s, fecha_registro=%s
        WHERE id_gasto=%s
    """, (descripcion, proveedor, total, fecha_registro, id_gasto))

    conn.commit()
    cursor.close()
    conn.close()


def eliminar_gasto(id_gasto):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM gastos WHERE id_gasto=%s", (id_gasto,))

    conn.commit()
    cursor.close()
    conn.close()


def obtener_gastos(q=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if q:
        cursor.execute("""
            SELECT id_gasto, descripcion, proveedor, total, fecha_registro
            FROM gastos
            WHERE descripcion LIKE %s OR proveedor LIKE %s
            ORDER BY fecha_registro DESC
        """, (f"%{q}%", f"%{q}%"))
    else:
        cursor.execute("""
            SELECT id_gasto, descripcion, proveedor, total, fecha_registro
            FROM gastos
            ORDER BY fecha_registro DESC
        """)

    gastos = cursor.fetchall()
    cursor.close()
    conn.close()

    return gastos

def obtener_gastos_por_proveedor(fecha_inicio, fecha_fin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT proveedor, SUM(total) as total
        FROM gastos
        WHERE fecha_registro BETWEEN %s AND %s
        GROUP BY proveedor
        ORDER BY total DESC
    """, (fecha_inicio, fecha_fin))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

