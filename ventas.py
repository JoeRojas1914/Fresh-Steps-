from db import get_connection
from datetime import date, datetime, timedelta 
from calendar import monthrange


def crear_venta(
    id_negocio,
    id_cliente,
    fecha_estimada,
    tipo_pago,
    prepago,
    monto_prepago,
    aplica_descuento,
    cantidad_descuento,
    articulos
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            INSERT INTO venta (
                id_negocio,
                id_cliente,
                fecha_recibo,
                fecha_estimada,
                tipo_pago,
                prepago,
                monto_prepago,
                aplica_descuento,
                cantidad_descuento,
                total
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
        """, (
            id_negocio,
            id_cliente,
            datetime.now(),
            fecha_estimada,
            tipo_pago,
            prepago,
            monto_prepago,
            aplica_descuento,
            cantidad_descuento
        ))

        id_venta = cursor.lastrowid
        total = 0

        tipos_por_negocio = {
            1: "calzado",
            2: "confeccion",
            3: "maquila"
        }

        for art in articulos:
            tipo_articulo = art["tipo_articulo"]
            tipo_esperado = tipos_por_negocio.get(id_negocio)

            if tipo_esperado and tipo_articulo != tipo_esperado:
                raise Exception(f"Tipo de artículo inválido. Este negocio solo permite: {tipo_esperado}")

            cursor.execute("""
                INSERT INTO articulo (id_venta, tipo_articulo, comentario)
                VALUES (%s, %s, %s)
            """, (
                id_venta,
                tipo_articulo,
                art.get("comentario")
            ))

            id_articulo = cursor.lastrowid

            if tipo_articulo == "calzado":
                d = art["datos"]

                cursor.execute("""
                    INSERT INTO articulo_calzado (
                        id_articulo_calzado,
                        tipo,
                        marca,
                        material,
                        color_base,
                        color_secundario,
                        color_agujetas
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_articulo,
                    d["tipo"],
                    d["marca"],
                    d["material"],
                    d["color_base"],
                    d.get("color_secundario"),
                    d.get("color_agujetas")
                ))

                if not art.get("servicios"):
                    raise Exception("Artículo de calzado sin servicios")

                for s in art["servicios"]:
                    id_servicio = int(s["id_servicio"])
                    precio_aplicado = float(s.get("precio_aplicado") or 0)

                    if precio_aplicado <= 0:
                        cursor.execute(
                            "SELECT precio_base FROM servicio WHERE id_servicio = %s",
                            (id_servicio,)
                        )
                        row = cursor.fetchone()
                        precio_aplicado = float(row["precio_base"]) if row else 0

                    cursor.execute("""
                        INSERT INTO articulo_servicio (
                            id_articulo,
                            id_servicio,
                            precio_aplicado
                        )
                        VALUES (%s, %s, %s)
                    """, (id_articulo, id_servicio, precio_aplicado))

                    total += precio_aplicado

            elif tipo_articulo == "confeccion":
                d = art["datos"]

                cursor.execute("""
                    INSERT INTO articulo_confeccion (
                        id_articulo_confeccion,
                        tipo,
                        marca,
                        material,
                        color_base,
                        color_secundario,
                        cantidad,
                        agujetas
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_articulo,
                    d["tipo"],
                    d["marca"],
                    d["material"],
                    d["color_base"],
                    d.get("color_secundario"),
                    d["cantidad"],
                    d["agujetas"]
                ))

                if not art.get("servicios"):
                    raise Exception("Artículo de confección sin servicios")

                for s in art["servicios"]:
                    id_servicio = int(s["id_servicio"])
                    precio_aplicado = float(s.get("precio_aplicado") or 0)

                    if precio_aplicado <= 0:
                        cursor.execute(
                            "SELECT precio_base FROM servicio WHERE id_servicio = %s",
                            (id_servicio,)
                        )
                        row = cursor.fetchone()
                        precio_aplicado = float(row["precio_base"]) if row else 0

                    cursor.execute("""
                        INSERT INTO articulo_servicio (
                            id_articulo,
                            id_servicio,
                            precio_aplicado
                        )
                        VALUES (%s, %s, %s)
                    """, (id_articulo, id_servicio, precio_aplicado))

                    total += precio_aplicado

            elif tipo_articulo == "maquila":
                d = art["datos"]

                cursor.execute("""
                    INSERT INTO articulo_maquila (
                        id_articulo_maquila,
                        tipo,
                        cantidad,
                        precio_unitario
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_articulo,
                    d["tipo"],
                    d["cantidad"],
                    d["precio_unitario"]
                ))

                total += float(d["cantidad"]) * float(d["precio_unitario"])

        if aplica_descuento and cantidad_descuento:
            total -= float(cantidad_descuento)
            if total < 0:
                total = 0

        cursor.execute(
            "UPDATE venta SET total = %s WHERE id_venta = %s",
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



def contar_entregas_pendientes(id_negocio=None):
    conn = get_connection()
    cursor = conn.cursor()

    filtros = ""
    params = []

    if id_negocio is not None:
        filtros = "AND id_negocio = %s"
        params.append(id_negocio)

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM venta
        WHERE fecha_entrega IS NULL
        {filtros}
    """, params)

    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total




def marcar_entregada(id_venta):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE venta
            SET fecha_entrega = NOW()
            WHERE id_venta = %s
              AND fecha_entrega IS NULL
        """, (id_venta,))

        conn.commit()

        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()





def obtener_detalles_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_articulo, tipo_articulo, comentario
        FROM articulo
        WHERE id_venta = %s
    """, (id_venta,))

    articulos = cursor.fetchall()
    detalles = []

    for art in articulos:
        id_articulo = art["id_articulo"]
        tipo_articulo = art["tipo_articulo"]
        if tipo_articulo == "calzado":
            cursor.execute("""
                SELECT
                    tipo,
                    marca,
                    material,
                    color_base,
                    color_secundario,
                    color_agujetas
                FROM articulo_calzado
                WHERE id_articulo_calzado = %s
            """, (id_articulo,))

            datos = cursor.fetchone()

            cursor.execute("""
                SELECT
                    s.nombre,
                    asv.precio_aplicado
                FROM articulo_servicio asv
                JOIN servicio s ON s.id_servicio = asv.id_servicio
                WHERE asv.id_articulo = %s
            """, (id_articulo,))

            servicios = cursor.fetchall()

            detalles.append({
                "tipo_articulo": "calzado",
                "datos": datos,
                "servicios": servicios,
                "comentario": art["comentario"]
            })

        elif tipo_articulo == "confeccion":
            cursor.execute("""
                SELECT
                    tipo,
                    marca,
                    material,
                    color_base,
                    color_secundario,
                    cantidad,
                    agujetas
                FROM articulo_confeccion
                WHERE id_articulo_confeccion = %s
            """, (id_articulo,))

            datos = cursor.fetchone()

            cursor.execute("""
                SELECT
                    s.nombre,
                    asv.precio_aplicado
                FROM articulo_servicio asv
                JOIN servicio s ON s.id_servicio = asv.id_servicio
                WHERE asv.id_articulo = %s
            """, (id_articulo,))

            servicios = cursor.fetchall()

            detalles.append({
                "tipo_articulo": "confeccion",
                "datos": datos,
                "servicios": servicios,
                "comentario": art["comentario"]
            })

        elif tipo_articulo == "maquila":
            cursor.execute("""
                SELECT
                    tipo,
                    cantidad,
                    precio_unitario,
                    subtotal
                FROM articulo_maquila
                WHERE id_articulo_maquila = %s
            """, (id_articulo,))

            datos = cursor.fetchone()

            detalles.append({
                "tipo_articulo": "maquila",
                "datos": datos,
                "servicios": [],
                "comentario": art["comentario"]
            })

    cursor.close()
    conn.close()
    return detalles




def obtener_ingresos_por_semana(id_negocio, mes=None, año=None):
    hoy = date.today()
    mes = mes or hoy.month
    año = año or hoy.year

    primer_dia = date(año, mes, 1)
    ultimo_dia = date(año, mes, monthrange(año, mes)[1])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.fecha_entrega, asv.precio_aplicado AS total
        FROM venta v
        JOIN articulo a ON a.id_venta = v.id_venta
        JOIN articulo_servicio asv ON asv.id_articulo = a.id_articulo
        WHERE v.id_negocio = %s
          AND v.fecha_entrega BETWEEN %s AND %s
    """, (id_negocio, primer_dia, ultimo_dia))

    servicios = cursor.fetchall()

    cursor.execute("""
        SELECT v.fecha_entrega, am.subtotal AS total
        FROM venta v
        JOIN articulo a ON a.id_venta = v.id_venta
        JOIN articulo_maquila am ON am.id_articulo_maquila = a.id_articulo
        WHERE v.id_negocio = %s
          AND v.fecha_entrega BETWEEN %s AND %s
    """, (id_negocio, primer_dia, ultimo_dia))

    maquila = cursor.fetchall()

    cursor.close()
    conn.close()

    ventas = servicios + maquila

    for v in ventas:
        if isinstance(v["fecha_entrega"], datetime):
            v["fecha_entrega"] = v["fecha_entrega"].date()

    rangos = []
    totales = []

    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        inicio = dia_actual
        fin = min(dia_actual + timedelta(days=6), ultimo_dia)

        total_semana = sum(
            float(v["total"]) for v in ventas
            if inicio <= v["fecha_entrega"] <= fin
        )

        rangos.append(f"{inicio.day}-{fin.day}")
        totales.append(total_semana)

        dia_actual = fin + timedelta(days=1)

    return {"rangos": rangos, "totales": totales}



