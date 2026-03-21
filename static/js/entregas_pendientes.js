document.addEventListener("DOMContentLoaded", () => {

    let ventaSeleccionada = null;

    const detallesCargados = {};

    function toggleDetalles(idVenta) {
        const fila = document.getElementById(`detalles-${idVenta}`);
        const lista = document.getElementById(`lista-detalles-${idVenta}`);

        if (!fila || !lista) return;

        const visible = fila.style.display === "table-row";

        if (visible) {
            fila.style.display = "none";
            return;
        }

        fila.style.display = "table-row";

        if (detallesCargados[idVenta]) return;

        lista.innerHTML = `<li style="opacity:0.6;">⏳ Cargando detalles...</li>`;

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
                        html += `👟 ${item.datos.tipo} ${item.datos.marca}`;
                    }

                    else if (item.tipo_articulo === "confeccion") {
                        html += `🧵 ${item.datos.tipo} ${item.datos.marca}`;
                    }

                    else if (item.tipo_articulo === "maquila") {
                        html += `🏭 ${item.datos.tipo}`;
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

                setTimeout(() => {
                    location.reload();
                }, 800);
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