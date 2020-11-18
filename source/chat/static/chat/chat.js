const socket = new WebSocket('ws://' + window.location.host + "/ws/chat");
let chats = {};
let currentChat;
let chatUID; // User ID
// let chatUsers = {};

socket.onmessage = function (e) {
    const msg = JSON.parse(e.data);
    switch (msg.type) {
        case 'message':
            if (!msg.room in chats) {
                console.log("Received a message for an unknown room.");
                return;
            }
            const $widget = (chats[msg.room].widget);
            const $chatLog = $widget.find("chat-log");
            messageToChatLog(msg, $chatLog)
            break;
        case 'status':
            break;
        case 'log':
            break;
    }
};

socket.onclose = function (e) {
    console.error('Chat socket closed.');
};

function openChat(chat) {
    const afterInstantiated = () => {
        if (!chat.joined) {
            socket.send(JSON.stringify([{
                'type': "join",
                'room': chat.meta.id
            }]));
            chat.joined = true;
            return;
        }
        if (currentChat != null) {
            currentChat.listing.removeClass('set');
            currentChat.widget.css('display', 'none');
        }
        chat.listing.addClass("set");
        chat.widget.css('display', 'grid');
        currentChat = chat;
    }
    if (chat.widget === undefined) {
        instantiateChatWidget(chat, true, afterInstantiated);
    } else {
        afterInstantiated.apply();
    }
}

// Loads the chats that the user has been enrolled to
function loadChats() {
    fetch("/api/chat/presence", {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders(),
    }).then(function (response) {
        return response.json();
    }).then(function (presence) {
        $('#chat-list .spinner').remove();
        for (let entry of presence) {
            const chat = {'meta': entry};
            chats[entry.id] = chat;
            listChat(chat);
        }
    });
}

// Lists a new chat in the chat list
function listChat(chat) {
    const meta = chat.meta;
    const $chatList = $('#chat-list');
    const $existing = $chatList.find(`.room[data-id=${meta.id}]`);
    if ($existing.length !== 0)
        return;
    const $listing = $(
        '<div class="chat-conversation">' +
        '<img class="chat-thumb" src="">' +
        '<div><span class="chat-title"></span><span class="chat-description"></span></div>' +
        '</div>');
    const $thumb = $listing.find(".chat-thumb");
    const $title = $listing.find(".chat-title");
    const $desc = $listing.find(".chat-description");
    const usrCnt = meta.users.length;
    switch (meta.type) {
        case 'dm':
            let otherUser = meta.users[0].id === chatUID ? meta.users[1] : meta.users[0];
            $thumb.attr("src", otherUser.thumbnail);
            $title.text(otherUser.name);
            $desc.text(otherUser.nickname);
            break
        case 'room':
            $thumb.attr("src", meta.thumbnail);
            $title.text(meta.name);
            $desc.append(meta.users.length + (usrCnt > 1 ? " utilizadores." : " utilizador."));
            break
    }

    // $listing.find(".chat-description").text(meta.description);
    $chatList.prepend($listing);
    $listing.data('id', meta.id);
    $listing.click(() => openChat(chat));
    chat.listing = $listing
}

// Creates a new chat widget
function instantiateChatWidget(chat, focus = false, afterInstantiated) {
    const $chatBox = $(
        '<div class="chatbox">' +
        '<div class="chat-log"></div>' +
        '<input class="chat-message-input" type="text" style="min-width: 80px">' +
        '<input class="chat-message-submit" type="button" value="»">' +
        '</div>');
    const $chatLog = $chatBox.find('.chat-log');

    fetch(`/api/chat/${chat.meta.id}/history`, {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders(),
    }).then(function (response) {
        return response.json();
    }).then(function (history) {
        for (let msg of history)
            messageToChatLog(msg, $chatLog)
        const $text = $chatBox.find('.chat-message-input');
        const $btn = $chatBox.find('.chat-message-submit');
        if (focus) $text.focus();
        $text.keyup((e) => {
            if (e.keyCode === 13) $btn.click()
        });
        $btn.click(() => {
            const message = $text.val();
            if (message.trim() === '') return;
            socket.send(JSON.stringify([{
                'type': "send",
                'room': chat.meta.id,
                'message': message
            }]));
            $text.val('');
        });
        chat.widget = $chatBox;
        $('#chat-container').append($chatBox);
        if (afterInstantiated !== undefined)
            afterInstantiated.apply()
    });
}

// Opens the chat that was requested by the user in the selector
function selectChat(selector) {
    delChildren(selector);
    fetch(`/api/chat/${selector.value}/join`, {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders()
    }).then(function (response) {
        return response.json();
    }).then(function (chat) {
        listChat(chat);
        openChat(chat);
    });
}

// Appends a message to a chat log
function messageToChatLog(msg, $log) {
    const timestamp = Date.parse(msg.creation);
    const datetime = new Date(timestamp);
    const date = `${datetime.getFullYear()}/${datetime.getMonth() + 1}/${datetime.getDate()}`;
    const time = `${datetime.getHours()}:${(datetime.getMinutes() < 10 ? "0" : "") + datetime.getMinutes()}`;
    const $lastBlk = $log.children().last();
    // $log.find(`[data-id=${msg.id}]`).length
    let $block;
    if ($lastBlk.length && !($lastBlk.data("author") === msg.author.id && Number($lastBlk.data("timestamp")) + 600 > msg.timestamp)) {
        $block = $lastBlk;
    } else {
        $block = $(
            '<div class="message-block">' +
            '<div class="meta">' +
            '<img class="author-pic"/><a class="author-name"></a><span class="datetime"></span>' +
            '</div>' +
            '</div>');
        $block.find(".author-pic").attr("src", msg.author.thumbnail);
        let authorName = $block.find(".author-name");
        authorName.text(msg.author.nickname);
        if (msg.author.profile)
            authorName.attr("href", msg.author.profile);
        $block.find(".datetime").text(date);
        $log.append($block);
    }
    let $msg = $('<div class="message"><span class="time"></span><span class="content"></span></div>');
    $msg.find(".time").text(time);
    $msg.find(".content").text(msg.content);
    $block.append($msg);
}

$(document).ready(function () {
    chatUID = JSON.parse(document.getElementById('chat-uid').textContent);
});