def obtener_ingresos_por_negocio(id_negocio, fecha_inicio=None, fecha_fin=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    filtros_fecha = ""
    params = [id_negocio]

    if fecha_inicio and fecha_fin:
        filtros_fecha = "AND v.fecha_entrega BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])

    cursor.execute(f"""
        SELECT COALESCE(SUM(asv.precio_aplicado), 0) AS total
        FROM venta v
        JOIN articulo a ON a.id_venta = v.id_venta
        JOIN articulo_servicio asv ON asv.id_articulo = a.id_articulo
        WHERE v.id_negocio = %s
          AND v.fecha_entrega IS NOT NULL
          {filtros_fecha}
    """, params)

    total_servicios = cursor.fetchone()["total"]

    cursor.execute(f"""
        SELECT COALESCE(SUM(am.subtotal), 0) AS total
        FROM venta v
        JOIN articulo a ON a.id_venta = v.id_venta
        JOIN articulo_maquila am ON am.id_articulo_maquila = a.id_articulo
        WHERE v.id_negocio = %s
          AND v.fecha_entrega IS NOT NULL
          {filtros_fecha}
    """, params)

    total_maquila = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return total_servicios + total_maquila


def obtener_ingresos_por_dia(id_negocio, fecha):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COALESCE(SUM(asv.precio_aplicado), 0) AS total
        FROM venta v
        JOIN articulo a ON a.id_venta = v.id_venta
        JOIN articulo_servicio asv ON asv.id_articulo = a.id_articulo
        WHERE v.id_negocio = %s
          AND DATE(v.fecha_entrega) = %s
    """, (id_negocio, fecha))

    total_servicios = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COALESCE(SUM(am.subtotal), 0) AS total
        FROM venta v
        JOIN articulo a ON a.id_venta = v.id_venta
        JOIN articulo_maquila am ON am.id_articulo_maquila = a.id_articulo
        WHERE v.id_negocio = %s
          AND DATE(v.fecha_entrega) = %s
    """, (id_negocio, fecha))

    total_maquila = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return total_servicios + total_maquila

