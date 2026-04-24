from flask import Blueprint, request, jsonify
from peewee_manager import ScheduleEntry, TeachingClass, Room, Teacher, SchoolClass, Course, Holiday
from datetime import datetime
import logging

schedule_bp = Blueprint('schedule', __name__)
logger = logging.getLogger(__name__)


@schedule_bp.route('/schedule/run', methods=['POST'])
def run_schedule():
    data = request.get_json() or {}
    start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))

    try:
        from scheduler import MainScheduler, Course as SchedulerCourse

        scheduler = MainScheduler(start_date)

        rooms = list(Room.select().where(Room.is_available == True))
        
        # 中文教室类型到英文排课器类型的映射
        room_type_to_english = {
            '普通教室': 'normal',
            '多媒体教室': 'normal',
            '机房': 'computer',
            '实验室': 'lab',
        }
        
        for room in rooms:
            english_room_type = room_type_to_english.get(room.room_type, 'normal')
            scheduler.add_room(
                room_id=str(room.id), name=room.name,
                capacity=room.capacity, room_type=english_room_type,
            )

        holidays = list(Holiday.select())
        holiday_dict = {}
        for h in holidays:
            holiday_dict[h.date.strftime('%Y-%m-%d')] = {'name': h.name}
        scheduler.setup_holidays(holiday_dict)

        teaching_classes = list(TeachingClass.select())
        courses_to_schedule = []
        
        for tc in teaching_classes:
            course = tc.course
            cls = tc.school_class
            teacher = tc.teacher
            if course and cls and teacher:
                # 课程类型映射
                db_room_type = course.course_type if hasattr(course, 'course_type') else ''
                
                course_type_to_room = {
                    '普通授课': 'normal',
                    '上机': 'computer',
                    '实验': 'lab',
                }
                
                scheduler_room_type = course_type_to_room.get(db_room_type, 'normal')
                
                courses_to_schedule.append(SchedulerCourse(
                    course_id=str(tc.id),
                    name=f"{course.name}-{cls.name}",
                    teacher_id=str(tc.teacher_id),
                    class_id=str(tc.school_class_id),
                    required_hours=course.total_hours,
                    student_count=cls.student_count,
                    room_type=scheduler_room_type,
                ))

        result = scheduler.schedule_courses(courses_to_schedule)

        success_count = 0
        for slot_key, sessions in result.items():
            parts = slot_key.split('_')
            if len(parts) < 3:
                continue
            week = int(parts[0].replace('W', ''))
            day_str = parts[1].replace('D', '')
            day_map = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5}
            day = day_map.get(day_str, int(day_str) if day_str.isdigit() else 1)
            period = parts[2]

            for session in sessions:
                existing = ScheduleEntry.select().where(
                    (ScheduleEntry.teaching_class == int(session['course_id'])) &
                    (ScheduleEntry.week == week) &
                    (ScheduleEntry.day == day) &
                    (ScheduleEntry.period == period)
                ).first()
                if existing:
                    continue

                room = Room.get_or_none(Room.id == int(session['room_id']))
                tc = TeachingClass.get_or_none(TeachingClass.id == int(session['course_id']))
                if room and tc:
                    ScheduleEntry.create(
                        teaching_class=tc, week=week, day=day,
                        period=period, room=room, is_holiday=False,
                    )
                    success_count += 1

        log = scheduler.get_scheduling_log()
        return jsonify({
            'message': '排课完成',
            'success_count': success_count,
            'failed_count': len(scheduler.get_failed_courses()),
            'log': log,
        }), 200

    except Exception as e:
        logger.error(f'排课失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'排课失败: {str(e)}'}), 500


@schedule_bp.route('/schedule/results', methods=['GET'])
def get_schedule_results():
    class_id = request.args.get('class_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    room_id = request.args.get('room_id', type=int)
    week = request.args.get('week', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = ScheduleEntry.select()

    if class_id:
        tc_ids = [tc.id for tc in TeachingClass.select().where(TeachingClass.school_class == class_id)]
        query = query.where(ScheduleEntry.teaching_class.in_(tc_ids))
    if teacher_id:
        tc_ids = [tc.id for tc in TeachingClass.select().where(TeachingClass.teacher == teacher_id)]
        query = query.where(ScheduleEntry.teaching_class.in_(tc_ids))
    if room_id:
        query = query.where(ScheduleEntry.room == room_id)
    if week:
        query = query.where(ScheduleEntry.week == week)

    total = query.count()
    entries = list(query.order_by(ScheduleEntry.week, ScheduleEntry.day).limit(per_page).offset((page - 1) * per_page))

    results = []
    for entry in entries:
        tc = entry.teaching_class
        course = tc.course if tc else None
        cls = tc.school_class if tc else None
        teacher = tc.teacher if tc else None
        room = entry.room

        results.append({
            'id': entry.id,
            'teaching_class_id': tc.id if tc else None,
            'week': entry.week,
            'day': entry.day,
            'period': entry.period,
            'room_id': room.id if room else None,
            'is_holiday': entry.is_holiday,
            'course_name': course.name if course else None,
            'class_name': cls.name if cls else None,
            'teacher_name': teacher.name if teacher else None,
            'room_name': room.name if room else None,
            'created_at': entry.created_at.isoformat() if entry.created_at else None,
        })

    return jsonify({
        'results': results,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page,
    })


@schedule_bp.route('/schedule/weekly', methods=['GET'])
def get_weekly_schedule():
    """获取周课表视图数据 - 按星期+节次展示，自动合并周次范围"""
    class_id = request.args.get('class_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    room_id = request.args.get('room_id', type=int)

    query = ScheduleEntry.select()
    if class_id:
        tc_ids = [tc.id for tc in TeachingClass.select().where(TeachingClass.school_class == class_id)]
        query = query.where(ScheduleEntry.teaching_class.in_(tc_ids))
    if teacher_id:
        tc_ids = [tc.id for tc in TeachingClass.select().where(TeachingClass.teacher == teacher_id)]
        query = query.where(ScheduleEntry.teaching_class.in_(tc_ids))
    if room_id:
        query = query.where(ScheduleEntry.room == room_id)

    entries = list(query.order_by(ScheduleEntry.day, ScheduleEntry.period))

    # 按 (day, period, course) 分组，计算周次范围
    grouped = {}
    for entry in entries:
        tc = entry.teaching_class
        course = tc.course if tc else None
        cls = tc.school_class if tc else None
        teacher = tc.teacher if tc else None
        room = entry.room

        key = (entry.day, entry.period, entry.teaching_class_id)
        if key not in grouped:
            grouped[key] = {
                'day': entry.day,
                'period': entry.period,
                'course_name': course.name if course else None,
                'course_id': course.id if course else None,
                'teacher_name': teacher.name if teacher else None,
                'teacher_id': teacher.id if teacher else None,
                'class_name': cls.name if cls else None,
                'room_name': room.name if room else None,
                'room_id': room.id if room else None,
                'weeks': [],
            }
        grouped[key]['weeks'].append(entry.week)

    # 将连续周次合并为范围
    def weeks_to_ranges(weeks):
        if not weeks:
            return ''
        weeks = sorted(set(weeks))
        ranges = []
        start = weeks[0]
        end = weeks[0]
        for w in weeks[1:]:
            if w == end + 1:
                end = w
            else:
                ranges.append(f'{start}-{end}' if start != end else f'{start}')
                start = w
                end = w
        ranges.append(f'{start}-{end}' if start != end else f'{start}')
        return ','.join(ranges)

    result = []
    for key, data in grouped.items():
        data['week_ranges'] = weeks_to_ranges(data['weeks'])
        result.append(data)

    # 计算周次对应的日期（学期起始2026-09-07周一）
    from datetime import datetime, timedelta
    semester_start = datetime(2026, 9, 7)
    week_dates = {}
    for w in range(1, 17):
        monday = semester_start + timedelta(weeks=w-1)
        week_dates[str(w)] = {
            'monday': monday.strftime('%m-%d'),
            'dates': [(monday + timedelta(days=i)).strftime('%m-%d') for i in range(7)]
        }

    return jsonify({
        'courses': result,
        'week_dates': week_dates,
        'semester_start': semester_start.strftime('%Y-%m-%d'),
    })


@schedule_bp.route('/schedule/adjust/<int:entry_id>', methods=['PUT'])
def adjust_schedule(entry_id):
    entry = ScheduleEntry.get_or_none(ScheduleEntry.id == entry_id)
    if not entry:
        return jsonify({'error': '课表记录不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    new_day = data.get('day', entry.day)
    new_period = data.get('period', entry.period)
    new_room_id = data.get('room_id', entry.room_id)

    conflict = ScheduleEntry.select().where(
        (ScheduleEntry.week == entry.week) &
        (ScheduleEntry.day == new_day) &
        (ScheduleEntry.period == new_period) &
        (ScheduleEntry.room == new_room_id) &
        (ScheduleEntry.id != entry_id)
    ).first()
    if conflict:
        return jsonify({'error': '目标时段已有课程安排，存在冲突'}), 400

    tc = entry.teaching_class
    if tc:
        teacher_conflict = ScheduleEntry.select().join(TeachingClass, on=(ScheduleEntry.teaching_class == TeachingClass.id)).where(
            (TeachingClass.teacher == tc.teacher) &
            (ScheduleEntry.week == entry.week) &
            (ScheduleEntry.day == new_day) &
            (ScheduleEntry.period == new_period) &
            (ScheduleEntry.id != entry_id)
        ).first()
        if teacher_conflict:
            return jsonify({'error': '该教师在此时段已有其他课程，存在冲突'}), 400

    entry.day = new_day
    entry.period = new_period
    if new_room_id != entry.room_id:
        entry.room = Room.get_or_none(Room.id == new_room_id)
    entry.save()

    return jsonify({
        'message': '课表调整成功',
        'entry': {'id': entry.id, 'week': entry.week, 'day': entry.day, 'period': entry.period, 'room_id': entry.room.id if entry.room else None}
    })


@schedule_bp.route('/schedule/check-conflict/<int:teaching_class_id>', methods=['POST'])
def check_conflict(teaching_class_id):
    tc = TeachingClass.get_or_none(TeachingClass.id == teaching_class_id)
    if not tc:
        return jsonify({'error': '教学班不存在'}), 404

    data = request.get_json() or {}
    week = data.get('week')
    day = data.get('day')
    period = data.get('period')

    query = ScheduleEntry.select().where(ScheduleEntry.teaching_class == tc)
    if week:
        query = query.where(ScheduleEntry.week == week)
    if day:
        query = query.where(ScheduleEntry.day == day)
    if period:
        query = query.where(ScheduleEntry.period == period)

    entries = list(query)
    conflicts = []

    time_slots = {}
    for entry in entries:
        slot_key = f"{entry.week}-{entry.day}-{entry.period}"
        if slot_key in time_slots:
            conflicts.append({
                'type': 'duplicate_slot',
                'message': f'第{entry.week}周星期{entry.day} {entry.period} 时段存在重复安排',
                'entry_ids': [time_slots[slot_key], entry.id],
            })
        else:
            time_slots[slot_key] = entry.id

    for entry in entries:
        teacher_conflict = ScheduleEntry.select().join(TeachingClass, on=(ScheduleEntry.teaching_class == TeachingClass.id)).where(
            (TeachingClass.teacher == tc.teacher) &
            (ScheduleEntry.week == entry.week) &
            (ScheduleEntry.day == entry.day) &
            (ScheduleEntry.period == entry.period) &
            (ScheduleEntry.teaching_class != tc)
        ).first()
        if teacher_conflict:
            teacher = tc.teacher
            conflicts.append({
                'type': 'teacher_conflict',
                'message': f'教师 {teacher.name if teacher else ""} 在第{entry.week}周星期{entry.day} {entry.period} 有其他课程',
                'entry_id': entry.id, 'conflict_entry_id': teacher_conflict.id,
            })

        room_conflict = ScheduleEntry.select().where(
            (ScheduleEntry.week == entry.week) &
            (ScheduleEntry.day == entry.day) &
            (ScheduleEntry.period == entry.period) &
            (ScheduleEntry.room == entry.room) &
            (ScheduleEntry.id != entry.id)
        ).first()
        if room_conflict:
            room = entry.room
            conflicts.append({
                'type': 'room_conflict',
                'message': f'教室 {room.name if room else ""} 在第{entry.week}周星期{entry.day} {entry.period} 已被占用',
                'entry_id': entry.id, 'conflict_entry_id': room_conflict.id,
            })

    return jsonify({
        'teaching_class_id': teaching_class_id,
        'has_conflict': len(conflicts) > 0,
        'conflict_count': len(conflicts),
        'conflicts': conflicts,
    })


@schedule_bp.route('/schedule/statistics', methods=['GET'])
def get_statistics():
    class_id = request.args.get('class_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)

    entries = list(ScheduleEntry.select())

    if class_id:
        tc_ids = [tc.id for tc in TeachingClass.select().where(TeachingClass.school_class == class_id)]
        entries = [e for e in entries if e.teaching_class_id in tc_ids]
    if teacher_id:
        tc_ids = [tc.id for tc in TeachingClass.select().where(TeachingClass.teacher == teacher_id)]
        entries = [e for e in entries if e.teaching_class_id in tc_ids]

    period_hours = {'morning': 4, 'afternoon': 4, 'evening': 3}
    total_hours = 0
    period_distribution = {'morning': 0, 'afternoon': 0, 'evening': 0}
    weekly_distribution = {}
    daily_distribution = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

    for entry in entries:
        hours = period_hours.get(entry.period, 0)
        total_hours += hours
        period_distribution[entry.period] = period_distribution.get(entry.period, 0) + hours
        weekly_distribution[str(entry.week)] = weekly_distribution.get(str(entry.week), 0) + hours
        daily_distribution[str(entry.day)] = daily_distribution.get(str(entry.day), 0) + hours

    teacher_stats = {}
    tc_ids = list(set(e.teaching_class_id for e in entries))
    for tc_id in tc_ids:
        tc = TeachingClass.get_or_none(TeachingClass.id == tc_id)
        if tc and tc.teacher:
            t_name = tc.teacher.name
            if t_name not in teacher_stats:
                teacher_stats[t_name] = {'teacher_id': tc.teacher.id, 'hours': 0, 'sessions': 0}
            for e in entries:
                if e.teaching_class_id == tc_id:
                    teacher_stats[t_name]['hours'] += period_hours.get(e.period, 0)
                    teacher_stats[t_name]['sessions'] += 1

    room_stats = {}
    for entry in entries:
        room = entry.room
        if room:
            if room.name not in room_stats:
                room_stats[room.name] = {'room_id': room.id, 'hours': 0, 'sessions': 0}
            room_stats[room.name]['hours'] += period_hours.get(entry.period, 0)
            room_stats[room.name]['sessions'] += 1

    all_tc = list(TeachingClass.select())
    if class_id:
        all_tc = list(TeachingClass.select().where(TeachingClass.school_class == class_id))
    if teacher_id:
        all_tc = list(TeachingClass.select().where(TeachingClass.teacher == teacher_id))

    scheduled_tc_ids = set(e.teaching_class_id for e in entries)
    missing_tc = [tc for tc in all_tc if tc.id not in scheduled_tc_ids]

    total_tc_count = len(all_tc)
    scheduled_tc_count = len(scheduled_tc_ids)
    completion_rate = (scheduled_tc_count / total_tc_count * 100) if total_tc_count > 0 else 0

    return jsonify({
        'total_hours': total_hours,
        'total_sessions': len(entries),
        'period_distribution': period_distribution,
        'weekly_distribution': dict(sorted(weekly_distribution.items(), key=lambda x: int(x[0]))),
        'daily_distribution': daily_distribution,
        'teacher_statistics': list(teacher_stats.values()),
        'room_statistics': list(room_stats.values()),
        'missing_classes': [{'teaching_class_id': tc.id, 'course_id': tc.course.id if tc.course else None} for tc in missing_tc],
        'completion_rate': round(completion_rate, 2),
        'total_classes': total_tc_count,
        'scheduled_classes': scheduled_tc_count,
    })
