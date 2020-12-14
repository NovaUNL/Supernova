const socket = new WebSocket('ws://' + window.location.host + "/ws/chat");
let chats = {};
let currentChat;
const msgBlockTimestampThreshold = 600000; // 10 minutes
const defaultUserPic = '/static/img/user.svg';

socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    switch (data.type) {
        case 'message':
            const msg = data.message;
            if (!data.conversation in chats) {
                console.log("Received a message for an unknown room.");
                return;
            }
            const chat = chats[msg.conversation];
            if (chat !== currentChat)
                addNotification(chat);
            if (chat.loaded)
                messageToChat(msg, chat.log, chat.scroll);
            break;
        case 'status':
            break;
        case 'log':
            break;
    }
};

socket.onclose = (e) => {
    console.error('Chat socket closed.');
};

function openChat(chat) {
    if (chat.widget === undefined) {
        const $chatBox = chat.widget = $(
            '<div class="chatbox">' +
            '<div class="chat-log"></div>' +
            '<input class="chat-message-input" type="text" style="min-width: 80px">' +
            '<input class="chat-message-submit" type="button" value="»">' +
            '</div>');
        const $log = chat.log = $chatBox.find('.chat-log');
        $log.append(spinner.clone());

        const $text = $chatBox.find('.chat-message-input');
        const $btn = $chatBox.find('.chat-message-submit');
        if (focus)
            $text.focus();
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
        $log.scroll(() => {
            chat.scroll = $log.prop('scrollHeight') - $log.height() - $log.scrollTop() === 0;
            if (chat.loaded && $log.scrollTop() === 0 && !chat.loadingMore) {
                chat.loadingMore = true;
                $log.find('.spinner').remove();
                let loadSpinner = spinner.clone();
                $log.prepend(loadSpinner);
                fetch(`/api/chat/${chat.meta.id}/history?to=${chat.minMsgID}`, {
                    method: 'GET',
                    credentials: 'include',
                    headers: defaultRequestHeaders(),
                }).then((response) => {
                    return response.json();
                }).then((history) => {
                    const firstMsg = chat.log[0].querySelector(".message");
                    loadSpinner.remove();
                    for (let msg of history) {
                        if (!chat.minMsgID || chat.minMsgID > msg.id)
                            chat.minMsgID = msg.id;
                        messageToChat(msg, chat.log)
                    }
                    if (firstMsg)
                        firstMsg.parentNode.scrollIntoView(true)
                    chat.loadingMore = false;
                })
            }
        });
    }

    if (currentChat != null) {
        currentChat.listing.removeClass('set');
        currentChat.widget.css('display', 'none');
    }
    currentChat = chat;
    if (chat.listing) {
        chat.listing.addClass("set");
        window.location.hash = chat.meta.id;
    }
    chat.widget.css('display', 'grid');

    if (!chat.loaded) {
        fetch(`/api/chat/${chat.meta.id}/history`, {
            method: 'GET',
            credentials: 'include',
            headers: defaultRequestHeaders(),
        }).then((response) => {
            return response.json();
        }).then((history) => {
            if (chat.loaded) return; // Double load
            for (let msg of history) {
                if (!chat.minMsgID || chat.minMsgID > msg.id)
                    chat.minMsgID = msg.id;
                messageToChat(msg, chat.log, chat.scroll);
            }
            scrollChat(chat);
            chat.widget.find('.spinner').remove();
            chat.loaded = true;
        });
    }
}

// Loads the chats that the user has been enrolled to
function loadChat(id) {
    fetch(`/api/chat/${id}/info`, {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders(),
    }).then((response) => {
        return response.json();
    }).then((meta) => {
        socket.send(JSON.stringify([{
            'type': 'join',
            'conversation': id
        }]));
        $('#chat-list .spinner').remove();
        const chat = {'meta': meta};
        chats[meta.id] = chat;
        openChat(chat);
    });
}

