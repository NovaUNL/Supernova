(function () {
    loadTheme(true);
    let notifications = document.getElementById('notification-count');
    if (notifications != null) {
        fetch("/api/notification/count", {credentials: 'include'})
            .then((response) => response.json())
            .then((count) => {
                if (count > 0) {
                    notifications.innerText = count;
                    notifications.style.visibility = "visible";
                    loadNotifications();
                    const btn = document.getElementById('notification-btn');
                    setupPopover(btn);
                    btn.href = "javascript: void(0)";
                }
            });
    }
    let glCount = document.getElementById('gitlab-count');
    if (glCount != null) {
        fetch("/api/stars/gitlab/")
            .then((response) => response.json())
            .then((stars) => glCount.innerText = stars);
    }
    let ghCount = document.getElementById('github-count');
    if (ghCount != null) {
        fetch("/api/stars/github/")
            .then((response) => response.json())
            .then((stars) => ghCount.innerText = stars);
    }
})();