function delChildren(elem) {
    while (elem.firstChild) {
        elem.removeChild(elem.firstChild);
    }
}

function defaultRequestHeaders() {
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken')
    }
}

function toggleMenu() {
    let element = document.getElementById("nav-column");
    if (element.style.display !== 'block') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

let notificationLoadTimestamp;

function loadNotifications() {
    const listElem = document.getElementById('notification-list');
    const clearBtn = listElem.querySelector('.clear');
    notificationLoadTimestamp = +new Date();
    fetch("/api/notification/list", {credentials: 'include'}
    ).then((r) => r.json()
    ).then((r) => {
        for (let entry of r.notifications) {
            let notification = document.createElement('a');
            notification.className = 'notification';
            let top = document.createElement('span');
            let bottom = document.createElement('span');
            let message = document.createElement('span');
            message.innerText = entry.message;
            let type = document.createElement('b');
            type.innerText = entry.type;
            let entity = document.createElement('b');
            entity.innerText = entry.entity;
            let timestamp = document.createElement('span');
            timestamp.innerText = entry.timestamp;
            if (entry.url !== undefined) notification.href = entry.url;
            top.appendChild(type);
            bottom.append(entity, timestamp);
            notification.append(top, message, bottom);
            listElem.insertBefore(notification, clearBtn);
            listElem.insertBefore(document.createElement('hr'), clearBtn)
        }
        notificationLoadTimestamp = r.timestamp;
    });
    clearBtn.addEventListener('click', clearNotifications);
}

function clearNotifications() {
    const e = document.getElementById('notifications');
    fetch("/api/notification/list", {
        method: 'DELETE',
        credentials: 'include',
        headers: defaultRequestHeaders(),
        body: JSON.stringify({'timestamp': notificationLoadTimestamp})
    }).then(() => {
        e.remove();
    });
}

function setupPopover(button) {
    const popover = button.parentNode.querySelector('.popover');
    let popperInstance = null;

    function show() {
        popover.setAttribute('data-show', '');
        popperInstance = Popper.createPopper(button, popover, {
            modifiers: [
                {name: 'offset', options: {offset: [0, 8]}},
            ],
        });
    }

    function hide(e) {
        if (e.target === popover || e.target.nodeName === 'A') return;
        popover.removeAttribute('data-show');
        if (popperInstance) {
            popperInstance.destroy();
            popperInstance = null;
        }
    }

    button.addEventListener('click', show);
    document.addEventListener('click', hide, true);
}

function loadTransportation(element, url) {
    fetch(url, {credentials: 'include'})
        .then(function (response) {
            return response.json();
        })
        .then(function (departures) {
            for (departure of departures) {
                let entry = document.createElement("div");
                entry.classList.add("pt-line");
                if (departure["name"] === "3") {
                    entry.classList.add("metro");
                } else {
                    entry.classList.add("bus");
                }
                let number = document.createElement("span");
                number.classList.add("number");
                number.textContent = departure["name"];
                entry.appendChild(number);
                let time = document.createElement("span");
                time.classList.add("time");
                time.textContent = departure["time"].substring(0, 5);
                entry.appendChild(time);
                let direction = document.createElement("span");
                direction.classList.add("direction");
                direction.textContent = departure["destination"];
                entry.appendChild(direction);
                element.appendChild(entry);
            }
            element.firstElementChild.remove();
        });
}

Date.prototype.addDays = function (days) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
};

const themes = ["Quasar", "Tokamak", "Nebula"];

