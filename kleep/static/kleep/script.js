function authShowPrompt() {
    document.getElementById("overlay").style.display = 'block';
}

function overlayClose() {
    document.getElementById("overlay").style.display = 'none';
}

let kleep_opened_nav_stage = null;

function showSubmenu(id) {
    if (kleep_opened_nav_stage !== id) {
        let menu = document.getElementById(id);
        let container = menu.parentNode;
        menu.style.display = 'inline';
        container.style.height = '110px';
        container.style.borderBottom = '2px solid rgb(57, 130, 53)';
        console.log(kleep_opened_nav_stage);
        if (kleep_opened_nav_stage !== null) {
            document.getElementById(kleep_opened_nav_stage).style.display = 'none';
        }
        kleep_opened_nav_stage = id;
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