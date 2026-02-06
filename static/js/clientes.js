document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector(".modal-form");
    if (!form) return;

    form.addEventListener("submit", function (e) {
        const nombre = document.querySelector("[name=nombre]").value.trim();
        const apellido = document.querySelector("[name=apellido]").value.trim();
        const telefono = document.querySelector("[name=telefono]").value.trim();

        if (!nombre || !apellido || !telefono) {
            alert("Nombre, apellido y teléfono son obligatorios.");
            e.preventDefault();
            return;
        }

        if (!/^\d{10}$/.test(telefono)) {
            alert("El teléfono debe tener exactamente 10 dígitos.");
            e.preventDefault();
        }
    });

});


window.abrirModal = function () {
    document.getElementById("modal").style.display = "block";
    document.getElementById("modalTitulo").innerText = "Agregar cliente";
    document.getElementById("id_cliente").value = "";
};

window.cerrarModal = function () {
    document.getElementById("modal").style.display = "none";
};

window.editarCliente = function (e, id, nombre, apellido, correo, telefono, direccion) {
    e.stopPropagation();
    window.abrirModal();

    document.getElementById("modalTitulo").innerText = "Editar cliente";
    document.getElementById("id_cliente").value = id;

    document.querySelector("[name=nombre]").value = nombre;
    document.querySelector("[name=apellido]").value = apellido;
    document.querySelector("[name=correo]").value = correo || "";
    document.querySelector("[name=telefono]").value = telefono;
    document.querySelector("[name=direccion]").value = direccion || "";
};

window.cerrarHistorialCliente = function () {
    document.getElementById("modalHistorialCliente").style.display = "none";
};

window.verHistorialCliente = async function (e, id) {
    e.stopPropagation();

    const modal = document.getElementById("modalHistorialCliente");
    const tbody = document.querySelector("#tablaHistorialCliente tbody");

    tbody.innerHTML = "<tr><td colspan='4'>Cargando...</td></tr>";
    modal.style.display = "block";

    const res = await fetch(`/clientes/${id}/historial`);
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

        if (h.accion === "RESTAURADO") {
            cambios = "<span>Cliente restaurado</span>";
        } else if (antes && despues) {
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
            cambios = "Cliente creado";
        } else {
            cambios = "Cliente eliminado";
        }

        tbody.innerHTML += `
            <tr>
                <td><b>${h.accion}</b></td>
                <td>${h.usuario}</td>
                <td>${new Date(h.fecha).toLocaleString()}</td>
                <td>${cambios}</td>
            </tr>
        `;
    });
};
