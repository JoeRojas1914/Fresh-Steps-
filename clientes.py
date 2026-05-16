import json
from db import get_db
from utils import to_json_safe


def crear_cliente(nombre, apellido, correo, telefono, direccion, id_usuario):
    with get_db() as (_, cursor):
        cursor.execute("""
            INSERT INTO cliente
            (nombre, apellido, correo, telefono, direccion, activo, id_usuario)
            VALUES (%s,%s,%s,%s,%s,1,%s)
        """, (nombre, apellido, correo, telefono, direccion, id_usuario))

        id_cliente = cursor.lastrowid

        despues = {
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "telefono": telefono,
            "direccion": direccion,
        }

        registrar_historial(cursor, id_cliente, "CREADO", id_usuario, None, despues)
        return id_cliente


def eliminar_cliente(id_cliente, id_usuario):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM venta
            WHERE id_cliente=%s
              AND eliminado = 0
        """, (id_cliente,))

        if cursor.fetchone()["total"] > 0:
            return False

        cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
        antes = cursor.fetchone()

        cursor.execute("""
            UPDATE cliente
            SET activo = 0
            WHERE id_cliente=%s
        """, (id_cliente,))

        registrar_historial(cursor, id_cliente, "ELIMINADO", id_usuario, antes, None)
        return True


def actualizar_cliente(id_cliente, nombre, apellido, correo, telefono, direccion, id_usuario):
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
        antes = cursor.fetchone()

        cursor.execute("""
            UPDATE cliente
            SET nombre=%s,
                apellido=%s,
                correo=%s,
                telefono=%s,
                direccion=%s
            WHERE id_cliente=%s
        """, (nombre, apellido, correo, telefono, direccion, id_cliente))

        despues = {
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "telefono": telefono,
            "direccion": direccion,
        }

        registrar_historial(cursor, id_cliente, "EDITADO", id_usuario, antes, despues)


def contar_clientes(q=None, incluir_eliminados=False):
    with get_db() as (_, cursor):
        sql = "SELECT COUNT(*) AS total FROM cliente WHERE 1=1"
        params = []

        if not incluir_eliminados:
            sql += " AND activo = 1"

        if q:
            sql += " AND (nombre LIKE %s OR apellido LIKE %s)"
            params.extend([f"%{q}%", f"%{q}%"])

        cursor.execute(sql, params)
        return cursor.fetchone()["total"]


def buscar_clientes_por_nombre(texto):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT *
            FROM cliente
            WHERE activo = 1
              AND (nombre LIKE %s OR apellido LIKE %s)
        """, (f"%{texto}%", f"%{texto}%"))
        return cursor.fetchall()


def obtener_cliente_por_id(id_cliente):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT *,
                   DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro_fmt
            FROM cliente
            WHERE id_cliente = %s
        """, (id_cliente,))
        return cursor.fetchone()


def registrar_historial(cursor, id_cliente, accion, id_usuario, antes=None, despues=None):
    cursor.execute("""
        INSERT INTO clientes_historial
        (id_cliente, accion, id_usuario, datos_antes, datos_despues)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        id_cliente,
        accion,
        id_usuario,
        json.dumps(to_json_safe(antes)) if antes else None,
        json.dumps(to_json_safe(despues)) if despues else None,
    ))


def restaurar_cliente(id_cliente, id_usuario):
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
        antes = cursor.fetchone()

        cursor.execute("""
            UPDATE cliente
            SET activo = 1
            WHERE id_cliente=%s
        """, (id_cliente,))

        registrar_historial(cursor, id_cliente, "RESTAURADO", id_usuario, antes, None)


def obtener_clientes(q=None, limit=10, offset=0, incluir_eliminados=False):
    with get_db() as (_, cursor):
        sql = """
            SELECT
                id_cliente,
                nombre,
                apellido,
                telefono,
                correo,
                direccion,
                activo
            FROM cliente
            WHERE 1=1
        """
        params = []

        if not incluir_eliminados:
            sql += " AND activo = 1"

        if q:
            sql += " AND (nombre LIKE %s OR apellido LIKE %s)"
            params.extend([f"%{q}%", f"%{q}%"])

        sql += " ORDER BY nombre ASC, apellido ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(sql, params)
        return cursor.fetchall()


def obtener_historial_cliente(id_cliente):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT
                h.*,
                u.usuario AS usuario
            FROM clientes_historial h
            JOIN usuario u ON u.id_usuario = h.id_usuario
            WHERE h.id_cliente = %s
            ORDER BY h.fecha DESC
        """, (id_cliente,))
        return cursor.fetchall()
