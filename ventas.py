from decimal import Decimal
from db import get_connection
from datetime import datetime



def crear_venta(
    id_negocio,
    id_cliente,
    fecha_estimada,
    aplica_descuento,
    cantidad_descuento,
    articulos,
    id_usuario_creo 
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
                aplica_descuento,
                cantidad_descuento,
                total,
                id_usuario_creo
            )
            VALUES (%s, %s, %s, %s, %s, %s, 0, %s)
        """, (
            id_negocio,
            id_cliente,
            datetime.now(),
            fecha_estimada,
            aplica_descuento,
            cantidad_descuento,
            id_usuario_creo
        ))


        id_venta = cursor.lastrowid
        total = Decimal("0.00")

        tipos_por_negocio = {
            1: "calzado",
            2: "confeccion",
            3: "maquila"
        }

        for art in articulos:
            tipo_articulo = art["tipo_articulo"]
            tipo_esperado = tipos_por_negocio.get(id_negocio)

            if tipo_esperado and tipo_articulo != tipo_esperado:
                raise Exception(
                    f"Tipo de artículo inválido. Este negocio solo permite: {tipo_esperado}"
                )

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
                        id_articulo,
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

                    try:
                        precio_aplicado = Decimal(str(s.get("precio_aplicado") or "0"))
                    except InvalidOperation:
                        precio_aplicado = Decimal("0")

                    if precio_aplicado <= 0:
                        cursor.execute(
                            "SELECT precio_base FROM servicio WHERE id_servicio = %s",
                            (id_servicio,)
                        )
                        row = cursor.fetchone()
                        precio_aplicado = (
                            Decimal(str(row["precio_base"])) if row else Decimal("0")
                        )

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

                cantidad = Decimal(str(d.get("cantidad", 1)))

                cursor.execute("""
                    INSERT INTO articulo_confeccion (
                        id_articulo,
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
                    int(cantidad),
                    d["agujetas"]
                ))

                if not art.get("servicios"):
                    raise Exception("Artículo de confección sin servicios")

                for s in art["servicios"]:
                    id_servicio = int(s["id_servicio"])

                    try:
                        precio_aplicado = Decimal(str(s.get("precio_aplicado") or "0"))
                    except InvalidOperation:
                        precio_aplicado = Decimal("0")

                    if precio_aplicado <= 0:
                        cursor.execute(
                            "SELECT precio_base FROM servicio WHERE id_servicio = %s",
                            (id_servicio,)
                        )
                        row = cursor.fetchone()
                        precio_aplicado = (
                            Decimal(str(row["precio_base"])) if row else Decimal("0")
                        )

                    cursor.execute("""
                        INSERT INTO articulo_servicio (
                            id_articulo,
                            id_servicio,
                            precio_aplicado
                        )
                        VALUES (%s, %s, %s)
                    """, (id_articulo, id_servicio, precio_aplicado))

                    total += cantidad * precio_aplicado

            elif tipo_articulo == "maquila":
                d = art["datos"]

                cantidad = Decimal(str(d["cantidad"]))
                precio_unitario = Decimal(str(d["precio_unitario"]))

                cursor.execute("""
                    INSERT INTO articulo_maquila (
                        id_articulo,
                        tipo,
                        cantidad,
                        precio_unitario
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_articulo,
                    d["tipo"],
                    int(cantidad),
                    precio_unitario
                ))

                total += cantidad * precio_unitario


        if aplica_descuento and cantidad_descuento:
            total -= Decimal(str(cantidad_descuento))
            if total < 0:
                total = Decimal("0.00")

        cursor.execute(
            "UPDATE venta SET total = %s WHERE id_venta = %s",
            (str(total), id_venta)
        )

        conn.commit()
        return id_venta

    except Exception:
        conn.rollback()
        raise

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




def marcar_entregada(id_venta, id_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE venta
            SET fecha_entrega = NOW(),
                id_usuario_entrego = %s
            WHERE id_venta = %s
              AND fecha_entrega IS NULL
        """, (id_usuario, id_venta))

        conn.commit()

        return cursor.rowcount > 0

    except Exception:
        conn.rollback()
        raise

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
                WHERE id_articulo = %s
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
                WHERE id_articulo = %s
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
                WHERE id_articulo = %s
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




def obtener_ventas_pendientes(id_negocio=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            v.id_venta,
            v.fecha_recibo,
            v.fecha_estimada,
            v.total,
            c.nombre,
            c.apellido,
            n.nombre AS negocio
        FROM venta v
        JOIN cliente c ON c.id_cliente = v.id_cliente
        JOIN negocio n ON n.id_negocio = v.id_negocio
        WHERE v.fecha_entrega IS NULL
    """

    params = []

    if id_negocio:
        query += " AND v.id_negocio = %s"
        params.append(id_negocio)

    query += " ORDER BY v.fecha_estimada ASC"

    cursor.execute(query, params)
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
            v.fecha_recibo,
            v.fecha_estimada,
            v.total,
            v.aplica_descuento,
            v.cantidad_descuento,

            CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente,

            COALESCE(SUM(p.monto), 0) AS total_pagado,
            (v.total - COALESCE(SUM(p.monto), 0)) AS saldo_pendiente

        FROM venta v
        JOIN cliente c ON c.id_cliente = v.id_cliente
        LEFT JOIN pago_venta p ON p.id_venta = v.id_venta

        WHERE v.id_venta = %s
        GROUP BY v.id_venta
    """, (id_venta,))

    venta = cursor.fetchone()

    cursor.close()
    conn.close()
    return venta

