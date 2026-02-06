window.csrfFetch = function (url, options = {}) {

    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (!tokenMeta) {
        console.error("CSRF token not found");
        return fetch(url, options);
    }

    const token = tokenMeta.getAttribute("content");

    options.headers = {
        ...options.headers,
        "X-CSRFToken": token,
        "Content-Type": "application/json"
    };

    return fetch(url, options);
};
