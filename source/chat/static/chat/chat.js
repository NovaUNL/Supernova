const socket = new WebSocket('ws://' + window.location.host + "/ws/chat");
let chats = {};
let currentChat;
let chatUID; // User ID
let startingChat = false;
let warnedHistoryLoadingIncomplete = false;

socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    switch (data.type) {
        case 'message':
            const msg = data.message;
            if (!data.conversation in chats) {
                console.log("Received a message for an unknown room.");
                return;
            }
            const chat = chats[msg.conversation];
            messageToChat(msg, chat)
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
                'type': 'join',
                'conversation': chat.meta.id
            }]));
            chat.joined = true;
        }
        if (currentChat != null) {
            currentChat.listing.removeClass('set');
            currentChat.widget.css('display', 'none');
        }
        currentChat = chat;
        chat.listing.addClass("set");
        chat.widget.css('display', 'grid');
        window.location.hash = chat.meta.id;
    }
    if (chat.widget === undefined) {
        if (!startingChat) {
            startingChat = true;
            instantiateChatWidget(chat, true, afterInstantiated);
        }
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
        let conversations = $('#chat-list .chat-conversation');
        conversations.sort(function (a, b) {
            return a.dataset.lastActivity < b.dataset.lastActivity;
        }).appendTo('#chat-list');

        const anchor = window.location.hash.substr(1);
        if (anchor !== '')
            $(`#chat-list .chat-conversation[data-id=${anchor}]`).click()
        if (currentChat == null)
            conversations.first().click()
    });
}

// Lists a new chat in the chat list
function listChat(chat) {
    const meta = chat.meta;
    const $chatList = $('#chat-list');
    const $existing = $chatList.find(`.chat-conversation[data-id=${meta.id}]`);
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
            $thumb.attr("src", otherUser.thumbnail ? otherUser.thumbnail : '/static/img/user.svg');
            $title.text(otherUser.name);
            $desc.text(otherUser.nickname);
            break
        case 'room':
            $thumb.attr("src", meta.thumbnail ? meta.thumbnail : '/static/img/user.svg'); //TODO Substitute by group pic
            $title.text(meta.name);
            $desc.append(meta.users.length + (usrCnt > 1 ? " utilizadores." : " utilizador."));
            break
    }

    // $listing.find(".chat-description").text(meta.description);
    $chatList.prepend($listing);
    $listing[0].dataset.id = meta.id;
    $listing[0].dataset.lastActivity = meta.lastActivity == null ? meta.creation : meta.lastActivity;
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
        chat.widget = $chatBox;
        for (let msg of history)
            messageToChat(msg, chat)
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
                'type': 'send',
                'conversation': chat.meta.id,
                'message': message
            }]));
            $text.val('');
        });
        $('#chat-container').append($chatBox);
        startingChat = false;
        if (afterInstantiated !== undefined)
            afterInstantiated.apply()
    });

    if (chat.scroll)
        $chatLog.animate({ scrollTop: $chatLog.prop('scrollHeight')})

    $chatLog.scroll(() => {
        chat.scroll = $chatLog.prop('scrollHeight') - $chatLog.height() - $chatLog.scrollTop() === 0;
        if (!chat.scroll && $chatLog.scrollTop() < 10 && !warnedHistoryLoadingIncomplete) {
            // TODO
            alert("O carregamento do histórico ainda não foi implementado.");
            warnedHistoryLoadingIncomplete = true;
        }
    });
}

// Opens the chat that was requested by the user in the selector
function selectChat(selector) {
    const conversationID = selector.value;
    delChildren(selector);
    fetch(`/api/chat/${conversationID}/join`, {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders()
    }).then(function (response) {
        return response.json();
    }).then(function (chatInfo) {
        const chat = {'meta': chatInfo};
        chats[chatInfo.id] = chat;
        listChat(chat);
        openChat(chat);
    });
}

// Appends a message to a chat log
function messageToChat(msg, chat) {
    const $log = chat.widget.find(".chat-log");

    const timestamp = Date.parse(msg.creation);
    const datetime = new Date(timestamp);
    const date = `${datetime.getFullYear()}/${datetime.getMonth() + 1}/${datetime.getDate()}`;
    const time = `${datetime.getHours()}:${(datetime.getMinutes() < 10 ? "0" : "") + datetime.getMinutes()}`;
    const authorID = msg.author.id;

    const [pred, succ] = findNearestMessages($log, timestamp);
    let $block = null;
    if (pred) {
        const $parent = $(pred.parentNode);
        const pTS = Number($parent.data("timestamp"));
        const pDate = new Date(timestamp);
        if (!($parent.data("author") === authorID && pTS - 600 < timestamp && pDate.getDay() === datetime.getDay())) {
            $block = $parent;
        }
    }

    if (!$block && succ) {
        const $parent = $(succ.parentNode);
        const pTS = Number($parent.data("timestamp"));
        const pDate = new Date(timestamp);
        if (!($parent.data("author") === authorID && pTS + 600 < timestamp && pDate.getDay() === datetime.getDay())) {
            $parent.data("timestamp", timestamp); // Update block timestamp to the current message timestamp
            $block = $parent;
        }
    }

    if (!$block) {
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
        $block.data('timestamp', timestamp);
        $block.data('author', authorID);
        $log.append($block);
    }

    let $msg = $('<div class="message"><span class="time"></span><span class="content"></span></div>');
    $msg.find(".time").text(time);
    $msg.find(".content").text(msg.content);
    $msg.data("timestamp", timestamp);
    $block.append($msg);

    $block.find(".message").sort(function (a, b) {
        return $(a).data("timestamp") > $(b).data("timestamp");
    }).appendTo($block);
    if (chat.scroll)
        $log.animate({ scrollTop: $log.prop('scrollHeight')})
}

function findNearestMessages($log, timestamp) {
    const msgs = $log.find(".message");

    let start = 0, end = msgs.length - 1;
    if (start === end) {
        const m = msgs[0];
        if ($(m).data("timestamp") < timestamp)
            return [m, null]
        else
            return [null, m]
    }
    while (start <= end) {
        const mid = Math.floor((start + end) / 2);
        const m = msgs[mid];
        const mTS = $(m).data("timestamp");
        if (mTS === timestamp)
            return [m, msgs[mid + 1]]
        else if (mTS < timestamp)
            start = mid + 1
        else
            end = mid - 1
    }
    // Nearest lower and nearest higher
    return [msgs[start], msgs[start + 1]];
}

window.addEventListener("load", () => {
    chatUID = JSON.parse($('#chat-uid')[0].textContent);
    loadChats();
});