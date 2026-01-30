from db import get_connection

def registrar_pago(id_venta, monto, tipo_pago):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO pago_venta (
                id_venta,
                fecha_pago,
                monto,
                tipo_pago
            )
            VALUES (%s, NOW(), %s, %s)
        """, (id_venta, monto, tipo_pago))

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

    cursor.execute("""
        SELECT
            id_pago,
            fecha_pago,
            monto,
            tipo_pago
        FROM pago_venta
        WHERE id_venta = %s
        ORDER BY fecha_pago ASC
    """, (id_venta,))

    pagos = cursor.fetchall()

    cursor.close()
    conn.close()
    return pagos