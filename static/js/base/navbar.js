document.addEventListener("DOMContentLoaded", () => {

    const navToggle = document.getElementById("navToggle");
    const navbar    = document.getElementById("navbar");

    if (navToggle && navbar) {
        navToggle.addEventListener("click", () => {
            navbar.classList.toggle("open");
        });
    }

    const userBtn      = document.getElementById("userBtn");
    const userMenu     = document.getElementById("userMenu");
    const userDropdown = document.getElementById("userDropdown");

    if (userBtn && userMenu && userDropdown) {
        userBtn.addEventListener("click", () => {
            userMenu.classList.toggle("show");
        });

        document.addEventListener("click", (e) => {
            if (!userDropdown.contains(e.target)) {
                userMenu.classList.remove("show");
            }
        });
    }

});