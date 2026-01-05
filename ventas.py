from db import get_connection

def crear_venta(id_cliente, tipo_pago):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO venta (id_cliente, tipo_pago, total)
        VALUES (%s, %s, 0)
    """, (id_cliente, tipo_pago))

    venta_id = cursor.lastrowid
    conn.commit()

    cursor.close()
    conn.close()
    return venta_id



def agregar_zapato_a_venta(id_venta, id_zapato):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO venta_zapato (id_venta, id_zapato)
        VALUES (%s, %s)
    """, (id_venta, id_zapato))

    venta_zapato_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()

    return venta_zapato_id


def asignar_servicio_a_venta_zapato(id_venta_zapato, id_servicio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO venta_zapato_servicio (id_venta_zapato, id_servicio)
        VALUES (%s, %s)
    """, (id_venta_zapato, id_servicio))

    conn.commit()
    cursor.close()
    conn.close()



def calcular_total_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(zs.precio_aplicado)
        FROM zapato_servicio zs
        JOIN venta_zapato vz ON zs.id_venta_zapato = vz.id_venta_zapato
        WHERE vz.id_venta = %s
    """, (id_venta,))

    total = cursor.fetchone()[0] or 0

    cursor.execute(
        "UPDATE venta SET total = %s WHERE id_venta = %s",
        (total, id_venta)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return total

def obtener_ventas_pendientes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.*, c.nombre, c.apellido
        FROM venta v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        WHERE v.fecha_entrega IS NULL
        ORDER BY v.fecha_recibo
    """)

    ventas = cursor.fetchall()
    cursor.close()
    conn.close()
    return ventas



def marcar_entregada(id_venta):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE venta
        SET fecha_entrega = NOW()
        WHERE id_venta = %s
    """, (id_venta,))

    conn.commit()
    cursor.close()
    conn.close()






def actualizar_total_venta(id_venta, total):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE venta SET total=%s WHERE id_venta=%s",
        (total, id_venta)
    )

    conn.commit()
    cursor.close()
    conn.close()

