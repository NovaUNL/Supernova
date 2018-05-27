function authShowPrompt() {
    document.getElementById("overlay").style.display = 'block';
}

function overlayClose() {
    document.getElementById("overlay").style.display = 'none';
}

let hamburgerMenuDisplayed = false;

function toggleHamburger() {
    let navigation = document.getElementById("main-navigation");

    if (hamburgerMenuDisplayed) {
        navigation.style.display = 'none';
    } else {
        navigation.style.display = 'block';
    }
    hamburgerMenuDisplayed = !hamburgerMenuDisplayed;
}

let openedNavStageElem = null;

function showSubmenu(id) {
    if (openedNavStageElem !== id) {
        let menu = document.getElementById(id);
        let container = menu.parentNode;
        menu.style.display = 'inline';
        if (window.innerWidth > 1200) {
            container.style.height = '110px';
        } else if (window.innerWidth > 840) {
            container.style.height = '70px';
        } else {
            container.style.height = 'auto';
        }
        container.style.borderBottom = '2px solid rgb(57, 130, 53)';
        console.log(openedNavStageElem);
        if (openedNavStageElem !== null) {
            document.getElementById(openedNavStageElem).style.display = 'none';
        }
        openedNavStageElem = id;
    }
    // The mobile interface was used, close it
    if (hamburgerMenuDisplayed) {
        toggleHamburger();
    }
}


function showStudentSubmenu() {
    showSubmenu("student_nav_stage");
}

function showUniversitySubmenu() {
    showSubmenu("university_nav_stage");
}

function showCommunitySubmenu() {
    showSubmenu("community_nav_stage");
}

function closeSubmenu() {
    let container = document.getElementById("nav_stage");
    container.style.height = '0';
    container.style.borderBottom = 'none';
}

let sidebarDisplayed = false;

function toggleSidebar() {
    if (sidebarDisplayed) {
        document.getElementById("middle").style.left = '-250px';
    } else {
        document.getElementById("middle").style.left = '0';
    }
    sidebarDisplayed = !sidebarDisplayed;
}