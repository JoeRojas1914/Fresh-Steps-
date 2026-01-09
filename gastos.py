from db import get_connection

# ==========================
# CREAR GASTO
# ==========================
def crear_gasto(id_negocio, descripcion, proveedor, total, fecha_registro):
    """
    Crea un nuevo gasto asociado a un negocio.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO gasto (id_negocio, descripcion, proveedor, total, fecha_registro)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (id_negocio, descripcion, proveedor, total, fecha_registro))
    id_gasto = cursor.lastrowid
    conn.commit()

    cursor.close()
    conn.close()
    return id_gasto


# ==========================
# ACTUALIZAR GASTO
# ==========================
def actualizar_gasto(id_gasto, id_negocio, descripcion, proveedor, total, fecha_registro):
    """
    Actualiza un gasto existente y su negocio asociado.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gasto
        SET id_negocio=%s, descripcion=%s, proveedor=%s, total=%s, fecha_registro=%s
        WHERE id_gasto=%s
    """, (id_negocio, descripcion, proveedor, total, fecha_registro, id_gasto))

    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# ELIMINAR GASTO
# ==========================
def eliminar_gasto(id_gasto):
    """
    Elimina un gasto por su ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gasto WHERE id_gasto=%s", (id_gasto,))
    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# OBTENER GASTOS (CON PAGINACIÓN Y FILTRO POR NEGOCIO)
# ==========================
def obtener_gastos(id_negocio=None, q=None, limit=10, offset=0):
    """
    Devuelve una lista de gastos con paginación y búsqueda opcional.
    - id_negocio: filtrar por negocio (opcional)
    - q: búsqueda por descripción o proveedor (opcional)
    - limit: cantidad de registros por página
    - offset: número de registros a saltar
    """
    conn = get_connection()
    cursor = conn.
