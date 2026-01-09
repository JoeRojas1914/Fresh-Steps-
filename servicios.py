from db import get_connection

# ==========================
# CREAR SERVICIO
# ==========================
def crear_servicio(id_negocio, nombre, precio):
    """
    Crea un nuevo servicio asociado a un negocio.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servicio (id_negocio, nombre, precio)
        VALUES (%s, %s, %s)
    """, (id_negocio, nombre, precio))
    id_servicio = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return id_servicio


# ==========================
# ACTUALIZAR SERVICIO
# ==========================
def actualizar_servicio(id_servicio, id_negocio, nombre, precio):
    """
    Actualiza un servicio existente.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE servicio
        SET id_negocio=%s, nombre=%s, precio=%s
        WHERE id_servicio=%s
    """, (id_negocio, nombre, precio, id_servicio))
    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# ELIMINAR SERVICIO
# ==========================
def eliminar_servicio(id_servicio):
    """
    Elimina un servicio por su ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicio WHERE id_servicio=%s", (id_servicio,))
    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# OBTENER SERVICIO POR ID
# ==========================
def obtener_servicio_por_id(id_servicio):
    """
    Obtiene un servicio por su ID.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicio WHERE id_servicio=%s", (id_servicio,))
    servicio = cursor.fetchone()
    cursor.close()
    conn.close()
    return servicio


# ==========================
# CONTAR SERVICIOS
# ==========================
def contar_servicios(q=None, id_negocio=None):
    """
    Devuelve la cantidad total de servicios.
    - q: búsqueda por nombre (opcional)
    - id_negocio: filtrar por negocio (opcional)
    """
    conn = get_connection()
    cursor = conn.cursor()

    if q and id_negocio:
        cursor.execute("""
            SELECT COUNT(*)
            FROM servicio
            WHERE nombre LIKE %s AND id_negocio=%s
        """, (f"%{q}%", id_negocio))
    elif q:
        cursor.execute("""
            SELECT COUNT(*)
            FROM servicio
            WHERE nombre LIKE %s
        """, (f"%{q}%",))
    elif id_negocio:
        cursor.execute("""
            SELECT COUNT(*)
            FROM servicio
            WHERE id_negocio=%s
        """, (id_negocio,))
    else:
        cursor.execute("SELECT COUNT(*) FROM servicio")

    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


# ==========================
# OBTENER SERVICIOS (CON PAGINACIÓN)
# ==========================
def obtener_servicios(q=None, id_negocio=None, limit=10, offset=0):
    """
    Devuelve una lista de servicios con paginación.
    - q: búsqueda por nombre (opcional)
    - id_negocio: filtrar por negocio (opcional)
    - limit: cantidad de registros por página
    - offset: número de registros a saltar (para paginación)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    base_sql = "SELECT id_servicio, id_negocio, nombre, precio FROM servicio"
    condiciones = []
    parametros = []

    if q:
        condiciones.append("nombre LIKE %s")
        parametros.append(f"%{q}%")
    if id_negocio:
        condiciones.append("id_negocio = %s")
        parametros.append(id_negocio)

    if condiciones:
        base_sql += " WHERE " + " AND ".join(condiciones)

    base_sql += " ORDER BY nombre ASC LIMIT %s OFFSET %s"
    parametros.extend([limit, offset])

    cursor.execute(base_sql, tuple(parametros))
    servicios = cursor.fetchall()
    cursor.close()
    conn.close()
    return servicios
