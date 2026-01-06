from db import get_connection

def crear_venta(id_cliente, tipo_pago, prepago, monto_prepago):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO venta (id_cliente, tipo_pago, prepago, monto_prepago, total)
        VALUES (%s, %s, %s, %s, 0)
    """, (id_cliente, tipo_pago, prepago, monto_prepago))

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

    conn.commit()
    cursor.close()
    conn.close()



def asignar_servicio_a_venta_zapato(id_venta_zapato, id_servicio, precio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO zapato_servicio (id_venta_zapato, id_servicio, precio_aplicado)
        VALUES (%s, %s, %s)
    """, (id_venta_zapato, id_servicio, precio))

    conn.commit()
    cursor.close()
    conn.close()





def calcular_total_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(s.precio)
        FROM venta_zapato vz
        JOIN zapato_servicio zs ON vz.id_zapato = zs.id_zapato
        JOIN servicio s ON zs.id_servicio = s.id_servicio
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

