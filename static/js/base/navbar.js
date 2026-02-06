document.addEventListener("DOMContentLoaded", () => {

    const navToggle = document.getElementById("navToggle");
    const navLinks = document.getElementById("navLinks");

    if (navToggle && navLinks) {
        navToggle.addEventListener("click", () => {
            navLinks.classList.toggle("active");
        });
    }

    const userBtn = document.getElementById("userBtn");
    const userMenu = document.getElementById("userMenu");
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
