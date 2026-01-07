from db import get_connection
from datetime import date, timedelta
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
                'tipo': r['tipo']
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


def obtener_ganancias_por_semana(mes=None, año=None):
    hoy = date.today()
    mes = mes or hoy.month
    año = año or hoy.year

    # Primer y último día del mes
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

    semanas = [0, 0, 0, 0, 0]
    labels = ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"]

    for v in ventas:
        dia = v['fecha_entrega'].day
        if dia <= 7:
            semanas[0] += float(v['total'])
        elif dia <= 14:
            semanas[1] += float(v['total'])
        elif dia <= 21:
            semanas[2] += float(v['total'])
        elif dia <= 28:
            semanas[3] += float(v['total'])
        else:
            semanas[4] += float(v['total'])

    return {"labels": labels, "totales": semanas}