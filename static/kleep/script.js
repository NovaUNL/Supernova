function authShowPrompt() {
    document.getElementById("overlay").style.display = 'block';
}

function overlayClose() {
    document.getElementById("overlay").style.display = 'none';
}

studentMenuItems = [
    {'name': 'Horario', 'url': '/#1', 'auth_required': false, 'icon': 'fa-clock'},
    {'name': 'Calendario', 'url': '/#1', 'auth_required': false, 'icon': 'fa-calendar'},
    {'name': 'Avaliações', 'url': '/#3', 'auth_required': false, 'icon': 'fa-star'},
    {'name': 'Curso', 'url': '/#4', 'auth_required': false, 'icon': 'fa-graduation-cap'}
];

universityItems = [
    {'name': 'Campus', 'url': '/campus/', 'auth_required': false, 'icon': 'fa-map'},
    {'name': 'Departamentos', 'url': '/departamentos/', 'auth_required': false, 'icon': 'fa-graduation-cap'},
    {'name': 'Noticias', 'url': '/noticias/', 'auth_required': false, 'icon': 'fa-newspaper'},
    {'name': 'Eventos', 'url': '/eventos/', 'auth_required': false, 'icon': 'fa-bullhorn'},
    {'name': 'Grupos', 'url': '/grupos/', 'auth_required': false, 'icon': 'fa-users'},
    {'name': 'Menus', 'url': '/#2', 'auth_required': false, 'icon': 'fa-utensils'}
];

communityItems = [
    {'name': 'Resumos', 'url': '/#1', 'auth_required': false, 'icon': 'fa-book'},
    {'name': 'Artigos', 'url': '/#2', 'auth_required': false, 'icon': 'fa-pencil-alt'},
    {'name': 'Grupos', 'url': '/grupos', 'auth_required': false, 'icon': 'fa-users'},
    {'name': 'Classificados', 'url': '/#3', 'auth_required': false, 'icon': 'fa-trash'},
    {'name': 'Opiniões', 'url': '/#3', 'auth_required': false, 'icon': 'fa-comments'},
    {'name': 'Loja', 'url': '/#3', 'auth_required': false, 'icon': 'fa-euro-sign'}
];

function showSubmenu(items) {
    let container = document.getElementById("nav_stage");
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    let closeIcon = document.createElement('a');
    closeIcon.classList.add('fas', 'fa-angle-double-up');
    let closeButton = document.createElement('a');
    closeButton.appendChild(closeIcon);
    closeButton.id = 'nav_stage_close_button';
    closeButton.href = 'javascript:closeSubmenu();';
    container.appendChild(closeButton);

    for (let item of items) {
        let link = document.createElement('a');
        link.href = item.url;
        let icon = document.createElement('i');
        icon.classList.add('fas', item.icon);
        icon.style.fontSize = '3em'; // TODO to CSS
        link.appendChild(icon);
        link.appendChild(document.createElement('br'));
        link.appendChild(document.createTextNode(item.name));
        container.appendChild(link);
    }
    container.style.height = '110px';
    container.style.borderBottom = '2px solid rgb(57, 130, 53)';
}

function showStudentSubmenu() {
    showSubmenu(studentMenuItems);
}

function showUniversitySubmenu() {
    showSubmenu(universityItems);
}

function showCommunitySubmenu() {
    showSubmenu(communityItems);
}

function closeSubmenu() {
    let container = document.getElementById("nav_stage");
    container.style.height = '0px';
    container.style.borderBottom = 'none';
}