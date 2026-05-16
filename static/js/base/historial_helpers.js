function renderDiff(h, entidad) {
    const antes   = h.datos_antes   ? JSON.parse(h.datos_antes)   : null;
    const despues = h.datos_despues ? JSON.parse(h.datos_despues) : null;

    if (h.accion === "RESTAURADO") return `${entidad} restaurado`;
    if (!antes && despues)         return `${entidad} creado`;
    if (antes  && !despues)        return `${entidad} eliminado`;

    if (antes && despues) {
        const diffs = Object.keys(despues)
            .filter(k => antes[k] !== despues[k])
            .map(k =>
                `<div><b>${escapeHtml(k)}</b>: ` +
                `<span style="color:#ef4444">${escapeHtml(String(antes[k] ?? ""))}</span>` +
                ` → ` +
                `<span style="color:#22c55e">${escapeHtml(String(despues[k] ?? ""))}</span></div>`
            );
        return diffs.length ? diffs.join("") : "Sin cambios";
    }

    return escapeHtml(h.accion);
}


async function abrirHistorial(url, modalId, tbodySelector, getCambios) {
    const tbody = document.querySelector(tbodySelector);
    if (!tbody) return;

    tbody.innerHTML = "<tr><td colspan='4'>Cargando...</td></tr>";
    abrirModal(modalId);

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error();
        const data = await res.json();

        if (!data.length) {
            tbody.innerHTML = "<tr><td colspan='4' style='text-align:center;opacity:.5;'>Sin historial</td></tr>";
            return;
        }

        tbody.innerHTML = data.map(h => `<tr>
            <td><b>${escapeHtml(h.accion)}</b></td>
            <td>${escapeHtml(h.usuario || h.usuario_admin || "—")}</td>
            <td>${new Date(h.fecha).toLocaleString("es-MX")}</td>
            <td>${getCambios(h)}</td>
        </tr>`).join("");
    } catch {
        tbody.innerHTML = "<tr><td colspan='4' style='text-align:center;opacity:.5;'>Error al cargar historial.</td></tr>";
    }
}
