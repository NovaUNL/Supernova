from college import models as college
from college.choice_types import RoomType


def build_schedule(shift_instances: [college.ShiftInstance]):
    week = [[], [], [], [], []]  # Monday-Friday turn instances
    unsortable = []  # Instances without schedule information
    end = 8 * 60  # Last turn added, to crop the end of the schedule. Starts as 8AM when there are no shifts
    for shift_instance in shift_instances:  # Fetch every turn of this class instance
        if hasattr(shift_instance, 'weekday') and shift_instance.weekday is not None \
                and hasattr(shift_instance, 'start') and shift_instance.start is not None \
                and hasattr(shift_instance, 'duration'):
            week[shift_instance.weekday].append(shift_instance)
            end = max(end, shift_instance.start + shift_instance.duration)
        else:  # Otherwise it's an unsortable turn instance
            unsortable.append(shift_instance)

    for day_index, day in enumerate(week):  # Sort days in chronological order
        week[day_index] = sorted(day, key=(lambda shift_instance: shift_instance.start))

    # Outer to inner dimension: Week, day, column, row. Formatted means it displays properly, without intersection.
    formatted_week = [[[]], [[]], [[]], [[]], [[]]]

    # Sort turn instances into columns without intersection between elements
    for f_day, day in zip(formatted_week, week):
        for shift_instance in day:
            allocated = False  # Whether this turn was successfully allocated in one column
            for column in f_day:  # Iterate through existing columns
                has_space = True  # Whether this column had space to allocate the turn
                for allocated_turn in column:  # For every turn already in the column
                    allocated_turn: college.ShiftInstance = allocated_turn
                    shift_instance: college.ShiftInstance = shift_instance
                    # If one of them intersect this one, then this column is no good, skip it
                    # TODO check only against the last added turn, if one intersects, that would be the one
                    if shift_instance.intersects(allocated_turn):
                        has_space = False
                        break
                if has_space:
                    column.append(shift_instance)
                    allocated = True
                    break
                else:
                    continue
            if not allocated:  # New column needed
                f_day.append([shift_instance])  # Append a new column to this day with the element already on it

    schedule = [[], [], [], [], []]
    for day, schedule_day in zip(formatted_week, schedule):
        for column in day:  # For every day in the column based week
            schedule_column = []
            last_addition = 8 * 60  # 8 AM
            for event in column:  # For every element in that column
                margin = event.start - last_addition  # Minutes from the last element
                gaps = margin // 30  # Every thirty minutes there's one gap
                [schedule_column.append(None) for _ in range(gaps)]  # Fill empty gaps
                schedule_column.append({'shift': event, 'rowspan': event.duration // 30,
                                        'start': event.minutes_to_str(event.start)})
                # Well, I kinda lost myself when I came back to comment. This would be margin + event duration
                last_addition += margin + 30  # But works with 30 minutes and doesn't with the event duration ¯\_(ツ )_/¯
            for _ in range((20 * 60 - last_addition) // 30):  # Fill with None events till 8 PM
                # TODO fill with None events only till the 'end' to save some pointless None array additions
                schedule_column.append(None)
            schedule_day.append(schedule_column)

    weekday_colspans = list(map(lambda day: len(day), schedule))  # Calculate the width of every weekday
    rows = []  # The schedule will be broken in rows. HTML doesn't like column-based tables
    # A rowspan makes the next row element shift right.
    skips = {}  # Signal those shifts in order not to add (None) elements that would get shifted
    [rows.append([]) for _ in range(12 * 60 // 30)]  # 30 minute spaces in 12 hours from 8AM to 8PM
    for row_index, row in enumerate(rows):
        column_offset = 0  # Tuesday isn't the first column. Store the previous days offset to have the correct column
        for day_index, day in enumerate(schedule):  # Run through the days once for every row
            for column_index, column in enumerate(day):
                column_index = column_index + column_offset  # Consider the shift that the previous days do to the cols
                if column_index in skips:  # If this column has an above element with >1 rowspan
                    skips[column_index] -= 1  # Decrement the remaining number of spans
                    if skips[column_index] == 0:
                        del skips[column_index]
                    continue  # And skip adding the corresponding event

                event = column[row_index]
                row.append(event)
                if event and event['rowspan'] > 1:  # If the event is not a None and has a >1 rowspan
                    skips[column_index] = event['rowspan'] - 1  # Tag it in the skips, for the next column to be skipped
            column_offset += weekday_colspans[day_index]  # Add this day to the offsets

    empty_rows_start = 0
    for row in rows[:]:  # For every row which only has None elements
        empty = True
        for column in row:
            if column is not None:
                empty = False
                break
        if empty:
            empty_rows_start += 1
        else:
            break

    empty_rows_end = (20 * 60 - end) // 30  # Rows to ignore at the end when adding to the result. Read last TODO

    initial_time = 8 * 6 + empty_rows_start * 3  # Initial schedule time (in tens of minutes)
    result = []
    # For every relevant row (ignore empty rows at the start/end)
    for row in rows[empty_rows_start:(-empty_rows_end if empty_rows_end > 0 else None)]:
        # TODO take that HTML out of here. Does not belong here
        result.append((f'{initial_time // 6}:{initial_time % 6}0 '
                       f'<span class="end-time">{(initial_time + 3) // 6}:{(initial_time + 3) % 6}0</span>', row))
        initial_time += 3
    return weekday_colspans, result, unsortable


def build_shifts_schedule(shifts: [college.Shift]):
    shift_instances = [shift_instance
                      for shift in shifts
                      for shift_instance in shift.instances.exclude(disappeared=True).all()]
    return build_schedule(shift_instances)


def build_occupation_table(period, year, weekday):
    # {building: {room: [time slot occupation]}}
    start_time = 8 * 60  # Start at 08:00
    end_time = 20 * 60  # End at 20:00
    slots = (end_time - start_time) // 30
    building_room_timeslots = dict()
    shift_instances = college.ShiftInstance.objects \
        .select_related('room', 'room__building') \
        .order_by('room__building', 'room', 'start') \
        .filter(weekday=weekday,
                start__lt=end_time,
                shift__class_instance__period=period,
                shift__class_instance__year=year) \
        .exclude(room=None).all()

    current_room = None
    room_slots = None
    for shift_instance in shift_instances:
        if shift_instance.room != current_room:
            if current_room is None or shift_instance.room.building != current_room.building:
                building_dict = dict()
                building_room_timeslots[shift_instance.room.building] = building_dict
            else:
                building_dict = building_room_timeslots[current_room.building]

            current_room = shift_instance.room
            empty_state = False if current_room == RoomType.CLASSROOM or current_room.unlocked else None
            room_slots = slots * [empty_state]
            building_dict[current_room] = room_slots

        # Fill the corresponding slots for this turn instance
        if shift_instance.start < start_time:
            if shift_instance.start + shift_instance.duration > start_time:
                busy_slots = (shift_instance.start - start_time + shift_instance.duration) // 30
                room_slots[:busy_slots] = busy_slots * [True]
            else:
                continue
        else:
            start_slot = (shift_instance.start - start_time) // 30
            if shift_instance.start + shift_instance.duration > end_time:
                relevant_duration = end_time - shift_instance.start
            else:
                relevant_duration = shift_instance.duration
            busy_slots = relevant_duration // 30
            room_slots[start_slot:start_slot + busy_slots] = busy_slots * [True]

    # Fetch remaining rooms (without classes associated)
    rooms = college.Room.objects \
        .select_related('building') \
        .order_by('building') \
        .exclude(extinguished=True).all()
    for room in rooms:
        empty_state = False if room == RoomType.CLASSROOM or room.unlocked else None
        if room.building in building_room_timeslots:
            building_dict = building_room_timeslots[room.building]
            if room in building_dict:
                continue
            building_dict[room] = slots * [empty_state]
        else:
            building_room_timeslots[room.building] = {room: slots * [empty_state]}
    return building_room_timeslots


def build_building_occupation_table(period, year, weekday, building):
    start_time = 8 * 60  # Start at 08:00
    end_time = 20 * 60  # End at 20:00
    slots = (end_time - start_time) // 30
    room_timeslots = dict()
    shift_instances = college.ShiftInstance.objects \
        .select_related('room', 'room__building') \
        .order_by('room', 'start') \
        .filter(weekday=weekday,
                start__lt=end_time,
                shift__class_instance__period=period,
                shift__class_instance__year=year,
                room__building=building) \
        .exclude(room=None).all()

    current_room = None
    room_slots = None
    for shift_instance in shift_instances:
        if shift_instance.room != current_room:
            current_room = shift_instance.room
            empty_state = False if current_room == RoomType.CLASSROOM or current_room.unlocked else None
            room_slots = slots * [empty_state]
            room_timeslots[current_room] = room_slots

        # Fill the corresponding slots for this turn instance
        if shift_instance.start < start_time:
            if shift_instance.start + shift_instance.duration > start_time:
                busy_slots = (shift_instance.start - start_time + shift_instance.duration) // 30
                room_slots[:busy_slots] = busy_slots * [True]
            else:
                continue
        else:
            start_slot = (shift_instance.start - start_time) // 30
            if shift_instance.start + shift_instance.duration > end_time:
                relevant_duration = end_time - shift_instance.start
            else:
                relevant_duration = shift_instance.duration
            busy_slots = relevant_duration // 30
            room_slots[start_slot:start_slot + busy_slots] = busy_slots * [True]

    # # Fetch remaining rooms (without classes associated)
    # rooms = college.Room.objects \
    #     .select_related('building') \
    #     .filter(building=building) \
    #     .exclude(extinguished=True).all()
    # for room in rooms:
    #     empty_state = False if room == RoomType.CLASSROOM or room.unlocked else None
    #     if room in room_timeslots:
    #         continue
    #     room_timeslots[room] = slots * [empty_state]
    return room_timeslots
