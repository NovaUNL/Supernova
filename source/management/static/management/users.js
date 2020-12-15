function suspend() {
    let suspendSelect = $("#suspension-selector")[0];
    let id = suspendSelect.value;
    let url = suspendSelect.parentNode.dataset.endpoint.replace("/0/", `/${id}/`);

    fetch(url, {
        method: 'POST',
        body: JSON.stringify({'action': 'suspend'}),
        headers: defaultRequestHeaders(),
        credentials: 'include',
    }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(() => location.reload());
}

function removeSuspension(element, user_id) {
    let url = element.closest('[data-endpoint]').dataset.endpoint.replace("/0/", `/${user_id}/`);

    fetch(url, {
        method: 'POST',
        body: JSON.stringify({'action': 'unsuspend'}),
        headers: defaultRequestHeaders(),
        credentials: 'include',
    }).then(res => res.json())
        .catch(() => alert('Error'))
        .then(() => location.reload());
}