function initChats() {
    for (const chat of document.querySelectorAll('.chatbox'))
        initChat(chat)
}

function initChat(elem, focus = false) {
    const endpoint = elem.dataset.endpoint;
    const chatLog = elem.querySelector('.chat-log');
    const textInput = elem.querySelector('.chat-message-input');
    const btn = elem.querySelector('.chat-message-submit');
    const socket = new WebSocket('ws://' + window.location.host + endpoint);

    if (focus) textInput.focus();

    textInput.onkeyup = function (e) {
        if (e.keyCode === 13) {  // enter, return
            btn.click();
        }
    };

    btn.onclick = function (e) {
        const message = textInput.value;
        if (message.trim() === '') return;
        socket.send(JSON.stringify({
            'message': message,
            'testerinoo': "fooo"
        }));
        textInput.value = '';
    };

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const lastBlock = chatLog.lastChild;
        let block;
        if (lastBlock && !(Number(lastBlock.dataset.timestamp) + 600 > data.timestamp && lastBlock.dataset.author === data.author.id)) {
            block = lastBlock;
        } else {
            block = document.createElement('div');
            block.className = 'message-block';
            let meta = document.createElement('div');
            meta.className = 'meta';
            let img = document.createElement('img');
            img.className = 'author-pic';
            img.src = data.message.author.pic;
            let author;
            if (data.message.author.url) {
                author = document.createElement('a');
                author.href = data.message.author.url;
            } else {
                author = document.createElement('span');
            }
            author.className = 'author-name';
            author.innerText = data.message.author.nickname;
            let datetime = document.createElement('span');
            datetime.className = 'datetime';
            datetime.innerText = data.message.datetime;
            meta.appendChild(img);
            meta.appendChild(author);
            meta.appendChild(datetime);
            block.appendChild(meta);
            block.dataset.author = data.message.author.id;
            block.dataset.timestamp = data.message.timestamp;
            chatLog.appendChild(block);
        }
        let msg = document.createElement('div');
        msg.className = 'message';
        let msgTime = document.createElement('span');
        msgTime.className = 'time';
        msgTime.innerText = data.message.datetime.split(" ")[1];
        let content = document.createElement('span');
        content.className = 'content';
        content.innerText = data.message.content;
        msg.appendChild(msgTime);
        msg.appendChild(content);
        block.appendChild(msg);
    };

    socket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };
}