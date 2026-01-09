from db import get_connection
from datetime import date, datetime, timedelta 
from calendar import monthrange

from db import get_connection

def crear_venta(id_cliente, tipo_pago, prepago, monto_prepago, entrega_express, aplica_descuento, porcentaje_descuento, zapatos):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            INSERT INTO venta (
                id_cliente,
                tipo_pago,
                prepago,
                monto_prepago,
                entrega_express,
                aplica_descuento,
                porcentaje_descuento,
                total
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
        """, (
            id_cliente,
            tipo_pago,
            prepago,
            monto_prepago,
            entrega_express,
            aplica_descuento,
            porcentaje_descuento
        ))

        id_venta = cursor.lastrowid
        total = 0

        for z in zapatos:
            cursor.execute("""
                INSERT INTO venta_zapato (id_venta, id_zapato)
                VALUES (%s, %s)
            """, (id_venta, z["id_zapato"]))

            id_venta_zapato = cursor.lastrowid

            cursor.execute(
                "SELECT precio FROM servicio WHERE id_servicio=%s",
                (z["id_servicio"],)
            )
            precio = float(cursor.fetchone()["precio"])

            cursor.execute("""
                INSERT INTO zapato_servicio (
                    id_venta_zapato,
                    id_servicio,
                    precio_aplicado
                )
                VALUES (%s, %s, %s)
            """, (
                id_venta_zapato,
                z["id_servicio"],
                precio
            ))

            total += precio

        if entrega_express:
            total += 50
        
        if aplica_descuento and porcentaje_descuento:
            descuento = total * (porcentaje_descuento / 100)
            total -= descuento

        cursor.execute(
            "UPDATE venta SET total=%s WHERE id_venta=%s",
            (total, id_venta)
        )

        conn.commit()
        return id_venta

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()




def obtener_ventas_pendientes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.*, c.nombre, c.apellido
        FROM venta v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        WHERE v.fecha_entrega IS NULL
        ORDER BY v.entrega_express DESC, v.fecha_recibo ASC
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




def obtener_detalles_venta(id_venta):
    """
    Devuelve los detalles de una venta:
    cada zapato con sus servicios aplicados y precio.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            z.marca,
            z.tipo,
            z.color_base,
            z.color_secundario,
            s.nombre AS nombre_servicio,
            zs.precio_aplicado AS precio
        FROM venta_zapato vz
        JOIN zapato z ON vz.id_zapato = z.id_zapato
        JOIN zapato_servicio zs ON vz.id_venta_zapato = zs.id_venta_zapato
        JOIN servicio s ON zs.id_servicio = s.id_servicio
        WHERE vz.id_venta = %s
    """, (id_venta,))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    detalles = []
    for r in resultados:
        detalles.append({
            'zapato': {
                'marca': r['marca'],
                'tipo': r['tipo'],
                'color_base': r['color_base'],
                'color_secundario': r['color_secundario']
            },
            'servicio': {
                'nombre': r['nombre_servicio'],
                'precio': r['precio']
            }
        })

    return detalles


def contar_entregas_pendientes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM venta 
        WHERE fecha_entrega IS NULL
    """)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total


def obtener_ingresos_por_semana(mes=None, año=None):
    hoy = date.today()
    mes = mes or hoy.month
    año = año or hoy.year

    meses_nombre = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    nombre_mes = meses_nombre[mes]

    primer_dia = date(año, mes, 1)
    ultimo_dia = date(año, mes, monthrange(año, mes)[1])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha_entrega, total
        FROM venta
        WHERE fecha_entrega IS NOT NULL
          AND fecha_entrega BETWEEN %s AND %s
        ORDER BY fecha_entrega
    """, (primer_dia, ultimo_dia))

    ventas = cursor.fetchall()
    cursor.close()
    conn.close()

    for v in ventas:
        if isinstance(v['fecha_entrega'], datetime):
            v['fecha_entrega'] = v['fecha_entrega'].date()

    rangos = []
    totales = []

    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        inicio_semana = dia_actual
        fin_semana = min(dia_actual + timedelta(days=6), ultimo_dia)

        total_semana = sum(
            float(v['total']) for v in ventas
            if inicio_semana <= v['fecha_entrega'] <= fin_semana
        )

        rangos.append(f"{inicio_semana.day}-{fin_semana.day} {nombre_mes}")
        totales.append(total_semana)

        dia_actual = fin_semana + timedelta(days=1)

    return {"rangos": rangos, "totales": totales}


