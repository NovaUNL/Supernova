const NETWORK_TO_FA = [
    ['fab', 'fa-gitlab'],
    ['fab', 'fa-github'],
    ['fab', 'fa-linkedin'],
    ['fab', 'fa-mastodon'],
    ['fab', 'fa-vimeo'],
    ['fab', 'fa-youtube'],
    ['fab', 'fa-deviantart'],
    ['fab', 'fa-flickr'],
    ['fas', 'fa-cube'],
    ['fab', 'fa-wikipedia-w']
];

const NETWORK_URLS = [
    /*http, username prefix, username sufix*/
    [true, "https://gitlab.com/", ""],
    [true, "https://github.com/", ""],
    [true, "https://linkedin.com/in/", ""],
    [true, "https://vimeo.com/", ""],
    [true, "https://youtube.com/channel/", ""],
    [true, "https://", ".deviantart.com/"],
    [true, "https://flickr.com/photos/", ""],
    [true, "", ""],
    [true, "https://wikipedia.org/", ""]
];


function populateSocialNetworks(url, edit = false) {
    fetch(url, {
        credentials: 'include'
    }).then(function (response) {
        return response.json();
    }).then(function (socialNetworks) {
        for (account of socialNetworks) {
            addNetworkToList(account, document.getElementById("social-network-list"), edit);
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

function addNetworkToList(account, listElement, editable = false) {
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
    if (editable) {
        let delIconAnchor = document.createElement("span");
        let delIcon = document.createElement("i");
        delIconAnchor.classList.add('delete-icon');
        delIcon.classList.add("fas", "fa-times");
        delIconAnchor.appendChild(delIcon);
        line.appendChild(delIconAnchor);
        delIconAnchor.onclick = function () {
            deleteNetwork(account, this.parentNode);
        };
    }
    listElement.appendChild(line);
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