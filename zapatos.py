from db import get_connection

def crear_zapato(id_cliente, color_base, color_secundario, material, tipo, marca):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO zapato (id_cliente, color_base, color_secundario, material, tipo, marca)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (id_cliente, color_base, color_secundario, material, tipo, marca))
    conn.commit()

    cursor.close()
    conn.close()

def obtener_zapatos_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM zapato
        WHERE id_cliente = %s
    """, (id_cliente,))

    zapatos = cursor.fetchall()
    cursor.close()
    conn.close()
    return zapatos

def actualizar_zapato(id_zapato, color_base, color_secundario, material, tipo, marca):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE zapato
        SET color_base=%s, color_secundario=%s, material=%s, tipo=%s, marca=%s
        WHERE id_zapato=%s
    """, (color_base, color_secundario, material, tipo, marca, id_zapato))

    conn.commit()
    cursor.close()
    conn.close()


def eliminar_zapato(id_zapato):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM zapato WHERE id_zapato=%s", (id_zapato,))
    conn.commit()

    cursor.close()
    conn.close()

