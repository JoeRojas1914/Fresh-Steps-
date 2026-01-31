from db import get_connection


def obtener_usuario_por_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM usuario
        WHERE usuario = %s AND activo = 1
    """, (username,))

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()
    return usuario


def obtener_usuario_caja_activo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM usuario
        WHERE rol = 'caja' AND activo = 1
        LIMIT 1
    """)

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()
    return usuario


def registrar_login_log(usuario, metodo, exito, ip):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO login_log (usuario, metodo, exito, ip)
        VALUES (%s, %s, %s, %s)
    """, (usuario, metodo, exito, ip))

    conn.commit()
    cursor.close()
    conn.close()
