const html = document.documentElement;

const atual = html.getAttribute("data-bs-theme");

if(atual === "dark"){
    html.setAttribute("data-bs-theme","light");
}else{
    html.setAttribute("data-bs-theme","dark");
}