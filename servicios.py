from db import get_connection

def crear_servicio(nombre, descripcion, precio):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO servicio (nombre, descripcion, precio)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (nombre, descripcion, precio))
    conn.commit()

    cursor.close()
    conn.close()

def obtener_servicios(q=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if q:
        cursor.execute("""
            SELECT id_servicio, nombre, descripcion, precio
            FROM servicio
            WHERE nombre LIKE %s
            ORDER BY nombre ASC
        """, (f"%{q}%",))
    else:
        cursor.execute("""
            SELECT id_servicio, nombre, descripcion, precio
            FROM servicio
            ORDER BY nombre ASC
        """)

    servicios = cursor.fetchall()

    cursor.close()
    conn.close()

    return servicios


def actualizar_servicio(id_servicio, nombre, descripcion, precio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE servicio
        SET nombre=%s, descripcion=%s, precio=%s
        WHERE id_servicio=%s
    """, (nombre, descripcion, precio, id_servicio))

    conn.commit()
    cursor.close()
    conn.close()


def eliminar_servicio(id_servicio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM servicio WHERE id_servicio=%s", (id_servicio,))

    conn.commit()
    cursor.close()
    conn.close()

def obtener_servicio_por_id(id_servicio):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM servicio WHERE id_servicio=%s
    """, (id_servicio,))

    servicio = cursor.fetchone()
    cursor.close()
    conn.close()
    return servicio



def contar_servicios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM servicio")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total