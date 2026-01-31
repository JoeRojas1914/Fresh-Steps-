from db import get_connection
from negocio import obtener_negocios
from ventas import obtener_detalles_venta

def crear_cliente(nombre, apellido, correo, telefono, direccion):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO cliente (nombre, apellido, correo, telefono, direccion)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (nombre, apellido, correo, telefono, direccion))
    id_cliente = cursor.lastrowid
    conn.commit()

    cursor.close()
    conn.close()
    return id_cliente

def obtener_clientes(q=None, limit=10, offset=0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if q:
        cursor.execute("""
            SELECT id_cliente, nombre, apellido, correo, telefono, direccion
            FROM cliente
            WHERE nombre LIKE %s OR apellido LIKE %s
            ORDER BY nombre ASC, apellido ASC
            LIMIT %s OFFSET %s
        """, (f"%{q}%", f"%{q}%", limit, offset))
    else:
        cursor.execute("""
            SELECT id_cliente, nombre, apellido, correo, telefono, direccion
            FROM cliente
            ORDER BY nombre ASC, apellido ASC
            LIMIT %s OFFSET %s
        """, (limit, offset))

    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes



def eliminar_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM cliente WHERE id_cliente = %s",
        (id_cliente,)
    )
    conn.commit()
    cursor.close()
    conn.close()



def actualizar_cliente(id_cliente, nombre, apellido, correo, telefono, direccion):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cliente
        SET nombre=%s, apellido=%s, correo=%s, telefono=%s, direccion=%s
        WHERE id_cliente=%s
    """, (nombre, apellido, correo, telefono, direccion, id_cliente))

    conn.commit()
    cursor.close()
    conn.close()


def contar_clientes(q=None):
    conn = get_connection()
    cursor = conn.cursor()

    if q:
        cursor.execute("""
            SELECT COUNT(*)
            FROM cliente
            WHERE nombre LIKE %s OR apellido LIKE %s
        """, (f"%{q}%", f"%{q}%"))
    else:
        cursor.execute("SELECT COUNT(*) FROM cliente")

    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


def buscar_clientes_por_nombre(texto):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM cliente
        WHERE nombre LIKE %s OR apellido LIKE %s
    """, (f"%{texto}%", f"%{texto}%"))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados



def obtener_cliente_por_id(id_cliente):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *,
               DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro_fmt
        FROM cliente
        WHERE id_cliente = %s
    """, (id_cliente,))

    data = cursor.fetchone()

    cursor.close()
    conn.close()
    return data
