(function () {
    loadTheme(true);
    let notifications = $('#notification-count');
    fetch("/api/notification/count", {credentials: 'include'})
        .then((response) => response.json())
        .then((count) => {
            if (count > 0) {
                notifications.text(count).css('visibility', 'visible');
                loadNotifications();
                setupPopover();
            }
        });
    fetch("/api/stars/gitlab/")
        .then((response) => response.json())
        .then((stars) => $('#gitlab-count').text(stars));
    fetch("/api/stars/github/")
        .then((response) => response.json())
        .then((stars) => $('#github-count').text(stars));
})();