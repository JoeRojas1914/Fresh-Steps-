from db import get_connection


def crear_servicio(id_negocio, nombre, precio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO servicio (id_negocio, nombre, precio)
        VALUES (%s, %s, %s)
    """, (id_negocio, nombre, precio))

    conn.commit()
    cursor.close()
    conn.close()


def actualizar_servicio(id_servicio, id_negocio, nombre, precio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE servicio
        SET id_negocio=%s,
            nombre=%s,
            precio=%s
        WHERE id_servicio=%s
    """, (id_negocio, nombre, precio, id_servicio))

    conn.commit()
    cursor.close()
    conn.close()


def eliminar_servicio(id_servicio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM servicio WHERE id_servicio=%s",
        (id_servicio,)
    )

    conn.commit()
    cursor.close()
    conn.close()


def obtener_servicio_por_id(id_servicio):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.id_servicio,
               s.id_negocio,
               n.nombre AS negocio,
               s.nombre,
               s.precio
        FROM servicio s
        JOIN Negocio n ON s.id_negocio = n.id_negocio
        WHERE s.id_servicio = %s
    """, (id_servicio,))

    servicio = cursor.fetchone()
    cursor.close()
    conn.close()
    return servicio


def contar_servicios(id_negocio=None, q=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT COUNT(*) FROM servicio WHERE 1=1"
    params = []

    if id_negocio:
        sql += " AND id_negocio = %s"
        params.append(id_negocio)

    if q:
        sql += " AND nombre LIKE %s"
        params.append(f"%{q}%")

    cursor.execute(sql, params)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total



def obtener_servicios(id_negocio=None, q=None, limit=10, offset=0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT s.id_servicio,
               s.nombre,
               s.precio,
               s.id_negocio,
               n.nombre AS negocio
        FROM servicio s
        JOIN negocio n ON n.id_negocio = s.id_negocio
        WHERE 1=1
    """
    params = []

    if id_negocio:
        sql += " AND s.id_negocio = %s"
        params.append(id_negocio)

    if q:
        sql += " AND s.nombre LIKE %s"
        params.append(f"%{q}%")

    sql += " ORDER BY s.nombre ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(sql, params)
    servicios = cursor.fetchall()

    cursor.close()
    conn.close()
    return servicios


