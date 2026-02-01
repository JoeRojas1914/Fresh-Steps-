from datetime import datetime
from werkzeug.security import check_password_hash

from login import (
    obtener_usuario_por_username,
    obtener_usuario_caja_activo,
    registrar_login_log,
    obtener_intentos,
    registrar_fallo,
    limpiar_intentos
)


def login_password_service(username, password, ip):
    intento = obtener_intentos(username, ip)

    if intento and intento["bloqueado_hasta"]:
        if datetime.now() < intento["bloqueado_hasta"]:
            registrar_login_log(username, "password_locked", False, ip)
            return "LOCKED"


    usuario = obtener_usuario_por_username(username)

    if not usuario or not check_password_hash(usuario["password_hash"], password):

        registrar_fallo(username, ip)
        registrar_login_log(username, "password", False, ip)
        return None


    limpiar_intentos(username, ip)
    registrar_login_log(username, "password", True, ip)

    return usuario


def login_pin_service(pin, ip):

    username = "caja" 

    intento = obtener_intentos(username, ip)

    if intento and intento["bloqueado_hasta"]:
        if datetime.now() < intento["bloqueado_hasta"]:
            registrar_login_log(username, "pin_locked", False, ip)
            return "LOCKED"


    usuario = obtener_usuario_caja_activo()

    if not usuario or not check_password_hash(usuario["pin_hash"], pin):

        registrar_fallo(username, ip)
        registrar_login_log(username, "pin", False, ip)
        return None


    limpiar_intentos(username, ip)
    registrar_login_log(usuario["usuario"], "pin", True, ip)

    return usuario
