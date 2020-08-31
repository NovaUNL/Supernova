function addToCollection(list, section) {
    let row = document.createElement("li");
    row.classList.add("sortable-line");
    row.dataset.id = section.id;

    row.appendChild(document.createTextNode(section.title));
    let id = document.createElement("sup");
    id.appendChild(document.createTextNode(section.id));
    row.appendChild(id);

    let deleteElement = document.createElement("div");
    deleteElement.classList.add('list-line-delete');
    deleteElement.innerText = "X";
    row.appendChild(deleteElement);
    row.setAttribute('data-id', section.id);
    list.appendChild(row);

    deleteElement.addEventListener('click', function () {
        rmFromCollectionEvt(row);
    });
}

function addToCollectionEvt(selector) {
    let listElem = selector.parentNode.querySelector('ul');
    let url = listElem.dataset.endpoint;
    fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({"child": parseInt(selector.value)})
    }).then(function (response) {
        return response.json();
    }).then(function (section) {
        addToCollection(listElem, section)
    });
    delChildren(selector);
}

function rmFromCollectionEvt(line) {
    let parent = line.parentNode;
    let listElem = parent.querySelector('ul');
    let url = listElem.dataset.endpoint;
    parent.removeChild(line);

    fetch(url, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({"child": parseInt(selector.value)})
    }).then(function (response) {
    });
}

function populateCollection(element) {
    let listElem = element.parentNode.querySelector('ul');
    let url = listElem.dataset.endpoint;
    fetch(url, {
        credentials: 'include'
    }).then(function (response) {
        return response.json();
    }).then(function (sections) {
        for (let section of sections) {
            addToCollection(element, section);
        }
    });
}

function saveCollectionOrder(collection) {
    let result = [];
    let index = 0;
    for (let element of collection.querySelectorAll(":scope li[data-id]")) {
        result.push({
            id: parseInt(element.dataset.id),
            index: index
        });
        index++;
    }

    fetch(url, {
        method: 'PUT',
        body: JSON.stringify(result),
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }),
        credentials: 'include',
    }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(response => {
            console.log('Success:', response);
            location.reload();
        });
}