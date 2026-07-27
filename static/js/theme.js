const html = document.documentElement;

const theme = localStorage.getItem("theme") || "light";

html.setAttribute("data-bs-theme", theme);

function toggleTheme(){

    const current = html.getAttribute("data-bs-theme");

    const next = current === "light" ? "dark" : "light";

    html.setAttribute("data-bs-theme", next);

    localStorage.setItem("theme", next);

}