const detallesCargados = {};

function toggleDetallesVenta(idVenta) {
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

    lista.innerHTML = `<li style="opacity:0.6;">⏳ Cargando...</li>`;

    fetch(`/ventas/detalles/${idVenta}`)
        .then(r => r.json())
        .then(detalles => {

            detallesCargados[idVenta] = true;

            if (!detalles.length) {
                lista.innerHTML = `<li>Sin detalles</li>`;
                return;
            }

            lista.innerHTML = detalles.map(item => {
                return `<li>${item.tipo_articulo}</li>`;
            }).join("");
        })
        .catch(() => {
            lista.innerHTML = `<li>Error</li>`;
        });
}