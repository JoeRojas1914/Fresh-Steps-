document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".btn-detalles[data-id]").forEach(btn => {
        btn.addEventListener("click", () => toggleDetalles(btn.dataset.id, btn));
    });

    document.querySelectorAll(".btn-historial-venta").forEach(btn => {
        btn.addEventListener("click", () => verHistorialVenta(btn.dataset.id));
    });

    const toggleEliminadas = document.getElementById("toggle-eliminadas");
    if (toggleEliminadas) {
        toggleEliminadas.addEventListener("change", () => toggleEliminadas.form.submit());
    }

});

async function verHistorialVenta(idVenta) {
    abrirModal("modalHistorialVenta");

    const tbody = document.querySelector("#tablaHistorialVenta tbody");
    tbody.innerHTML = "<tr><td colspan='4' class="text-center dim">Cargando...</td></tr>";

    try {
    const res  = await fetch(`/ventas/${idVenta}/historial`);
    if (!res.ok) throw new Error("Error de red");
    const data = await res.json();

    if (!data.length) {
        tbody.innerHTML = "<tr><td colspan='4' class="text-center dim">Sin historial registrado</td></tr>";
        return;
    }

    const iconos = {
        CREADO:    "",
        LISTA:     "",
        ENTREGADO: "",
        ELIMINADO: "",
    };

    tbody.innerHTML = data.map(h => {
        const icono  = iconos[h.accion]  || "•";
        const fecha  = new Date(h.fecha).toLocaleString("es-MX");

        let detalle = "—";
        if (h.accion === "CREADO" && h.datos_despues) {
            try {
                const d = JSON.parse(h.datos_despues);
                detalle = `Total: $${parseFloat(d.total || 0).toFixed(2)}`;
            } catch {}
        }

        return `<tr>
            <td><span class="accion-badge accion--${h.accion.toLowerCase()}">${escapeHtml(h.accion)}</span></td>
            <td>${escapeHtml(h.usuario || "—")}</td>
            <td>${fecha}</td>
            <td>${detalle}</td>
        </tr>`;
    }).join("");
    } catch {
        tbody.innerHTML = "<tr><td colspan='4' class="text-center dim">Error al cargar historial.</td></tr>";
    }
}