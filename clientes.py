from db import get_connection
from datetime import date

# ==========================
# CREAR CLIENTE
# ==========================
def crear_cliente(nombre, apellido, correo, telefono, codigo_postal):
    """
    Crea un nuevo cliente en la base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO cliente (fecha_registro, nombre, apellido, correo, telefono, codigo_postal)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    fecha_registro = date.today()  # fecha actual

    cursor.execute(sql, (fecha_registro, nombre, apellido, correo, telefono, codigo_postal))
    id_cliente = cursor.lastrowid
    conn.commit()

    cursor.close()
    conn.close()
    return id_cliente


# ==========================
# OBTENER CLIENTES (CON PAGINACIÓN)
# ==========================
def obtener_clientes(q=None, limit=10, offset=0):
    """
    Devuelve una lista de clientes con paginación.
    - q: búsqueda por nombre o apellido (opcional)
    - limit: cantidad de registros por página
    - offset: número de registros a saltar (para paginación)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if q:
        cursor.execute("""
            SELECT id_cliente, fecha_registro, nombre, apellido, correo, telefono, codigo_postal
            FROM cliente
            WHERE nombre LIKE %s OR apellido LIKE %s
            ORDER BY nombre ASC, apellido ASC
            LIMIT %s OFFSET %s
        """, (f"%{q}%", f"%{q}%", limit, offset))
    else:
        cursor.execute("""
            SELECT id_cliente, fecha_registro, nombre, apellido, correo, telefono, codigo_postal
            FROM cliente
            ORDER BY nombre ASC, apellido ASC
            LIMIT %s OFFSET %s
        """, (limit, offset))

    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes


# ==========================
# ACTUALIZAR CLIENTE
# ==========================
def actualizar_cliente(id_cliente, nombre, apellido, correo, telefono, codigo_postal):
    """
    Actualiza los datos de un cliente.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cliente
        SET nombre=%s, apellido=%s, correo=%s, telefono=%s, codigo_postal=%s
        WHERE id_cliente=%s
    """, (nombre, apellido, correo, telefono, codigo_postal, id_cliente))

    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# ELIMINAR CLIENTE
# ==========================
def eliminar_cliente(id_cliente):
    """
    Elimina un cliente por su ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM cliente WHERE id_cliente = %s",
        (id_cliente,)
    )
    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# CONTAR CLIENTES
# ==========================
def contar_clientes(q=None):
    """
    Devuelve la cantidad total de clientes.
    - q: búsqueda por nombre o apellido (opcional)
    """
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
