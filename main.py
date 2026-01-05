# from db import get_connection

# conn = get_connection()
# cursor = conn.cursor()

# cursor.execute("SELECT 'Conectado correctamente'")
# print(cursor.fetchone()[0])

# cursor.close()
# conn.close()


from ventas import (
    crear_venta,
    agregar_zapato_a_venta,
    agregar_servicio_a_zapato,
    calcular_total_venta
)

# 1️⃣ Crear venta
venta_id = crear_venta(1, "Efectivo")

# Zapato A
vz1 = agregar_zapato_a_venta(venta_id, 1)
agregar_servicio_a_zapato(vz1, 1, 150)
agregar_servicio_a_zapato(vz1, 2, 80)

# Zapato B
vz2 = agregar_zapato_a_venta(venta_id, 2)
agregar_servicio_a_zapato(vz2, 2, 280)


# 4️⃣ Calcular total
total = calcular_total_venta(venta_id)
print(f"Total venta: ${total}")