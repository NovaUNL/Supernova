function loadExternalPageSettings(endpoint) {
    /**
     * Fetches the list of external pages an populates the corresponding widget
     */
    const list = $("#external-page-list");
    const input = $("#external-url-input");
    $("#external-url-submit").click(() => {
        const val = input.val().trim();
        input.val("");
        if (val === "") return; // TODO warn user

        fetch(endpoint, {
            method: 'PUT',
            body: JSON.stringify({'url': val}),
            headers: defaultRequestHeaders(),
            credentials: 'include'
        })
            .catch(() => alert("Erro"))
            .then(r => r.json())
            .catch(error => console.error('Error:', error))
            .then(info => appendExternalPage(list, info, endpoint));
    })
    fetch(endpoint, {credentials: 'include'})
        .then(r => r.json())
        .then((pages) => {
            pages.forEach((p) => appendExternalPage(list, p, endpoint));
        });
}

function appendExternalPage(list, info, endpoint) {
    /**
     * Appends an external page object to the page list
     */
    const row = $('<li><a class="page"></a> (<a class="remove-link" href="javascript:void(0);">Remover</a>)</li>');
    const page = row.find('.page');
    if ('name' in info && info.name)
        page.text(info.name)
    else if ('platform' in info && info.platform)
        page.text(info.platform)
    else
        page.text(info.url)

    page.attr('href', info.url);
    page.el = row;
    list.append(row);

    row.find('.remove-link').click(() => {
        fetch(endpoint, {
            method: 'DELETE',
            body: JSON.stringify({'id': info.id}),
            headers: defaultRequestHeaders(),
            credentials: 'include',
        }).catch(error => console.error('Error:', error))
            .then(() => row.remove());
    });
}