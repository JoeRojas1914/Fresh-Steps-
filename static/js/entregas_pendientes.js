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