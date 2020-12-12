const spinner = $('<img class="spinner" src="/static/img/spinner.svg">');
const themes = ["Quasar", "Tokamak", "Nebula"];

function delChildren(e) {
    /**
     * Deletes every child of an element
     * (TODO deprecate)
     */
    $(e).children().remove();
}

function defaultRequestHeaders() {
    /**
     * Headers used in most requests, with the csrf token attached to pass server protections
     */
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken')
    }
}

function toggleMenu() {
    /**
     * Toggles the main navigation menu (when browsing on a phone screen)
     */
    const s = $("#nav-column")[0].style;
    s.display = s.display !== 'block' ? 'block' : s.display = 'none';
}

let notificationLoadTimestamp;


function loadNotifications() {
    /**
     * Inserts notifications (n) inside the notification list (l)
     */
    const l = $('#notification-list');
    notificationLoadTimestamp = +new Date();
    fetch("/api/notification/list", {credentials: 'include'})
        .then((r) => r.json())
        .then((r) => {
            for (let n of r.notifications) {
                let e = $('<a class="notification">' +
                    `<span><b>${n.type ? n.type : ''}</b></span>` +
                    `<span>${n.message}</span>` +
                    `<span><b>${n.entity ? n.entity : ''}</b><span>${n.timestamp}</span></span>` +
                    '</a><hr>');
                l.append(e);
                if (n.url !== undefined) e.attr("href", n.url);
            }
            notificationLoadTimestamp = r.timestamp;
            l.append('<a class="clear" href="javascript: void(0)">Limpar notifícações</a><div class="arrow" data-popper-arrow></div>')
                .find('.clear').click(clearNotifications);
        });
}

function clearNotifications() {
    /**
     * Tags the shown notifications as seen and clears them.
     * FIXME: Prevent this from deleting yet unseen notifications
     */
    fetch("/api/notification/list", {
        method: 'DELETE',
        credentials: 'include',
        headers: defaultRequestHeaders(),
        body: JSON.stringify({'timestamp': notificationLoadTimestamp})
    }).then(() => $('#notifications').remove());
}

function setupPopover() {
    const b = $('#notification-btn');
    const p = $('#notifications').find('.popover')[0];
    let popperInstance = null;

    b.click(() => {
        p.setAttribute('data-show', '');
        popperInstance = Popper.createPopper(b[0], p, {
            modifiers: [
                {name: 'offset', options: {offset: [0, 8]}},
            ],
        });
    });

    document.addEventListener('click', (e) => {
        if (e.target === p || e.target.nodeName === 'A') return;
        p.removeAttribute('data-show');
        if (popperInstance) {
            popperInstance.destroy();
            popperInstance = null;
        }
    }, true);

    b.attr("href", "javascript: void(0)");
}

function loadTransportation() {
    /**
     * Loads data to the transportation widget
     */
    const widget = $("#transportation-widget");
    const loadSpinner = spinner.clone()
    loadSpinner.appendTo(widget);
    fetch(widget.data("endpoint"), {credentials: 'include'})
        .then((r) => {
            return r.json()
        })
        .then((departures) => {
            for (departure of departures) {
                const entry = $(
                    '<div class="pt-line">' +
                    `<span class="number">${departure["name"]}</span>` +
                    `<span class="time">${departure["time"].substring(0, 5)}</span>` +
                    `<span class="direction">${departure["destination"]}</span>` +
                    '</div>');
                if (departure["name"] === "3")
                    entry.addClass("metro")
                else
                    entry.addClass("bus")
                widget.append(entry);
            }
            loadSpinner.remove();
        });
}


