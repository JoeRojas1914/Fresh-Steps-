from werkzeug.security import generate_password_hash
from flask import session
import usuario


def guardar_usuario_service(id_usuario, username, password, rol, pin):

    admin = session.get("usuario")

    if not id_usuario:

        if not password:
            raise ValueError("Password obligatorio")

        if not pin:
            raise ValueError("PIN obligatorio")

        rol = rol or "caja"

        password_hash = generate_password_hash(password)
        pin_hash = generate_password_hash(pin)

        nuevo_id = usuario.crear_usuario(username, password_hash, rol, pin_hash)

        usuario.registrar_historial_usuario(
            nuevo_id,
            "CREADO",
            None,
            {"usuario": username, "rol": rol},
            admin
        )

        return



    antes = usuario.obtener_usuario_por_id(id_usuario)
    if antes["rol"] == "admin":
        return

    usuario.actualizar_usuario(id_usuario, username, rol)

    if password:
        usuario.actualizar_password(id_usuario, generate_password_hash(password))

    if pin:
        usuario.actualizar_pin(id_usuario, generate_password_hash(pin))

    despues = usuario.obtener_usuario_por_id(id_usuario)

    usuario.registrar_historial_usuario(
        id_usuario,
        "EDITADO",
        antes,
        despues,
        admin
    )




def toggle_usuario_service(id_usuario):

    admin = session.get("usuario")

    antes = usuario.obtener_usuario_por_id(id_usuario)

    if antes["rol"] == "admin":
        return

    usuario.toggle_activo(id_usuario)

    despues = usuario.obtener_usuario_por_id(id_usuario)

    usuario.registrar_historial_usuario(
        id_usuario,
        "TOGGLE_ACTIVO",
        antes,
        despues,
        admin
    )


def listar_usuarios_service():
    return usuario.obtener_usuarios()


def obtener_historial_usuario_service(id_usuario):
    return usuario.obtener_historial_usuario(id_usuario)
