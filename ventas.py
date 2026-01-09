from db import get_connection
from datetime import date, datetime, timedelta
from calendar import monthrange

# ==========================
# CREAR VENTA
# ==========================
def crear_venta(id_negocio, id_cliente, tipo_pago, prepago, monto_prepago, aplica_descuento, porcentaje_descuento, articulos):
    """
    Crea una venta y registra todos los artículos con sus servicios.
    - articulos: lista de dicts con:
        id_articulo, id_servicio
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Insertamos la venta
        cursor.execute("""
            INSERT INTO venta (
                id_negocio,
                id_cliente,
                fecha_recibo,
                tipo_pago,
                prepago,
                monto_prepago,
                aplica_descuento,
                cantidad_descuento,
                total
            )
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, 0)
        """, (
            id_negocio,
            id_cliente,
            tipo_pago,
            prepago,
            monto_prepago,
            aplica_descuento,
            porcentaje_descuento
        ))

        id_venta = cursor.lastrowid
        total = 0

        # Registramos cada artículo en venta_articulo y su servicio
        for a in articulos:
            cursor.execute("""
                INSERT INTO venta_articulo (id_venta, id_articulo, id_servicio)
                VALUES (%s, %s, %s)
            """, (id_venta, a['id_articulo'], a['id_servicio']))
            id_venta_articulo = cursor.lastrowid

            cursor.execute("SELECT precio FROM servicio WHERE id_servicio=%s", (a['id_servicio'],))
            precio = float(cursor.fetchone()['precio'])

            # Guardamos precio aplicado en venta_articulo
            cursor.execute("""
                UPDATE venta_articulo SET precio_aplicado=%s WHERE id_venta_articulo=%s
            """, (precio, id_venta_articulo))

            total += precio

        # Aplicamos prepago y descuento si corresponde
        if prepago:
            total += monto_prepago
        if aplica_descuento and porcentaje_descuento:
            total -= total * (porcentaje_descuento / 100)

        cursor.execute("UPDATE venta SET total=%s WHERE id_venta=%s", (total, id_venta))

        conn.commit()
        return id_venta

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


# ==========================
# OBTENER VENTAS PENDIENTES
# ==========================
def obtener_ventas_pendientes(id_negocio=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT v.*, c.nombre, c.apellido
        FROM venta v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        WHERE v.fecha_entrega IS NULL
    """
    params = []
    if id_negocio:
        sql += " AND v.id_negocio=%s"
        params.append(id_negocio)

    sql += " ORDER BY v.fecha_recibo ASC"

    cursor.execute(sql, tuple(params))
    ventas = cursor.fetchall()
    cursor.close()
    conn.close()
    return ventas


# ==========================
# MARCAR VENTA ENTREGADA
# ==========================
def marcar_entregada(id_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE venta SET fecha_entrega=NOW() WHERE id_venta=%s", (id_venta,))
    conn.commit()
    cursor.close()
    conn.close()


# ==========================
# OBTENER DETALLES DE VENTA
# ==========================
def obtener_detalles_venta(id_venta):
    """
    Devuelve los detalles de una venta: cada artículo con su tipo y servicio aplicado.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.tipo_articulo, a.id_articulo, a.id_detalle_articulo,
               s.nombre AS nombre_servicio, va.precio_aplicado AS precio
        FROM venta_articulo va
        JOIN articulo a ON va.id_articulo = a.id_articulo
        JOIN servicio s ON va.id_servicio = s.id_servicio
        WHERE va.id_venta = %s
    """, (id_venta,))

    articulos = cursor.fetchall()
    detalles = []

    for art in articulos:
        # Obtenemos detalles según tipo_articulo
        if art['tipo_articulo'] == 'ropa':
            cursor.execute("SELECT * FROM ropa WHERE id_confeccion=%s", (art['id_detalle_articulo'],))
        else:
            cursor.execute("SELECT * FROM calzado WHERE id_calzado=%s", (art['id_detalle_articulo'],))
        detalle = cursor.fetchone()

        detalles.append({
            'tipo_articulo': art['tipo_articulo'],
            'detalle': detalle,
            'servicio': {
                'nombre': art['nombre_servicio'],
                'precio': art['precio']
            }
        })

    cursor.close()
    conn.close()
    return detalles


# ==========================
# CONTAR VENTAS PENDIENTES
# ==========================
def contar_ventas_pendientes(id_negocio=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT COUNT(*) FROM venta WHERE fecha_entrega IS NULL"
    params = []
    if id_negocio:
        sql += " AND id_negocio=%s"
        params.append(id_negocio)

    cursor.execute(sql, tuple(params))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


# ==========================
# INGRESOS POR SEMANA
# ==========================
def obtener_ingresos_por_semana(id_negocio=None, mes=None, año=None):
    hoy = date.today()
    mes = mes or hoy.month
    año = año or hoy.year

    primer_dia = date(año, mes, 1)
    ultimo_dia = date(año, mes, monthrange(año, mes)[1])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT fecha_entrega, total
        FROM venta
        WHERE fecha_entrega IS NOT NULL
          AND fecha_entrega BETWEEN %s AND %s
    """
    params = [primer_dia, ultimo_dia]
    if id_negocio:
        sql += " AND id_negocio=%s"
        params.append(id_negocio)

    cursor.execute(sql, tuple(params))
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
        rangos.append(f"{inicio_semana.day}-{fin_semana.day} {mes}")
        totales.append(total_semana)
        dia_actual = fin_semana + timedelta(days=1)

    return {"rangos": rangos, "totales": totales}