function loadBOINC() {
    const widget = $('#boinc');
    const spin = spinner.clone();
    widget.append(spin);

    fetch(widget.data("endpoint"), {credentials: 'include'})
        .then((r) => {
            return r.json()
        })
        .then((stats) => {
            const t = $(
                "<table>" +
                "<thead><tr><td></td><th>Utilizador</th><th>Última semana</th></tr></thead>" +
                "<tbody class='user-data'></tbody>" +
                "<thead><tr><td></td><th>Projeto</th><th>Última semana</th></tr></thead>" +
                "<tbody class='project-data'></tbody>" +
                "</table>");
            const picNames = ['first', 'second', 'third'];
            const userRoot = t.find('.user-data');
            stats.users.sort((a, b) => b.weekly - a.weekly);
            stats.projects.sort((a, b) => b.weekly - a.weekly);
            for (const [i, u] of Object.entries(stats.users.slice(0, 3))) {
                const r = $(`<tr><td><img src="static/img/icons/${picNames[i]}.svg"></td><td>${u.name}</td><td>${u.weekly}</td></tr>`);
                userRoot.append(r);
            }
            const projectRoot = t.find('.project-data');
            for (const [i, p] of Object.entries(stats.projects.slice(0, 3))) {
                const r = $(`<tr><td><td>${p.name}</td><td>${p.weekly}</td></tr>`);
                projectRoot.append(r);
            }
            widget.append(t);
            spin.remove();
        });

    // '          <table>\n' +
    // '            <thead>\n' +
    // '            <tr>\n' +
    // '              <td></td>\n' +
    // '              <th>Utilizador</th>\n' +
    // '              <th>Última semana</th>\n' +
    // '            </tr>\n' +
    // '            </thead>\n' +
    // '            <tbody></tbody>\n' +
    // '            {% for user in boinc_users %}\n' +
    // '              <tr>\n' +
    // '                {% if forloop.counter == 1 %}\n' +
    // '                  <td><img src="{% static \'img/icons/first.svg\' %}"></td>\n' +
    // '                {% elif forloop.counter == 2 %}\n' +
    // '                  <td><img src="{% static \'img/icons/second.svg\' %}"></td>\n' +
    // '                {% elif forloop.counter == 3 %}\n' +
    // '                  <td><img src="{% static \'img/icons/third.svg\' %}"></td>\n' +
    // '                {% else %}\n' +
    // '                  <td></td>\n' +
    // '                {% endif %}\n' +
    // '                <td>{{ user.name }}</td>\n' +
    // '                <td>{{ user.weekly }}</td>\n' +
    // '              </tr>\n' +
    // '            {% endfor %}\n' +
    // '            <thead>\n' +
    // '            <tr>\n' +
    // '              <td></td>\n' +
    // '              <th>Projeto</th>\n' +
    // '              <th>Última semana</th>\n' +
    // '            </tr>\n' +
    // '            <tbody></tbody>\n' +
    // '            {% for project in boinc_projects %}\n' +
    // '              <tr>\n' +
    // '                <td></td>\n' +
    // '                <td>{{ project.name }}</td>\n' +
    // '                <td>{{ project.weekly }}</td>\n' +
    // '              </tr>\n' +
    // '            {% endfor %}\n' +
    // '            </thead>\n' +
    // '          </table>'
}

Date.prototype.addDays = function (days) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
};


function showThemePicker() {
    /**
     * Exhibits the prompt where the user can pick themes
     */
    const cuts = [
        "0 0, 20% 0, 40% 100%, 0 100%",
        "20% 0, 50% 0, 75% 100%, 39.5% 100%",
        "50% 0, 100% 0, 100% 100%, 75% 100%"];
    const overlay = $("#overlay");
    delChildren(overlay[0]);

    const container = $("<div class='theme-picker'></div>");
    for (const [i, theme] of themes.entries()) {
        let themeDiv = $(
            "<div class='flex-pane'>" +
            "<div class='pane-title bg-grad'><h2>Escolha o seu tema</h2></div>" +
            "<div class='pane-content'><span>Seleccione o tema que quer utilizar no supernova.</span></div>" +
            "</div>");
        const picker = $("<div class='theme-inputs'></div>");
        for (const [j, other] of themes.entries()) {
            const btn = $('<input type="button">');
            btn.val(other);
            if (i === j)
                btn.mouseover((e) => {
                    $("body").attr("data-theme", e.target.value.toLowerCase())
                }).click((e) => {
                    let theme = e.target.value.toLowerCase();
                    if (typeof (Storage) !== "undefined") {
                        localStorage.setItem("theme", theme);
                        $("#overlay").css("display", "none");
                    } else {
                        alert("O navegador está a bloquear o armazenamento.");
                    }
                });
            picker.append(btn);
        }
        themeDiv.find('.pane-content').append(picker);

        const wrap = $(`<div data-theme="${theme.toLowerCase()}" style="clip-path: polygon(${cuts[i]}); padding: 5px"></div>`);
        if (i > 0)
            wrap.css("position", "absolute").css("top", "0");

        wrap.append(themeDiv);
        container.append(wrap);
    }
    overlay.css("display", "inherit").append(container);
}

function loadTheme(prompt) {
    /**
     * Loads the user theme
     * @param prompt: Prompt for a theme if the user has no explicitly set theme
     */
    if (typeof (Storage) !== "undefined") {
        let theme = localStorage.getItem("theme");
        if (theme == null)
            $('body').attr("data-theme", "quasar");
        else
            $('body').attr("data-theme", theme);
    } else {
        console.log("O navegador está a bloquear o armazenamento.");
    }
}

function showFilePreview(elem) {
    /**
     * Shows a preview for a file in a file listing
     */
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
            if (mime !== "application/pdf") {
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
    /**
     * Loads a group subscribe button
     * @type {jQuery|HTMLElement}
     */
    const b = $("#subscribe-btn")
    fetch(b.data("endpoint"), {credentials: 'include', method: 'GET'})
        .then((r) => r.json())
        .then((val) => {
            b.text(val ? "Dessubscrever" : "Subscrever")
                .data("val", val)
                .click(clickSubscribe);
        }).catch(() => b.remove());
}

function clickSubscribe(e) {
    /**
     * Toggles a group subscription
     */
    const b = $(e.target);
    const val = b.data("val");
    fetch(b.data("endpoint"), {
        method: val ? 'DELETE' : 'POST',
        credentials: 'include',
        headers: defaultRequestHeaders()
    }).then(() => b.text(val ? "Subscrever" : "Dessubscrever").data("val", !val));
}