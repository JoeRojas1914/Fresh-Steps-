let ventaEntregaActual = null;
let saldoPendienteActual = 0;

document.addEventListener("DOMContentLoaded", () => {

    const detallesCargados = {};

    function toggleDetalles(idVenta) {
        const fila = document.getElementById(`detalles-${idVenta}`);
        const lista = document.getElementById(`lista-detalles-${idVenta}`);

        if (!fila || !lista) return;

        const visible = fila.style.display === "table-row" || fila.style.display === "";

        if (visible) {
            fila.style.display = "none";
            return;
        }

        fila.style.display = "table-row";

        if (detallesCargados[idVenta]) return;

        lista.innerHTML = `<li style="opacity:0.6;">Cargando Detalles...</li>`;

        fetch(`/ventas/detalles/${idVenta}`)
            .then(r => r.json())
            .then(detalles => {

                detallesCargados[idVenta] = true;

                if (!detalles.length) {
                    lista.innerHTML = `<li>Sin detalles</li>`;
                    return;
                }

                lista.innerHTML = detalles.map(item => {

                    let html = "";

                    if (item.tipo_articulo === "calzado") {
                        html += `
                            <div class="detalle-zapato">
                                👟 ${item.datos.tipo} ${item.datos.marca}
                            </div>
                        `;

                        html += item.servicios.map(s => `
                            <div class="detalle-servicio">
                                ${s.nombre}
                                <span class="detalle-precio">
                                    $${parseFloat(s.precio_aplicado).toFixed(2)}
                                </span>
                            </div>
                        `).join("");
                    }

                    else if (item.tipo_articulo === "confeccion") {
                        html += `
                            <div class="detalle-zapato">
                                🧵 ${item.datos.tipo} ${item.datos.marca}
                            </div>
                            <div>
                                Cantidad: <b>${item.datos.cantidad}</b>
                            </div>
                        `;

                        html += item.servicios.map(s => `
                            <div class="detalle-servicio">
                                ${s.nombre}
                                <span class="detalle-precio">
                                    $${parseFloat(s.precio_aplicado).toFixed(2)}
                                </span>
                            </div>
                        `).join("");
                    }

                    else if (item.tipo_articulo === "maquila") {
                        html += `
                            <div class="detalle-zapato">
                                🏭 ${item.datos.tipo}
                            </div>
                            <div>
                                Cantidad: <b>${item.datos.cantidad}</b> |
                                Precio: <b>$${parseFloat(item.datos.precio_unitario).toFixed(2)}</b>
                            </div>
                        `;
                    }

                    if (item.comentario) {
                        html += `
                            <div style="margin-top:6px; font-style:italic; opacity:0.8;">
                                💬 ${item.comentario}
                            </div>
                        `;
                    }

                    return `<li class="detalle-item">${html}</li>`;
                }).join("");
            })
            .catch(() => {
                lista.innerHTML = `<li>Error al cargar detalles</li>`;
            });
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
