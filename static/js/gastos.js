document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector(".modal-form");
    if (!form) return;

    form.addEventListener("submit", function (e) {
        const descripcion = document.querySelector("[name=descripcion]").value.trim();
        const proveedor = document.querySelector("[name=proveedor]").value.trim();
        const total = document.querySelector("[name=total]").value;

        if (!descripcion || !proveedor || total === "") {
            mostrarFeedback("Descripción, proveedor y total son obligatorios.", "error");
            e.preventDefault();
            return;
        }

        if (parseFloat(total) < 0) {
            mostrarFeedback("El total no puede ser negativo.", "error");
            e.preventDefault();
        }
    });

});


let _pendingGastoUrl = null;

window.confirmarEliminarGasto = function (id) {
    _pendingGastoUrl = `/gastos/eliminar/${id}`;
    abrirModal("modalConfirmarEliminarGasto");
};

window.ejecutarEliminarGasto = function () {
    if (_pendingGastoUrl) location.href = _pendingGastoUrl;
};


window.editarGasto = function (
    id,
    id_negocio,
    descripcion,
    proveedor,
    total,
    fecha_registro,
    tipo_comprobante,
    tipo_pago
) {
    abrirModal("modalGasto");

    document.getElementById("modalGasto_title").innerText = "Editar gasto";

    document.getElementById("id_gasto").value = id;
    document.getElementById("id_negocio").value = id_negocio;
    document.querySelector("[name=descripcion]").value = descripcion;
    document.querySelector("[name=proveedor]").value = proveedor;
    document.querySelector("[name=total]").value = total;
    document.querySelector("[name=fecha_registro]").value = fecha_registro || "";
    document.getElementById("tipo_comprobante").value = tipo_comprobante;
    document.getElementById("tipo_pago").value = tipo_pago;
};




window.verHistorial = function (id) {
    abrirHistorial(
        `/gastos/${id}/historial`,
        "modalHistorial",
        "#tablaHistorial",
        h => renderDiff(h, "Gasto")
    );
};
