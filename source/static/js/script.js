function toggleMenu() {
    let element = document.getElementById("nav-column");
    if (element.style.display !== 'block') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}