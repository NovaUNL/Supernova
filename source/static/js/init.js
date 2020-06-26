(function () {
    loadTheme();
    let glCount = document.getElementById('gitlab-count');
    if (glCount != null) {
        fetch("/api/stars/gitlab/")
            .then(function (response) {
                return response.json();
            })
            .then(function (stars) {
                glCount.innerText = stars
            });
    }
    let ghCount = document.getElementById('github-count');
    if (ghCount != null) {
        fetch("/api/stars/github/")
            .then(function (response) {
                return response.json();
            })
            .then(function (stars) {
                ghCount.innerText = stars
            });
    }
})();