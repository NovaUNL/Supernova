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

let kleep_opened_nav_stage = null;

function showSubmenu(id) {
    if (kleep_opened_nav_stage !== id) {
        let menu = document.getElementById(id);
        let container = menu.parentNode;
        menu.style.display = 'inline';
        if (window.innerWidth > 1200) {
            container.style.height = '110px';
        } else if (window.innerWidth > 840){
            container.style.height = '70px';
        }else{
            container.style.height = 'auto';
        }
        container.style.borderBottom = '2px solid rgb(57, 130, 53)';
        console.log(kleep_opened_nav_stage);
        if (kleep_opened_nav_stage !== null) {
            document.getElementById(kleep_opened_nav_stage).style.display = 'none';
        }
        kleep_opened_nav_stage = id;
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

