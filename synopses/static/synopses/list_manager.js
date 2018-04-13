function addElementToList(list, sectionID, sectionName, sectionIndex) {
    let line = document.createElement("div");
    line.classList.add("sortable-line");
    let index = document.createElement("span");
    index.classList.add('list-line-index');
    if (sectionIndex == null) {
        index.appendChild(document.createTextNode('N- '));
    } else {
        index.appendChild(document.createTextNode((sectionIndex + 1) + 'º '));
    }
    line.appendChild(index);
    line.appendChild(document.createTextNode(sectionName));
    let id = document.createElement("sup");
    id.appendChild(document.createTextNode(sectionID));
    line.appendChild(id);

    let deleteElement = document.createElement("div");
    deleteElement.classList.add('list-line-delete');
    let i = document.createElement("i");
    i.classList.add('fas', 'fa-times');
    deleteElement.appendChild(i);
    line.appendChild(deleteElement);
    line.setAttribute('data-id', sectionID);
    list.appendChild(line);

    deleteElement.addEventListener('click', function () {
        list.removeChild(line);
    });
}

function newItem(selector) {
    let id = selector.value;
    let name = selector.textContent;
    addElementToList(document.getElementById("sortable-list"), id, name, null);
    while (selector.firstChild) {
        selector.removeChild(selector.firstChild);
    }
}

function populate(element, url) {
    fetch(url, {
        credentials: 'include'
    }).then(function (response) {
        return response.json();
    }).then(function (topic) {
        let topicSections = topic.sections;
        for (let section of topicSections) {
            addElementToList(element, section.id, section.name, section.index);
        }
    });
}

function save(sorter, url) {
    let result = [];
    let index = 0;
    for (let element of sorter.toArray()) {
        result.push({
            id: parseInt(element),
            index: index
        });
        index++;
    }
    fetch(url, {
        method: 'PUT',
        body: JSON.stringify(result),
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': jQuery("[name=csrfmiddlewaretoken]").val()
        }),
        credentials: 'include',
    }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(response => {
            console.log('Success:', response);
            location.reload();
        });

}