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

    document.querySelectorAll(".btn-info").forEach(btn => {
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


    const inputBuscador = document.getElementById("buscador-cliente");
    const selectNegocio = document.getElementById("filtro-negocio");

    if (inputBuscador && selectNegocio) {

        function aplicarFiltros() {
            const filtroNombre  = inputBuscador.value.toLowerCase();
            const filtroNegocio = selectNegocio.value.toLowerCase();

            const filas = document.querySelectorAll("#tabla-ventas tbody tr");

            filas.forEach(fila => {

                if (fila.classList.contains("detalles-venta")) return;

                const nombreCliente = fila.cells[2].textContent.toLowerCase();
                const negocio       = fila.cells[1].textContent.toLowerCase();

                const coincideNombre  = nombreCliente.includes(filtroNombre);
                const coincideNegocio =
                    filtroNegocio === "" || negocio.includes(filtroNegocio);

                const mostrar = coincideNombre && coincideNegocio;
                fila.style.display = mostrar ? "" : "none";

                // Ocultar detalle si se filtra
                const btnInfo = fila.querySelector(".btn-info");
                if (btnInfo) {
                    const idVenta = btnInfo.dataset.id;
                    const filaDetalle = document.getElementById(`detalles-${idVenta}`);
                    if (filaDetalle) filaDetalle.style.display = "none";
                }
            });
        }

        inputBuscador.addEventListener("keyup", aplicarFiltros);
        selectNegocio.addEventListener("change", aplicarFiltros);
    }

});



window.abrirModalEntrega = function (idVenta, deuda, pagado, total) {

    ventaEntregaActual = idVenta;
    saldoPendienteActual = deuda;

    document.getElementById("modalEntrega").style.display = "block";

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

window.cerrarModalEntrega = function () {
    document.getElementById("modalEntrega").style.display = "none";
    document.getElementById("metodoPagoFinal").value = "";
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
