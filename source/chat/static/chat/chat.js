const socket = new WebSocket('ws://' + window.location.host + "/ws/chat");
let chats = {};
let currentChat;
let chatUID; // User ID
let startingChat = false;
let warnedHistoryLoadingIncomplete = false;
const msgBlockTimestampThreshold = 600000;
const defaultUserPic = '/static/img/user.svg';

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
        if (chat.scroll)
            $chatLog.animate({scrollTop: $chatLog.prop('scrollHeight')})
        $chatLog.scroll(() => {
            chat.scroll = $chatLog.prop('scrollHeight') - $chatLog.height() - $chatLog.scrollTop() === 0;
            if (!chat.scroll && $chatLog.scrollTop() < 10 && !warnedHistoryLoadingIncomplete) {
                // TODO
                alert("O carregamento do histórico ainda não foi implementado.");
                warnedHistoryLoadingIncomplete = true;
            }
        });
        if (afterInstantiated !== undefined)
            afterInstantiated.apply()
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
        const chat = {'meta': chatInfo, 'scroll': true};
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
            '<img class="author-pic"/><a class="author-name"></a><span class="datetime"></span>' +
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
        $log.find(".message-block").sort(function (a, b) {
            return $(a).data("timestamp") > $(b).data("timestamp");
        }).appendTo($log);
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
        $log.animate({scrollTop: $log.prop('scrollHeight')})
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

window.addEventListener("load", () => {
    chatUID = JSON.parse($('#chat-uid')[0].textContent);
    loadChats();
});