function showThemePicker() {
    const cuts = [
        "0 0, 20% 0, 40% 100%, 0 100%",
        "20% 0, 50% 0, 75% 100%, 39.5% 100%",
        "50% 0, 100% 0, 100% 100%, 75% 100%"];
    let overlay = document.getElementById("overlay");
    delChildren(overlay);
    let container = document.createElement("div");
    container.style.position = "relative";
    container.style.marginTop = "10px";
    for (const [i, theme] of themes.entries()) {
        let themeDiv = document.createElement("div");
        themeDiv.classList.add("flex-pane");
        themeDiv.style.marginTop = "0";
        let titleContainer = document.createElement("div");
        titleContainer.classList.add("pane-title", "bg-grad");
        let title = document.createElement("h2");
        title.innerText = "Escolha o seu tema";
        titleContainer.appendChild(title);
        let contentContainer = document.createElement("div");
        contentContainer.classList.add("pane-content");
        let contentSpan = document.createElement("span");
        contentSpan.innerText = "Seleccione o tema que quer utilizar no supernova.";

        let picker = document.createElement("div");
        picker.style.display = "flex";
        picker.style.justifyContent = "space-between";
        picker.style.padding = "5px 0";

        for (const [j, other] of themes.entries()) {
            let btn = document.createElement("input");
            btn.type = "button";
            btn.value = other;
            if (i === j) {
                btn.onmouseover = function (e) {
                    showThemePreview(e)
                };
                btn.onclick = function (e) {
                    setTheme(e)
                };
            }
            picker.appendChild(btn);
        }
        contentContainer.appendChild(contentSpan);
        contentContainer.appendChild(picker);
        themeDiv.appendChild(titleContainer);
        themeDiv.appendChild(contentContainer);

        let themeWrapper = document.createElement("div");
        themeWrapper.setAttribute("data-theme", theme.toLowerCase());
        themeWrapper.style.clipPath = "polygon(" + cuts[i] + ")";
        themeWrapper.style.padding = "5px";
        if (i > 0) {
            themeWrapper.style.position = "absolute";
            themeWrapper.style.top = "0";
        }
        themeWrapper.appendChild(themeDiv);
        container.appendChild(themeWrapper);
    }
    overlay.appendChild(container);
    overlay.style.display = "inherit";
}

function showThemePreview(e) {
    let theme = e.target.value.toLowerCase();
    document.body.setAttribute("data-theme", theme);
}

function setTheme(e) {
    let theme = e.target.value.toLowerCase();
    if (typeof (Storage) !== "undefined") {
        localStorage.setItem("theme", theme);
        document.getElementById("overlay").style.display = "none";
    } else {
        alert("O navegador está a bloquear o armazenamento.");
    }
}

function loadTheme(promptIfUnset) {
    if (typeof (Storage) !== "undefined") {
        let theme = localStorage.getItem("theme");
        if (theme != null)
            document.body.setAttribute("data-theme", theme);
        else if (promptIfUnset)
            showThemePicker();
    } else {
        console.log("O navegador está a bloquear o armazenamento.");
    }
}

function showFilePreview(elem) {
    let fileElem = elem.closest('.file');
    let dlElem = fileElem.querySelector('.dllink')
    let previewElem = fileElem.querySelector('.preview')
    const mime = fileElem.dataset.mime;
    const src = dlElem.href + "?inline";
    delChildren(previewElem);
    let container;
    switch (mime.split('/')[0]) {
        case "text":
            container = document.createElement("div");
            break;
        case "application":
            if (mime === "application/pdf") {
                container = document.createElement("object");
                container.data = src;
                container.mime = mime;
            }
            break;
        case "image":
            container = document.createElement("img");
            container.src = src;
            break;
        case "video":
            container = document.createElement("video");
            container.src = src;
            break;
        case "audio":
            container = document.createElement("audio");
            container.src = src;
            break;
    }
    previewElem.appendChild(container);
    elem.remove();
}

function setSubscribeButton() {
    const b = document.getElementById("subscribe-btn")
    fetch(b.dataset.endpoint, {credentials: 'include', method: 'GET'})
        .then((response) => response.json())
        .then((val) => {
            b.innerText = val ? "Dessubscrever" : "Subscrever";
            b.dataset.val = val;
            b.addEventListener('click', clickSubscribe);
        }).catch(() => {
        b.remove()
    });
}

function clickSubscribe(e) {
    const b = e.target;
    if (b.dataset.val === "true") {
        fetch(b.dataset.endpoint, {
            method: 'DELETE',
            credentials: 'include',
            headers: defaultRequestHeaders()
        }).then(() => {
            b.innerText = "Subscrever"
            b.dataset.val = "false";
        });
    } else {
        fetch(b.dataset.endpoint, {
            method: 'POST',
            credentials: 'include',
            headers: defaultRequestHeaders()
        }).then(() => {
            b.innerText = "Dessubscrever";
            b.dataset.val = "true";
        });
    }
}