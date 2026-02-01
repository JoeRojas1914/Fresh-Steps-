import datetime
from decimal import Decimal
import json
from db import get_connection


def crear_servicio(id_negocio, nombre, precio, id_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            INSERT INTO servicio (id_negocio, nombre, precio)
            VALUES (%s, %s, %s)
        """, (id_negocio, nombre, precio))

        id_servicio = cursor.lastrowid

        despues = {
            "nombre": nombre,
            "precio": precio
        }

        registrar_historial(cursor, id_servicio, "CREADO", id_usuario, None, despues)

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def actualizar_servicio(id_servicio, id_negocio, nombre, precio, id_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM servicio WHERE id_servicio=%s", (id_servicio,))
        antes = cursor.fetchone()

        cursor.execute("""
            UPDATE servicio
            SET id_negocio=%s, nombre=%s, precio=%s
            WHERE id_servicio=%s
        """, (id_negocio, nombre, precio, id_servicio))

        despues = {
            "nombre": nombre,
            "precio": precio
        }

        registrar_historial(cursor, id_servicio, "EDITADO", id_usuario, antes, despues)

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def eliminar_servicio(id_servicio, id_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if servicio_tiene_ventas(cursor, id_servicio):
            return False  

        cursor.execute("SELECT * FROM servicio WHERE id_servicio=%s", (id_servicio,))
        antes = cursor.fetchone()

        cursor.execute("DELETE FROM servicio WHERE id_servicio=%s", (id_servicio,))

        registrar_historial(cursor, id_servicio, "ELIMINADO", id_usuario, antes, None)

        conn.commit()
        return True

    finally:
        cursor.close()
        conn.close()


def obtener_servicio_por_id(id_servicio):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.id_servicio,
               s.id_negocio,
               n.nombre AS negocio,
               s.nombre,
               s.precio
        FROM servicio s
        JOIN Negocio n ON s.id_negocio = n.id_negocio
        WHERE s.id_servicio = %s
    """, (id_servicio,))

    servicio = cursor.fetchone()
    cursor.close()
    conn.close()
    return servicio


def contar_servicios(id_negocio=None, q=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT COUNT(*) FROM servicio WHERE 1=1"
    params = []

    if id_negocio:
        sql += " AND id_negocio = %s"
        params.append(id_negocio)

    if q:
        sql += " AND nombre LIKE %s"
        params.append(f"%{q}%")

    cursor.execute(sql, params)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total



def obtener_servicios(id_negocio=None, q=None, limit=10, offset=0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT s.id_servicio,
               s.nombre,
               s.precio,
               s.id_negocio,
               n.nombre AS negocio
        FROM servicio s
        JOIN negocio n ON n.id_negocio = s.id_negocio
        WHERE 1=1
    """
    params = []

    if id_negocio:
        sql += " AND s.id_negocio = %s"
        params.append(id_negocio)

    if q:
        sql += " AND s.nombre LIKE %s"
        params.append(f"%{q}%")

    sql += " ORDER BY s.nombre ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(sql, params)
    servicios = cursor.fetchall()

    cursor.close()
    conn.close()
    return servicios

def servicio_tiene_ventas(cursor, id_servicio):

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM articulo_servicio
        WHERE id_servicio = %s
    """, (id_servicio,))

    row = cursor.fetchone()

    if isinstance(row, dict):
        return row["total"] > 0
    else:
        return row[0] > 0




def to_json_safe(data):
    if not data:
        return None

    safe = {}

    for k, v in data.items():

        if isinstance(v, Decimal):
            safe[k] = float(v)

        elif isinstance(v, (datetime.date, datetime.datetime)):
            safe[k] = str(v)

        else:
            safe[k] = v

    return safe



def registrar_historial(cursor, id_servicio, accion, id_usuario, antes=None, despues=None):
    cursor.execute("""
        INSERT INTO servicios_historial
        (id_servicio, accion, id_usuario, datos_antes, datos_despues)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        id_servicio,
        accion,
        id_usuario,
        json.dumps(to_json_safe(antes)) if antes else None,
        json.dumps(to_json_safe(despues)) if despues else None
    ))

def obtener_historial_servicio(id_servicio):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT h.*, u.usuario AS usuario
        FROM servicios_historial h
        JOIN usuario u ON u.id_usuario = h.id_usuario
        WHERE id_servicio=%s
        ORDER BY fecha DESC
    """, (id_servicio,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data
