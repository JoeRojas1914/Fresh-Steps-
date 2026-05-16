function abrirModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add("is-open");
}

function cerrarModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove("is-open");
}

document.addEventListener("click", e => {
  const btnOpen = e.target.closest("[data-modal-open]");
  if (btnOpen) { abrirModal(btnOpen.dataset.modalOpen); return; }

  const btnClose = e.target.closest("[data-modal-close]");
  if (btnClose) { cerrarModal(btnClose.dataset.modalClose); return; }

  const modal = e.target.closest(".modal.is-open");
  if (!modal) return;
  if (e.target === modal) modal.classList.remove("is-open");
});
