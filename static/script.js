let menuIcon = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

menuIcon.onclick = () => {
    menuIcon.classList.toggle('bx-x');
    navbar.classList.toggle('active');
}

let darkmode = localStorage.getItem('darkmode');
const themeSwitch = document.querySelector('#theme-switch');

const enableDarkMode = () => {
    document.body.classList.add('dark-mode');
    document.body.classList.remove('light-mode');
    localStorage.setItem('darkmode', 'active');
};

const disableDarkMode = () => {
    document.body.classList.remove('dark-mode');
    document.body.classList.add('light-mode');
    localStorage.setItem('darkmode', null);
};

// Initialisation
if (darkmode === "active") {
    enableDarkMode();
} else {
    disableDarkMode();
}

themeSwitch.addEventListener("click", () => {
    darkmode = localStorage.getItem('darkmode');
    darkmode !== "active" ? enableDarkMode() : disableDarkMode();
});