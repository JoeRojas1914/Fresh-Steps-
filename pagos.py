from db import get_connection

def registrar_pago(id_venta, monto, tipo_pago, id_usuario_cobro):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO pago_venta (
                id_venta,
                fecha_pago,
                monto,
                tipo_pago,
                id_usuario_cobro
            )
            VALUES (%s, NOW(), %s, %s, %s)
        """, (id_venta, monto, tipo_pago, id_usuario_cobro))


        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def obtener_pagos_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id_pago,
                p.fecha_pago,
                p.monto,
                p.tipo_pago,
                p.tipo_pago_venta,
                p.id_usuario_cobro,
                u.usuario AS usuario_cobro
            FROM pago_venta p
            JOIN usuario u
                ON p.id_usuario_cobro = u.id_usuario
            WHERE p.id_venta = %s
            ORDER BY p.fecha_pago ASC
        """, (id_venta,))

        pagos = cursor.fetchall()
        return pagos

    finally:
        cursor.close()
        conn.close()


def obtener_pagos_por_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT tipo_pago_venta, tipo_pago, monto, fecha_pago
        FROM pago_venta
        WHERE id_venta=%s
        ORDER BY fecha_pago
    """, (id_venta,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data