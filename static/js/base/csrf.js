document.addEventListener("DOMContentLoaded", () => {

    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (!tokenMeta) return;

    const token = tokenMeta.content;

    document.querySelectorAll("form").forEach(form => {

        if (form.method.toUpperCase() === "POST") {

            if (!form.querySelector("input[name='csrf_token']")) {

                const input = document.createElement("input");
                input.type = "hidden";
                input.name = "csrf_token";
                input.value = token;

                form.appendChild(input);
            }
        }
    });
});
