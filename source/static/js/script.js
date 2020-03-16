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