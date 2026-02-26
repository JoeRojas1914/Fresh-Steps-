document.addEventListener("DOMContentLoaded", () => {

    let ventaSeleccionada = null;

    function toggleDetalles(idVenta) {
        const fila = document.getElementById(`detalles-${idVenta}`);
        if (!fila) return;

        fila.style.display =
            fila.style.display === "none" || fila.style.display === ""
                ? "table-row"
                : "none";
    }

    document.querySelectorAll(".btn--info").forEach(btn => {
        btn.addEventListener("click", () => {
            toggleDetalles(btn.dataset.id);
        });
    });

    document.querySelectorAll(".btn-marcar-lista").forEach(btn => {
        btn.addEventListener("click", () => {
            ventaSeleccionada = btn.dataset.id;
            abrirModal("modalProcesado"); 
        });
    });

    const btnConfirmar = document.getElementById("btnConfirmarLista");

    if (btnConfirmar) {
        btnConfirmar.addEventListener("click", () => {

            if (!ventaSeleccionada) return;

            csrfFetch(`/ventas/marcar-lista/${ventaSeleccionada}`, {
                method: "POST"
            })
            .then(r => r.json())
            .then(res => {

                if (res.ok) {
                    cerrarModal("modalProcesado");
                    mostrarFeedback(res.message, "success");

                    setTimeout(() => location.reload(), 1000);

                } else {
                    mostrarFeedback(res.error || "Error al marcar como lista", "error");
                }

            });
        });
    }

        document.querySelectorAll(".btn-eliminar").forEach(btn => {
    btn.addEventListener("click", () => {

        const idVenta = btn.dataset.id;

        const confirmar = confirm(
            "¿Seguro que deseas eliminar esta venta?\n\n" +
            "Se eliminarán artículos y pagos relacionados.\n" +
            "Esta acción NO se puede deshacer."
        );

        if (!confirmar) return;

        csrfFetch(`/ventas/eliminar/${idVenta}`, {
            method: "POST"
        })
        .then(r => r.json())
        .then(res => {

            if (res.ok) {
                mostrarFeedback(res.message || "Venta eliminada", "success");

                const filaPrincipal = btn.closest("tr");
                const filaDetalles = document.getElementById(`detalles-${idVenta}`);

                if (filaPrincipal) filaPrincipal.remove();
                if (filaDetalles) filaDetalles.remove();

            } else {
                mostrarFeedback(res.error || "Error al eliminar", "error");
            }

        })
        .catch(() => {
            mostrarFeedback("Error de conexión", "error");
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