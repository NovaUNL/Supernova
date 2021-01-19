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
    const menu = $("#nav-column");
    const content = $("#content-column");
    const display = menu.css('display');
    if (display === 'block') {
        menu.css('display', 'none');
        content.css('display', 'block');
    } else {
        menu.css('display', 'block');
        content.css('display', 'none');
    }
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

function createOverlay() {
    const o = $('<div class="overlay"></div>').appendTo('body');
    let p = $(
        "<div class='flex-pane'>" +
        "<div class='pane-title bg-grad'><h2></h2><span class='close'></span></div>" +
        "<div class='pane-content'></div>" +
        "</div>");
    o.append(p);
    p.find('.close').click(() => o.remove());
    return p;
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
}

Date.prototype.addDays = function (days) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
};

Date.prototype.addMinutes = function (minutes) {
    this.setMinutes(this.getMinutes() + minutes);
    return this;
};

function showThemePicker() {
    /**
     * Exhibits the prompt where the user can pick themes
     */
    const cuts = [
        "0 0, 20% 0, 40% 100%, 0 100%",
        "20% 0, 50% 0, 75% 100%, 39.5% 100%",
        "50% 0, 100% 0, 100% 100%, 75% 100%"];

    const p = createOverlay();
    const overlay = p.parent();
    p.remove();

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
                        $(".overlay").css("display", "none");
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


const searchCols = {
    'teacher': {
        'loc': {'en': 'Teacher', 'pt': 'Professor'},
        'icon': 'teacher.svg',
        'public': false,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img class="circle" src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                container.append(elem);
            }
            return container;
        }
    },
    'student': {
        'loc': {'en': 'Student', 'pt': 'Estudante'},
        'icon': 'student.svg',
        'public': false,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img class="circle" src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                container.append(elem);
            }
            return container;
        }
    },
    'building': {
        'loc': {'en': 'Building', 'pt': 'Edifício'},
        'icon': 'building.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                container.append(elem);
            }
            return container;
        }
    },
    'room': {
        'loc': {'en': 'Room', 'pt': 'Sala'},
        'icon': 'door.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                container.append(elem);
            }
            return container;
        }
    },
    'class': {
        'loc': {'en': 'Classe', 'pt': 'U.Curricular'},
        'icon': 'books.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                // elem.append($(`<span>2015-2020, Dept. Informática, 50 alunos.</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'course': {
        'loc': {'en': 'Course', 'pt': 'Curso'},
        'icon': 'scientist.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                elem.append($(`<span>2015-2020, Dept. Informática, 50 alunos.</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'department': {
        'loc': {'en': 'Department', 'pt': 'Dept.'},
        'icon': 'flagbuilding.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            items.forEach((entry) =>
                container.append($(`<div class="result"><h3><a href="${entry.url}">${entry.name}</a></h3></div>`)));
            return container;
        }
    },
    'document': {
        'loc': {'en': 'Document', 'pt': 'Documento'},
        'icon': 'document.svg',
        'public': false,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                elem.append($(`<span>foo.zip; bar.zip</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'group': {
        'loc': {'en': 'Group', 'pt': 'Grupo'},
        'icon': 'collaboration.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                elem.append($(`<span>${entry.abbreviation}</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'synopsis': {
        'loc': {'en': 'Synopsis', 'pt': 'Síntese'},
        'icon': 'notes.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                elem.append($(`<h3><a href="${entry.url}">${entry.title}</a></h3>`));
                // elem.append($(`<span>Parent; Classes</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'exercise': {
        'loc': {'en': 'Exercise', 'pt': 'Exercício'},
        'icon': 'pencil.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                elem.append($(`<h3><a href="${entry.url}">${entry.id}</a></h3>`));
                // elem.append($(`<span>Foo, Bar, Baz</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'question': {
        'loc': {'en': 'Question', 'pt': 'Questão'},
        'icon': 'question.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                elem.append($(`<h3><a href="${entry.url}">${entry.title}</a></h3>`));
                elem.append($(`<span>Foo, Bar, Baz</span>`));
                container.append(elem);
            }
            return container;
        }
    },
    'service': {
        'loc': {'en': 'Service', 'pt': 'Serviço'},
        'icon': 'services.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.name}</a></h3>`));
                container.append(elem);
            }
            return container;
        }
    },
    'news': {
        'loc': {'en': 'News Item', 'pt': 'Notícia'},
        'icon': 'newspaper.svg',
        'public': true,
        'display': function (items) {
            const container = $('<div class="indented"></div>');
            for (const entry of items) {
                const elem = $('<div class="result"></div>');
                if (entry.thumb)
                    elem.append($(`<img src="${entry.thumb}">`));
                elem.append($(`<h3><a href="${entry.url}">${entry.title}</a></h3>`));
                elem.append($(`<span>${entry.summary}</span>`));
                container.append(elem);
            }
            return container;
        }
    },
}

function showSearch() {
    /**
     * Shows the search prompt
     */
    let selectedCategory = null;

    const p = createOverlay();
    p.addClass('search');
    p.find('h2').text('Pesquisar');
    const textInp = $('<input type="search">');
    const btn = $('<input type="button" value="🔍">');
    const inputs = $('<div class="inputs"></div>').append(textInp).append(btn);
    const results = $('<div class="results"></div>').css('flex-grow', 1);
    const categories = $('<div class="categories"></div>');
    p.find('.pane-content').append(inputs).append(results).append(categories);
    for (const [key, category] of Object.entries(searchCols)) {
        const disabled = UID === -1 && !category.public;
        const elem = $(`<div id="search-category-${key}" class="category ${disabled ? "disabled" : ""}">
            <img src="/static/img/icons/${category.icon}">
            <h3>${category.loc.pt}</h3>
            </div>`);
        categories.append(elem);
        if (disabled) continue;
        elem.click(() => {
            categories.find('.category').removeClass('set');
            elem.addClass('set');
            categories.addClass('picked');
            selectedCategory = key;
        });
    }

    btn.click(() => {
        results.css('display', 'block');
        results.children().remove();
        const loadSpinner = spinner.clone()
        results.append(loadSpinner);
        const query = textInp.val();
        fetch(`/api/search?q=${query}${selectedCategory ? "&e=" + selectedCategory : ""}`,
            {credentials: 'include', method: 'GET'})
            .then((r) => r.json())
            .then((val) => {
                loadSpinner.remove();
                for (const [key, subset] of Object.entries(val.results)) {
                    if(!selectedCategory && UID === -1)
                        results.append($(`<b>Utilizadores não autenticados tem visibilidade reduzida.</b>`));
                    results.append($(`<h3>${searchCols[key].loc.pt}</h3>`));
                    results.append(searchCols[key].display(subset));
                }
            });
    }
)
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