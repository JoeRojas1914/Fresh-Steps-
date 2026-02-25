document.addEventListener("DOMContentLoaded", () => {

    function toggleDetalles(idVenta) {
        const fila = document.getElementById(`detalles-${idVenta}`);
        if (!fila) return;

        fila.style.display =
            fila.style.display === "none" || fila.style.display === ""
                ? "table-row"
                : "none";
    }

    // Mostrar detalles
    document.querySelectorAll(".btn--info").forEach(btn => {
        btn.addEventListener("click", () => {
            toggleDetalles(btn.dataset.id);
        });
    });

    // Marcar como lista
    document.querySelectorAll(".btn-marcar-lista").forEach(btn => {
        btn.addEventListener("click", () => {

            const idVenta = btn.dataset.id;

            if (!confirm("¿Marcar esta venta como lista para entrega?")) return;

            csrfFetch(`/ventas/marcar-lista/${idVenta}`, {
                method: "POST"
            })
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    mostrarFeedback(res.message, "success");
                    setTimeout(() => location.reload(), 1000);
                } else {
                    mostrarFeedback(res.error || "Error al marcar como lista", "error");
                }
            });
        });
    });

});


function mostrarFeedback(texto, tipo = "success") {

    const div = document.createElement("div");
    div.className = `alert ${tipo}`;
    div.innerText = texto;

    document.body.prepend(div);

    setTimeout(() => {
        div.remove();
    }, 3000);
}