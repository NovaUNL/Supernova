function castVote(evt) {
    let e = evt.target;
    let is_set = e.classList.contains("set");
    let vote_type;
    if (e.classList.contains("upvote-btn")) {
        vote_type = 'up'
    } else if (e.classList.contains("downvote-btn")) {
        vote_type = 'down'
    } else if (e.classList.contains("answer-btn")) {
        vote_type = 'ans'
    } else if (e.classList.contains("fav-btn")) {
        vote_type = 'fav'
    }
    if (is_set) {
        e.classList.remove('set');
    } else {
        e.classList.add('set');
        if (vote_type === 'up')
            e.parentNode.querySelector(".downvote-btn").classList.remove('set');
        else if (vote_type === 'down')
            e.parentNode.querySelector(".upvote-btn").classList.remove('set');
    }
    let id = e.closest("[data-id]").dataset.id;
    let url = document.querySelector('[data-voting-endpoint]').dataset.votingEndpoint.replace("/0/", `/${id}/`);

    fetch(url, {
        method: is_set ? 'DELETE' : 'POST',
        credentials: 'include',
        headers: defaultRequestHeaders(),
        body: JSON.stringify({"type": vote_type})
    });
}

function loginAlert() {
    alert("Entre para votar.");
}

function loadOwnVotes() {
    let url = document.querySelector('[data-question-votes-endpoint]').dataset.questionVotesEndpoint;

    fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders()
    }).then(function (response) {
        return response.json();
    }).then((data) => {
        for (let postableElem of document.querySelectorAll(".postable")) {
            let votes = data[postableElem.dataset.id];
            [postableElem.querySelector('.upvote-btn'), postableElem.querySelector('.downvote-btn')]
                .forEach((elem, index) => {
                    elem.removeEventListener('click', loginAlert);
                    if (!elem.classList.contains('disabled')) elem.addEventListener('click', castVote)
                    if (typeof votes !== 'undefined' && votes.includes(index)) elem.classList.add('set')
                })
        }
    });
}

(function () {
    for (elem of document.querySelectorAll(".upvote-btn,.downvote-btn")) {
        elem.addEventListener('click', loginAlert);
    }
})();