document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector(".modal-form");
    if (!form) return;

    form.addEventListener("submit", function (e) {
        const negocio = document.getElementById("id_negocio").value;
        const nombre = document.querySelector("[name=nombre]").value.trim();
        const precio = document.querySelector("[name=precio]").value;

        if (!negocio || !nombre || precio === "") {
            alert("Negocio, nombre y precio son obligatorios.");
            e.preventDefault();
            return;
        }

        if (parseFloat(precio) < 0) {
            alert("El precio no puede ser negativo.");
            e.preventDefault();
        }
    });

});


window.abrirModal = function () {
    document.getElementById("modal").style.display = "block";
    document.getElementById("tituloModal").innerText = "Agregar servicio";
    document.getElementById("id_servicio").value = "";

    document.querySelector(".modal-form").reset();
};

window.cerrarModal = function () {
    document.getElementById("modal").style.display = "none";
};

window.editarServicio = function (btn) {
    window.abrirModal();
    document.getElementById("tituloModal").innerText = "Editar servicio";

    document.getElementById("id_servicio").value = btn.dataset.id;
    document.getElementById("id_negocio").value = btn.dataset.negocio;
    document.querySelector("[name=nombre]").value = btn.dataset.nombre;
    document.querySelector("[name=precio]").value = btn.dataset.precio;
};



window.cerrarHistorialServicio = function () {
    document.getElementById("modalHistorialServicio").style.display = "none";
};

window.verHistorialServicio = async function (id) {

    const modal = document.getElementById("modalHistorialServicio");
    const tbody = document.querySelector("#tablaHistorialServicio tbody");

    tbody.innerHTML = "<tr><td colspan='4'>Cargando...</td></tr>";
    modal.style.display = "block";

    const res = await fetch(`/servicios/${id}/historial`);
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

        if (h.accion === "CREADO") {
            cambios = "Servicio creado";
        }
        else if (h.accion === "EDITADO" && antes && despues) {
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
        }
        else if (h.accion === "ELIMINADO") {
            cambios = "Servicio eliminado";
        }
        else if (h.accion === "RESTAURADO") {
            cambios = "Servicio restaurado";
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
