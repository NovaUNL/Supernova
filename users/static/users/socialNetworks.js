const NETWORK_TO_FA = [
    ['fab', 'fa-gitlab'], ['fab', 'fa-github'], ['fab', 'fa-reddit'], ['fab', 'fa-discord'],
    ['fab', 'fa-linkedin'], ['fab', 'fa-twitter'], ['fab', 'fa-google-plus'], ['fab', 'fa-facebook'],
    ['fab', 'fa-vimeo'], ['fab', 'fa-youtube'], ['fab', 'fa-deviantart'], ['fab', 'fa-instagram'],
    ['fab', 'fa-flickr'], ['fas', 'fa-film'], ['fab', 'fa-imdb']
];

const NETWORK_URLS = [
    /*http, username prefix, username sufix*/
    [true, "https://gitlab.com/", ""],
    [true, "https://github.com/", ""],
    [true, "https://reddit.com/user/", ""],
    [false, "", ""],
    [true, "https://linkedin.com/in/", ""],
    [true, "https://twitter.com/", ""],
    [true, "https://plus.google.com/+", ""],
    [true, "https://facebook.com/", ""],
    [true, "https://vimeo.com/", ""],
    [true, "https://youtube.com/channel/", ""],
    [true, "https://", ".deviantart.com/"],
    [true, "https://instagram.com/p/", ""],
    [true, "https://flickr.com/photos/", ""],
    [true, "https://myanimelist.net/profile/", ""],
    [true, "https://imdb.com/user/", ""]
];


function populateSocialNetworks(url) {
    fetch(url, {
        credentials: 'include'
    }).then(function (response) {
        return response.json();
    }).then(function (socialNetworks) {
        for (account of socialNetworks) {
            addNetworkToList(account, document.getElementById("social-network-list"));
        }
    });
}


function addNetwork() {
    let networkElement = document.getElementById("network");
    let linkElement = document.getElementById("network-link");
    let account = {'network': networkElement.value, 'profile': linkElement.value};
    linkElement.value = null;

    fetch(apiURL, {
        method: 'PUT',
        body: JSON.stringify(account),
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': jQuery("[name=csrfmiddlewaretoken]").val()
        }),
        credentials: 'include',
    }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(response => {
            console.log('Added ' + account + ':', response);
            addNetworkToList(account, document.getElementById("social-network-list"))
        });
}

function addNetworkToList(account, listElement) {
    let line = document.createElement("li");
    let icon = document.createElement("i");
    if (account.network <= NETWORK_TO_FA.length) {
        icon.classList.add(...NETWORK_TO_FA[account.network]);
    } else {
        icon.classList.add("fas", "fa-question");
    }
    line.appendChild(icon);
    let link = document.createElement("a");
    if (account.network <= NETWORK_URLS.length) {
        let network_url = NETWORK_URLS[account.network];
        if (network_url[0]) {
            link.href = " " + network_url[1] + account.profile + network_url[2] + " ";
        }
    }
    link.text = " " + account.profile + " ";
    line.appendChild(link);
    let delIconAnchor = document.createElement("span");
    let delIcon = document.createElement("i");
    delIconAnchor.classList.add('delete-icon');
    delIcon.classList.add("fas", "fa-times");
    delIconAnchor.appendChild(delIcon);
    line.appendChild(delIconAnchor);
    listElement.appendChild(line);

    delIconAnchor.onclick = function () {
        deleteNetwork(account, this.parentNode);
    };
}

function deleteNetwork(account, listElement) {
    fetch(apiURL, {
        method: 'DELETE',
        body: JSON.stringify(account),
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': jQuery("[name=csrfmiddlewaretoken]").val()
        }),
        credentials: 'include',
    }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(response => {
            console.log('Deleted ' + account.network + ':', response);
            listElement.remove();
        });
}