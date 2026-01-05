from db import get_connection

def crear_cliente(nombre, apellido, correo, telefono, direccion):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO cliente (nombre, apellido, correo, telefono, direccion)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (nombre, apellido, correo, telefono, direccion))
    conn.commit()

    cursor.close()
    conn.close()

def obtener_clientes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("""
        SELECT nombre, apellido, correo, telefono, direccion
        FROM cliente
    """)

    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    return clientes

def eliminar_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))

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

