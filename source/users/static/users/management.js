function suspend() {
    let suspendSelect = document.getElementById("suspension-selector");
    let id = suspendSelect.value;
    let url = suspendSelect.parentNode.dataset.endpoint.replace("/0/", `/${id}/`);

    fetch(url, {
        method: 'POST',
        body: JSON.stringify({'action': 'suspend'}),
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }),
        credentials: 'include',
    }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(() => {
            location.reload();
        });
}

function removeSuspension(element, user_id) {
    let url = element.closest('[data-endpoint]').dataset.endpoint.replace("/0/", `/${user_id}/`);

    fetch(url, {
        method: 'POST',
        body: JSON.stringify({'action': 'unsuspend'}),
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }),
        credentials: 'include',
    }).then(res => res.json())
        .catch(() => alert('Error'))
        .then(() => {
            location.reload();
        });
}