function toggleMenu() {
    let element = document.getElementById("nav-column");
    if (element.style.display !== 'block') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
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

function showThemePicker() {
    let themes = ["Quasar", "Tokamak", "Nebula"];
    let cuts = [
        "0 0, 20% 0, 40% 100%, 0 100%",
        "20% 0, 50% 0, 75% 100%, 39.5% 100%",
        "50% 0, 100% 0, 100% 100%, 75% 100%"];
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
            }
            picker.appendChild(btn);
        }
        contentContainer.appendChild(picker);

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
    document.getElementById("overlays").appendChild(container);
}

function showThemePreview(e) {
    let theme = e.target.value.toLowerCase();
    document.body.setAttribute("data-theme", theme);
}