def obtener_ventas_pendientes(id_negocio=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    filtros = ""
    params = []

    if id_negocio:
        filtros = "AND v.id_negocio = %s"
        params.append(id_negocio)

    cursor.execute(f"""
        SELECT 
            v.id_venta,
            v.fecha_recibo,
            v.fecha_estimada,
            v.total,
            v.prepago,             
            v.monto_prepago, 
            c.nombre,
            c.apellido,
            n.nombre AS negocio
        FROM venta v
        LEFT JOIN cliente c ON v.id_cliente = c.id_cliente
        LEFT JOIN negocio n ON v.id_negocio = n.id_negocio
        WHERE v.fecha_entrega IS NULL
        {filtros}
        ORDER BY 
            v.fecha_estimada ASC,
            v.fecha_recibo ASC
    """, params)

    ventas = cursor.fetchall()
    cursor.close()
    conn.close()
    return ventas


def obtener_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            v.id_venta,
            v.id_negocio,
            v.total,
            v.fecha_recibo,
            v.fecha_estimada,
            v.prepago,
            v.monto_prepago,
            v.aplica_descuento,
            v.cantidad_descuento,
            CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente
        FROM venta v
        JOIN cliente c ON c.id_cliente = v.id_cliente
        WHERE v.id_venta = %s
        LIMIT 1
    """, (id_venta,))

    venta = cursor.fetchone()

    cursor.close()
    conn.close()
    return venta
