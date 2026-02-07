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
  const modal = e.target.closest(".modal.is-open");
  if (!modal) return;

  if (e.target === modal) {
    modal.classList.remove("is-open");
  }
});