// Loads the chats that the user has been enrolled to
function loadChats() {
    fetch("/api/chat/presence", {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders(),
    }).then((response) => {
        return response.json();
    }).then((presence) => {
        $('#chat-list .spinner').remove();
        for (let entry of presence) {
            const chat = {'meta': entry};
            chats[entry.id] = chat;
            listChat(chat);
        }
        socket.send(JSON.stringify([{
            'type': 'join',
            'conversation': '__all__'
        }]));
        let conversations = $('#chat-list .chat-conversation');
        conversations.sort((a, b) => {
            return $(b).data('lastActivity') - $(a).data('lastActivity');
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
    const $listing = chat.listing = $(
        '<div class="chat-conversation">' +
        '<img class="chat-thumb" src="">' +
        '<div><span class="chat-title"></span><span class="chat-description"></span></div>' +
        '<span class="chat-notif"></span>' +
        '</div>');
    const $thumb = $listing.find(".chat-thumb");
    const $title = $listing.find(".chat-title");
    const $desc = $listing.find(".chat-description");
    const usrCnt = meta.users.length;
    switch (meta.type) {
        case 'dm':
            let otherUser = meta.users[0].id === UID ? meta.users[1] : meta.users[0];
            $thumb.attr("src", otherUser.thumbnail ? otherUser.thumbnail : defaultUserPic);
            $title.text(otherUser.name);
            $desc.text(otherUser.nickname);
            break
        case 'room':
            $thumb.attr("src", meta.thumbnail ? meta.thumbnail : defaultUserPic); //TODO Substitute with group pic
            $title.text(meta.name);
            $desc.append(meta.users.length + (usrCnt > 1 ? " utilizadores." : " utilizador."));
            break
    }

    $chatList.prepend($listing);
    $listing.data('id', meta.id);
    $listing.data('lastActivity', Date.parse(meta.lastActivity == null ? meta.creation : meta.lastActivity));
    $listing.click(() => {
        openChat(chat);
        $listing.find(".chat-notif").removeClass('set');
    })
}

// Opens the chat that was requested by the user in the selector
function selectChat(selector) {
    const conversationID = selector.value;
    delChildren(selector);
    fetch(`/api/chat/${conversationID}/join`, {
        method: 'GET',
        credentials: 'include',
        headers: defaultRequestHeaders()
    }).then((response) => {
        return response.json();
    }).then((chatInfo) => {
        const chat = {'meta': chatInfo, 'scroll': true};
        chats[chatInfo.id] = chat;
        listChat(chat);
        openChat(chat);
    });
}

// Appends a message to a chat log
function messageToChat(msg, $log, scroll = false) {
    const timestamp = Date.parse(msg.creation);
    const datetime = new Date(timestamp);
    const now = new Date(Date.now());
    const time = `${datetime.getHours()}:${(datetime.getMinutes() < 10 ? "0" : "") + datetime.getMinutes()}`;
    let date;
    if (now.getDate() === datetime.getDate())
        date = `Hoje ás ${time}`
    else if (now.getDate() === datetime.getDate() - 1)
        date = `Ontem ás ${time}`
    else
        date = `${datetime.getFullYear()}/${datetime.getMonth() + 1}/${datetime.getDate()} ${time}`;
    const authorID = msg.author.id;

    const [pred, succ] = findNearestMessages($log, timestamp);

    let $block = null;
    if (pred) {
        const $parent = $(pred.parentNode); // Message block
        const pTS = Number($parent.data("timestamp"));
        const pDate = new Date(pTS);
        if ($parent.data("author") === authorID && pTS > timestamp - msgBlockTimestampThreshold && pDate.getDay() === datetime.getDay()) {
            $block = $parent;
        }
    }

    if (!$block && succ) {
        const $parent = $(succ.parentNode); // Message block
        const pTS = Number($parent.data("timestamp"));
        const pDate = new Date(pTS);
        if ($parent.data("author") === authorID && pTS < timestamp + msgBlockTimestampThreshold && pDate.getDay() === datetime.getDay()) {
            $parent.data("timestamp", timestamp); // Update block timestamp to the current message timestamp
            $block = $parent;
        }
    }

    if (!$block) {
        $block = $(
            '<div class="message-block">' +
            '<div class="meta">' +
            '<img alt="autor" class="author-pic"/><a class="author-name"></a><span class="datetime"></span>' +
            '</div>' +
            '</div>');
        $block.find(".author-pic").attr("src", msg.author.thumbnail ? msg.author.thumbnail : defaultUserPic)
        let authorName = $block.find(".author-name");
        authorName.text(msg.author.nickname);
        if (msg.author.profile)
            authorName.attr("href", msg.author.profile);
        $block.find(".datetime").text(date);
        $block.data('timestamp', timestamp);
        $block.data('author', authorID);
        $log.append($block);
        $log.find(".message-block").sort((a, b) => {
            return $(a).data("timestamp") - $(b).data("timestamp");
        }).appendTo($log);
    }

    let $msg = $('<div class="message"><span class="time"></span><span class="content"></span></div>');
    $msg.find(".time").text(time);
    $msg.find(".content").text(msg.content);
    $msg.data("timestamp", timestamp);
    $block.append($msg);

    $block.find(".message")
        .sort((a, b) => {
            return $(a).data("timestamp") - $(b).data("timestamp");
        })
        .appendTo($block);
    if (scroll)
        $log.animate({scrollTop: $log.prop('scrollHeight')})
}

function scrollChat(chat) {
    chat.log.animate({scrollTop: chat.log.prop('scrollHeight')});
}

function addNotification(chat) {
    if (!chat.listing) return;
    chat.listing.find(".chat-notif").addClass('set');
    chat.listing.parent().prepend(chat.listing)
}

function findNearestMessages($log, timestamp) {
    const msgs = $log.find(".message");

    let start = 0, end = msgs.length - 1;
    let prev = null, succ = null;
    while (start <= end) {
        const mi = Math.floor((start + end) / 2);
        const m = msgs[mi];
        const mTS = $(m).data("timestamp");
        if (mTS <= timestamp) {
            prev = m;
            start = mi + 1;
        } else {
            succ = m;
            end = mi - 1;
        }
    }
    // Nearest lower and nearest higher
    return [prev, succ];
}