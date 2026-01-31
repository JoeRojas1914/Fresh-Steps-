from werkzeug.security import check_password_hash
from login import (
    obtener_usuario_por_username,
    obtener_usuario_caja_activo,
    registrar_login_log
)


def login_password_service(username, password, ip):

    usuario = obtener_usuario_por_username(username)

    if not usuario:
        registrar_login_log(username, "password", False, ip)
        return None

    if not check_password_hash(usuario["password_hash"], password):
        registrar_login_log(username, "password", False, ip)
        return None

    registrar_login_log(username, "password", True, ip)
    return usuario


def login_pin_service(pin, ip):

    usuario = obtener_usuario_caja_activo()

    if not usuario:
        registrar_login_log("caja", "pin", False, ip)
        return None

    if not check_password_hash(usuario["pin_hash"], pin):
        registrar_login_log("caja", "pin", False, ip)
        return None

    registrar_login_log(usuario["usuario"], "pin", True, ip)
    return usuario
