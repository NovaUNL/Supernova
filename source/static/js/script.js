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
    const b = $('#notifications');
    const p = b.find('.popover')[0];
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
    const o = $('<div class="overlay"></div>').prependTo('body');
    let p = $(
        "<div class='pane'>" +
        "<div class='pane-title'><h2></h2><span class='close'></span></div>" +
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
            "<div class='pane'>" +
            "<div class='pane-title'><h2>Escolha o seu tema</h2></div>" +
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

function loadTheme() {
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

function promptTutorial(force = false) {
    if (window.innerWidth < 1200 || window.innerHeight < 600)
        return; // Too small, could have issues
    if (force || (typeof (Storage) !== "undefined" && !localStorage.getItem("skipTutorial"))) {
        $('head').append('<link rel="stylesheet" type="text/css" href="/static/js/lib/intro/introjs.min.css">');
        $.getScript("/static/js/lib/intro/intro.min.js").done(() => {
            $.getScript("/static/js/tutorial.js");
        })
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
                elem.append($(`<span>${entry.building}</span>`));
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
    textInp.focus();
    textInp.on('keyup', (e) => {
        if (e.key === 'Enter' || e.keyCode === 13) btn.click()
    });
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
                        if (!selectedCategory && UID === -1)
                            results.append($(`<b>Utilizadores não autenticados tem visibilidade reduzida.</b>`));
                        results.append($(`<h3>${searchCols[key].loc.pt}</h3>`));
                        results.append(searchCols[key].display(subset));
                    }
                })
                .catch(() => {
                    loadSpinner.remove();
                    results.append($(`<b>Erro a realizar a pesquisa.</b>`));
                });
        }
    )
}

cathegoryCathegoryMappings = [null, null, // First two indexes are unused
    {'name': 'Slides', 'color': 'red'}, {'name': 'Problemas', 'color': 'green'},
    {'name': 'Protolos', 'color': 'yellow'}, {'name': 'Seminário', 'color': 'yellow'},
    {'name': 'Exame', 'color': 'blue'}, {'name': 'Teste', 'color': 'blue'},
    {'name': 'Suporte', 'color': 'orange'}, {'name': 'Outros', 'color': 'purple'}
]

function sizeStrFromBytes(bytes) {
    if (bytes >> 20)
        return (bytes >> 20) + " MB"
    if (bytes >> 10)
        return (bytes >> 10) + " KB"
    return bytes + " B"
}

function loadClassFiles(inst_id) {
    const officialPane = $(".pane .official-files");
    const communityPane = $(".pane .community-files");
    const listPaneBase = officialPane.parent();
    const oSpinner = spinner.clone()
    const cSpinner = spinner.clone()
    officialPane.append(oSpinner);
    communityPane.append(cSpinner);
    fetch(`/api/class/i/${inst_id}/files`, {credentials: 'include'})
        .then((r) => {
            return r.json()
        })
        .then((files) => {
            if (files.official.length > 0) {
                const listEl = $('<div class="file-list"></div>');
                _loadClassFiles_aux(listEl, files.official);
                officialPane.append(listEl)
            } else {
                officialPane.append($("<p>Esta unidade curricular não tem ficheiros oficiais públicos.</p>"));
            }
            if (files.community.length > 0) {
                const listEl = $('<div class="file-list"></div>');
                _loadClassFiles_aux(listEl, files.community);
                communityPane.append(listEl)
            } else {
                communityPane.append($("<p>A comunidade não adicionou ficheiros a esta unidade curricular.</p>"));
            }
            if (files.denied.length > 0) {
                const deniedPane = listPaneBase.clone(true);
                deniedPane.find('h2').text('Ficheiros restritos');
                deniedPane.find('p').remove();
                const listEl = $('<div class="file-list"></div>');
                _loadClassFiles_aux(listEl, files.denied);
                deniedPane.find('.pane-content').append(listEl);
                deniedPane.find('.open').parent().remove();
                deniedPane.find('.download').parent().remove();
                listPaneBase.parent().append(deniedPane);
            }
            $('.spinner').remove();
        }).catch(() => {
            $('.spinner').remove();
            officialPane.append($("<b>Erro a carregar os ficheiros.</b>"));
        }
    );
}

function _loadClassFiles_aux(listEl, files) {
    for (let ifile of files) {
        const category = cathegoryCathegoryMappings[ifile.category];
        const fileEl = $(
            '<div class="file">' +
            '<span class="type" data-balloon-pos="left"></span>' +
            '<a class="name" href="javascript: void(0)"></a>' +
            '<a class="author highres"></a>' +
            `<span class="size highres">${sizeStrFromBytes(ifile.file.size)}</span>` +
            '<span class="date midhighres">' +
            new Date(ifile.upload_datetime).toLocaleDateString("pt-PT") +
            '</span>' +
            '</div>');
        fileEl.append(createFileMenu(ifile));
        fileEl.find('.type').css('background-color', `var(--${category.color})`)
            .attr('aria-label', category.name);
        fileEl.find('.name').text(ifile.name).click(() => {
            showFilePreview(ifile);
        });
        const authEl = fileEl.find('.author');
        if (ifile.uploader)
            authEl.text(ifile.uploader.nickname).attr('href', ifile.uploader.url);
        else if (ifile.uploader_teacher)
            authEl.text(ifile.uploader_teacher.short_name).attr('href', ifile.uploader_teacher.url);

        listEl.append(fileEl)
    }
}

function createFileMenu(ifile) {
    const options = $('<ul class="option-list"></ul>');
    options.append($('<li></li>')
        .append($('<a class="open" href="javascript: void(0)">Abrir</a>').click(() => {
            showFilePreview(ifile)
        })));
    options.append($('<li></li>').append($(`<a class="download" href="${ifile.url}/download">Descarregar</a>`)));
    options.append($('<li></li>').append($(`<a href="${ifile.url}">Propriedades na UC</a>`)));
    options.append($('<li></li>').append($(`<a href="${ifile.file.url}">Propriedades globais</a>`)));

    const base = $(`<a class="options trigger" href="#${ifile.id}">⋮</a>` +
        `<div class="lightbox" id="${ifile.id}"><nav><a href="#" class="close"></a></nav></div>`);
    base.find('nav').append(options);
    return base;
}

function showFilePreview(ifile) {
    /**
     * Shows a preview overlay
     */
    const overlay = createOverlay();
    overlay.find('h2').text(ifile.name);
    const viewer = overlay.find('.pane-content').addClass('file-viewer');

    const mime = ifile.file.mime;
    const src = ifile.url + "/download?inline";
    let preview;
    switch (mime.split('/')[0]) {
        case "text":
            preview = document.createElement("div");
            break;
        case "application":
            if (mime === "application/pdf")
                preview = $(`<object data="${src}" type="${mime}"/>`).addClass('pdf');
            break;
        case "image":
            preview = $(`<img src="${src}"/>`);
            break;
        case "video":
            preview = $(`<video src="${src}"/>`);
            break;
        case "audio":
            preview = $(`<audio src="${src}"/>`);
            break;
        default:
            preview = $(`<div></div>`).text("Ficheiro sem pré-visualização");
            break;
    }
    viewer.append(preview.addClass('preview'));
    viewer.append($('<input type="button" value="download">').click(() => {
        window.open(ifile.url + "/download")
    }));
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