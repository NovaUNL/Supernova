const sources = {
    'T': {'events': [], color: "#a3be8caa"},
    'P': {'events': [], color: "#bf616aaa"},
    'TP': {'events': [], color: "#d08770aa"},
    'CE': {'events': [], color: "#8fbcbbaa"},
    'G': {'events': [], color: "#b48eadaa"},
    'U': {'events': [], color: "#5e81acaa"},
};

function loadCalendar(nickname) {
    let calendarEl = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        slotMinTime: "07:00:00",
        slotMaxTime: "24:00:00",
        footerToolbar: {
            start: 'title',
            center: '',
            end: 'today prev,next'
        },
        headerToolbar: false,
        nowIndicator: true,
        dayMinWidth: 150,
        contentHeight: 'auto',
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        locale: 'pt-br',
    });
    calendar.render();
    fetch(`/api/user/${nickname}/calendar`, {credentials: 'include'})
        .then((r) => {
            return r.json();
        })
        .then((entries) => {
            entries.forEach(e => addToCalendarSources(sources, e));
            Object.entries(sources).forEach(es => calendar.addEventSource(es[1]));
            calendar.render();
        })
}

function loadGroupCalendar(group) {
    let calendarEl = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'listMonth',
        slotMinTime: "08:00:00",
        slotMaxTime: "24:00:00",
        headerToolbar: {
            start: 'dayGridMonth,listMonth',
            center: 'title',
            end: 'today prev,next'
        },
        contentHeight: 'auto',
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        locale: 'pt-br',
    });
    calendar.render();
    fetch(`/api/group/${group}/calendar`, {credentials: 'include'})
        .then((r) => {
            return r.json();
        })
        .then((entries) => {
            entries.forEach(e => addToCalendarSources(sources, e));
            Object.entries(sources).forEach(es => calendar.addEventSource(es[1]));
            calendar.render();
        })
}

function loadSchedule(nickname, tiny) {
    let calendarEl = document.getElementById('schedule');
    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        slotMinTime: "08:00:00",
        slotMaxTime: "20:00:00",
        allDaySlot: !tiny,
        dayHeaderFormat: {
            weekday: 'short'
        },
        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            omitZeroMinute: true,
            meridiem: false
        },
        weekends: false,
        headerToolbar: false,
        nowIndicator: true,
        dayMinWidth: tiny ? 0 : 150,
        contentHeight: 'auto',
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        locale: 'pt-br'
    });
    calendar.render();
    fetch(`/api/user/${nickname}/schedule`, {credentials: 'include'})
        .then((r) => {
            return r.json();
        })
        .then((entries) => {
            entries.forEach(e => addToCalendarSources(sources, e));
            Object.entries(sources).forEach(es => calendar.addEventSource(es[1]));
            calendar.render();
        })
}

function loadOccupation(building_id) {
    let calendar = new FullCalendar.Calendar($('#occupation-table')[0], {
        timeZone: 'UTC',
        initialView: 'resourceTimelineDay',
        slotMinTime: "08:00:00",
        slotMaxTime: "20:00:00",
        resourceOrder: 'floor,door_number,type,title',
        nowIndicator: true,
        contentHeight: 'auto',
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        locale: 'pt-br',
        resourceAreaHeaderContent: 'Espaços',
        resourceAreaWidth: 120,
        resources: `/api/building/${building_id}/rooms`,
        events: `/api/building/${building_id}/schedule`,
        resourceLabelDidMount: (info) => {
          $(info.el).find('.fc-datagrid-cell-main').text(null)
              .append($(`<a href="${info.resource.extendedProps.url}">${info.resource.title}</a>`));
        }
    });
    calendar.render();
}

function addToCalendarSources(sources, entry) {
    let e = {'title': entry.title};
    if (entry.url) e.url = entry.url;
    if ('weekday' in entry) { // Periodic events
        e.daysOfWeek = [(entry.weekday + 8) % 7];
        e.startTime = entry.time;
        e.endTime = new Date(`1970-01-01 ${entry.time}`).addMinutes(entry.duration).toTimeString();
    } else { // "Once" events
        e.start = entry.datetime;
        e.end = new Date(new Date(entry.datetime).addMinutes(entry.duration));
    }
    if (entry.type in sources) sources[entry.type].events.push(e);
}

function addMinutesToTime(time, minutes) {
    return new Date(`1970-01-01 ${time}`).addMinutes(minutes).toTimeString();
}