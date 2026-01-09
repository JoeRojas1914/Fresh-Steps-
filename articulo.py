from db import get_connection

# ==========================
# CREAR ARTICULO
# ==========================
def crear_articulo(tipo_articulo, detalles):
    """
    Crea un artículo y su detalle correspondiente en ropa o calzado.
    - tipo_articulo: 'ropa' o 'calzado'
    - detalles: diccionario con los campos específicos
        ROPA: marca, tipo, material, color, observaciones
        CALZADO: tipo, marca, color_base, color_secundario, color_agujetas, observaciones
    Devuelve el id_articulo creado.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if tipo_articulo == 'ropa':
        sql_detalle = """
            INSERT INTO ropa (marca, tipo, material, color, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql_detalle, (
            detalles.get('marca'),
            detalles.get('tipo'),
            detalles.get('material'),
            detalles.get('color'),
            detalles.get('observaciones')
        ))
        id_detalle = cursor.lastrowid

    elif tipo_articulo == 'calzado':
        sql_detalle = """
            INSERT INTO calzado (tipo, marca, color_base, color_secundario, color_agujetas, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_detalle, (
            detalles.get('tipo'),
            detalles.get('marca'),
            detalles.get('color_base'),
            detalles.get('color_secundario'),
            detalles.get('color_agujetas'),
            detalles.get('observaciones')
        ))
        id_detalle = cursor.lastrowid

    else:
        cursor.close()
        conn.close()
        raise ValueError("tipo_articulo debe ser 'ropa' o 'calzado'")

    # Ahora insertamos en ARTICULO
    sql_articulo = """
        INSERT INTO articulo (tipo_articulo, id_detalle_articulo)
        VALUES (%s, %s)
    """
    cursor.execute(sql_articulo, (tipo_articulo, id_detalle))
    id_articulo = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()
    return id_articulo


# ==========================
# OBTENER ARTICULO POR ID
# ==========================
def obtener_articulo_por_id(id_articulo):
    """
    Devuelve la información completa del artículo, incluyendo su detalle.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM articulo WHERE id_articulo=%s", (id_articulo,))
    articulo = cursor.fetchone()
    if not articulo:
        cursor.close()
        conn.close()
        return None

    tipo = articulo['tipo_articulo']
    id_detalle = articulo['id_detalle_articulo']

    if tipo == 'ropa':
        cursor.execute("SELECT * FROM ropa WHERE id_ropa=%s", (id_detalle,))
        detalle = cursor.fetchone()
    elif tipo == 'calzado':
        cursor.execute("SELECT * FROM calzado WHERE id_calzado=%s", (id_detalle,))
        detalle = cursor.fetchone()
    else:
        detalle = None

    articulo['detalle'] = detalle
    cursor.close()
    conn.close()
    return articulo


# ==========================
# ELIMINAR ARTICULO
# ==========================
def eliminar_articulo(id_articulo):
    """
    Elimina un artículo y su detalle.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articulo WHERE id_articulo=%s", (id_articulo,))
    articulo = cursor.fetchone()
    if not articulo:
        cursor.close()
        conn.close()
        return False

    tipo = articulo[1]  # tipo_articulo
    id_detalle = articulo[2]

    # Eliminar detalle
    if tipo == 'ropa':
        cursor.execute("DELETE FROM ropa WHERE id_ropa=%s", (id_detalle,))
    elif tipo == 'calzado':
        cursor.execute("DELETE FROM calzado WHERE id_calzado=%s", (id_detalle,))

    # Eliminar registro de ARTICULO
    cursor.execute("DELETE FROM articulo WHERE id_articulo=%s", (id_articulo,))
    conn.commit()
    cursor.close()
    conn.close()
    return True
