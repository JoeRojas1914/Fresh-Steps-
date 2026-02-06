document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector(".modal-form");
    if (!form) return;

    form.addEventListener("submit", function (e) {

        const id = document.getElementById("id_usuario").value;
        const password = document.getElementById("password").value.trim();
        const pin = document.getElementById("pin").value.trim();
        const username = document.getElementById("usuario").value.trim();

        const creando = !id;

        if (creando && !password) {
            alert("La contraseña es obligatoria al crear el usuario.");
            e.preventDefault();
            return;
        }

        if (password && !/^(?=.*\d).{6,}$/.test(password)) {
            alert("🔒 La contraseña debe tener mínimo 6 caracteres y al menos 1 número.");
            e.preventDefault();
            return;
        }

        if (creando && !/^\d{4}$/.test(pin)) {
            alert("El PIN debe tener exactamente 4 dígitos.");
            e.preventDefault();
            return;
        }

        if (!/^[a-zA-Z0-9_]{3,}$/.test(username)) {
            alert("El usuario debe tener mínimo 3 caracteres y solo letras, números o _");
            e.preventDefault();
            return;
        }
    });

});



window.abrirModal = function () {
    document.getElementById("modal").style.display = "block";
    document.getElementById("modalTitulo").innerText = "Agregar usuario";

    document.getElementById("id_usuario").value = "";
    document.getElementById("usuario").value = "";
    document.getElementById("password").value = "";
    document.getElementById("pin").value = "";

    document.getElementById("password").required = true;
    document.getElementById("pin").required = true;
};

window.cerrarModal = function () {
    document.getElementById("modal").style.display = "none";
};

window.editarUsuario = function (e, id, usuario) {
    e.stopPropagation();

    window.abrirModal();

    document.getElementById("modalTitulo").innerText = "Editar usuario";
    document.getElementById("id_usuario").value = id;
    document.getElementById("usuario").value = usuario;

    document.getElementById("password").required = false;
    document.getElementById("pin").required = false;
};



window.cerrarHistorialUsuario = function () {
    document.getElementById("modalHistorialUsuario").style.display = "none";
};

window.verHistorialUsuario = async function (e, id) {
    e.stopPropagation();

    const modal = document.getElementById("modalHistorialUsuario");
    const tbody = document.querySelector("#tablaHistorialUsuario tbody");

    tbody.innerHTML = "<tr><td colspan='4'>Cargando...</td></tr>";
    modal.style.display = "block";

    const res = await fetch(`/usuarios/${id}/historial`);
    const data = await res.json();

    if (!data.length) {
        tbody.innerHTML = "<tr><td colspan='4'>Sin historial</td></tr>";
        return;
    }

    tbody.innerHTML = "";

    data.forEach(h => {

        const antes = h.datos_antes ? JSON.parse(h.datos_antes) : null;
        const despues = h.datos_despues ? JSON.parse(h.datos_despues) : null;

        let cambios = "";

        if (antes && despues) {
            Object.keys(despues).forEach(k => {
                if (antes[k] !== despues[k]) {
                    cambios += `
                        <div>
                            <b>${k}</b>:
                            <span style="color:#ef4444">${antes[k]}</span>
                            →
                            <span style="color:#22c55e">${despues[k]}</span>
                        </div>
                    `;
                }
            });
        } else if (despues) {
            cambios = "Usuario creado";
        } else {
            cambios = h.accion;
        }

        tbody.innerHTML += `
            <tr>
                <td><b>${h.accion}</b></td>
                <td>${h.usuario_admin}</td>
                <td>${new Date(h.fecha).toLocaleString()}</td>
                <td>${cambios}</td>
            </tr>
        `;
    });
};
