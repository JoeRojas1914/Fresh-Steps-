let ventaEntregaActual = null;
let saldoPendienteActual = 0;

document.addEventListener("DOMContentLoaded", () => {

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

    document.querySelectorAll(".btn-entregar").forEach(btn => {
        btn.addEventListener("click", () => {

            const idVenta = parseInt(btn.dataset.id);
            const deuda   = parseFloat(btn.dataset.deuda);
            const pagado  = parseFloat(btn.dataset.pagado);
            const total   = parseFloat(btn.dataset.total);

            abrirModalEntrega(idVenta, deuda, pagado, total);
        });
    });

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


window.abrirModalEntrega = function (idVenta, deuda, pagado, total) {

    ventaEntregaActual = idVenta;
    saldoPendienteActual = deuda;

    abrirModal("modalEntrega");

    const bloquePago     = document.getElementById("bloquePago");
    const textoSinDeuda  = document.getElementById("textoSinDeuda");
    const btnConfirmar   = document.getElementById("btnConfirmarEntrega");

    if (deuda <= 0) {
        textoSinDeuda.style.display = "block";
        bloquePago.style.display = "none";
        btnConfirmar.onclick = confirmarEntregaSinPago;
    } else {
        textoSinDeuda.style.display = "none";
        bloquePago.style.display = "block";

        document.getElementById("montoPendiente").innerText =
            `$${deuda.toFixed(2)}`;

        btnConfirmar.onclick = confirmarPagoYEntrega;
    }
};


window.confirmarEntregaSinPago = function () {

    csrfFetch(`/ventas/entregar/${ventaEntregaActual}`, { method: "POST" })
        .then(r => r.json())
        .then(res => {
            if (res.ok) {
                cerrarModalEntrega();
                mostrarFeedback(res.message, "success");
                setTimeout(() => location.reload(), 1200);
            } else {
                mostrarFeedback(res.error || "Error al entregar", "error");
            }
        });
};


window.confirmarPagoYEntrega = function () {

    const metodo = document.getElementById("metodoPagoFinal").value;

    if (!metodo) {
        alert("Selecciona un método de pago");
        return;
    }

    csrfFetch("/ventas/pago-final", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id_venta: ventaEntregaActual,
            monto: saldoPendienteActual,
            metodo_pago: metodo
        })
    })
    .then(r => r.json())
    .then(res => {
        if (res.ok) {
            cerrarModalEntrega();
            mostrarFeedback(res.message, "success");
            setTimeout(() => location.reload(), 1200);
        } else {
            mostrarFeedback(res.error || "Error al registrar pago", "error");
        }
    });
};


window.mostrarFeedback = function (texto, tipo = "success") {

    const div = document.createElement("div");
    div.className = `alert ${tipo}`;
    div.innerText = texto;

    document.body.prepend(div);

    setTimeout(() => {
        div.remove();
    }, 3000);
};


window.cerrarModalEntrega = function () {
    cerrarModal("modalEntrega");

    const metodo = document.getElementById("metodoPagoFinal");
    if (metodo) metodo.value = "";

    const texto = document.getElementById("textoSinDeuda");
    const bloque = document.getElementById("bloquePago");

    if (texto) texto.style.display = "none";
    if (bloque) bloque.style.display = "none";
};
