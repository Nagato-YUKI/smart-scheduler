from flask import Blueprint, request, jsonify
from peewee_manager import ScheduleEntry, TeachingClass, Room, Teacher, SchoolClass, Course, Holiday
from datetime import datetime, timedelta
import logging
from collections import defaultdict

schedule_bp = Blueprint('schedule', __name__)
logger = logging.getLogger(__name__)

# 学期开始日期（模块级常量，供所有函数使用）
SEMESTER_START = datetime(2026, 9, 7)
TOTAL_WEEKS = 20  # 排课20周


@schedule_bp.route('/schedule/run', methods=['POST'])
def run_schedule():
    """简单排课算法：
    1. 每门课每周固定排1次（上午或下午，4课时）
    2. 同一教师的课尽量集中在1-2天
    3. 教室轮流使用，保证均匀分布
    4. 自动跳过节假日
    """
    # 清空已有排课记录
    ScheduleEntry.delete().execute()

    # 基础参数
    semester_start = SEMESTER_START
    total_weeks = TOTAL_WEEKS
    period_hours = {'morning': 4, 'afternoon': 4, 'evening': 3}

    # 获取节假日，计算哪些(week, day)是节假日
    holiday_dates = set()
    for h in Holiday.select():
        holiday_dates.add(h.date)

    holiday_week_day = set()
    for week in range(1, total_weeks + 1):
        for day in range(1, 6):
            d = semester_start + timedelta(days=(week - 1) * 7 + day - 1)
            if d.date() in holiday_dates:
                holiday_week_day.add((week, day))

    # 获取可用教室（按容量排序）
    rooms = list(Room.select().where(Room.is_available == True).order_by(Room.capacity))

    # 获取教学班
    teaching_classes = list(TeachingClass.select())
    teaching_classes = [
        tc for tc in teaching_classes
        if tc.school_class and getattr(tc.school_class, 'is_available', True)
        and tc.teacher and getattr(tc.teacher, 'is_available', True)
    ]

    # ===== 按教师分组，集中排课 =====
    teacher_courses = defaultdict(list)
    for tc in teaching_classes:
        teacher_courses[tc.teacher.id].append(tc)

    # 带课多的教师先排
    sorted_teachers = sorted(teacher_courses.keys(), key=lambda tid: -len(teacher_courses[tid]))

    # 全局占用记录
    teacher_day_slots = defaultdict(set)  # {(teacher_id, day, period): set of weeks}
    class_day_slots = defaultdict(set)    # {(class_id, day, period): set of weeks}
    room_week_slots = defaultdict(set)    # {(room_id, week, day, period): True}

    # 每天课时统计（用于均衡排课）
    day_usage_count = defaultdict(int)  # {day: total hours scheduled}

    # 教室使用次数统计
    room_usage_count = defaultdict(int)

    # 教师排课日期记录（用于集中排课）
    teacher_scheduled_days = defaultdict(list)

    # ===== 第一步：为所有教师分配固定排课天 =====
    # 每个教师3天，不同教师错开，避免资源竞争
    for idx, teacher_id in enumerate(sorted_teachers):
        # 轮流分配到周一到周五（每人3天）
        days = [(idx % 5) + 1, ((idx % 5) + 2) % 5 + 1, ((idx % 5) + 3) % 5 + 1]
        days = sorted(set(days))  # 去重并排序
        teacher_scheduled_days[teacher_id] = days
    # ===== 第一步完成 =====

    scheduled_count = 0
    fail_count = 0

    for teacher_id in sorted_teachers:
        courses = teacher_courses[teacher_id]
        preferred_days = teacher_scheduled_days.get(teacher_id, [])

        # 为每个课程分配教室
        for tc in courses:
            cls = tc.school_class
            course = tc.course
            course_hours = course.total_hours if course and course.total_hours else 64  # 课程总课时

            if not cls:
                fail_count += 1
                continue

            best_day = None
            best_period = None
            best_weeks = []
            best_score = float('inf')

            # 遍历所有可能的(day, period)组合
            for day_num in range(1, 6):
                for period in ['morning', 'afternoon', 'evening']:
                    period_h = period_hours.get(period, 4)
                    target_sessions = (course_hours + period_h - 1) // period_h

                    # 检查这天-时段是否已被该教师占用
                    if (teacher_id, day_num, period) in teacher_day_slots:
                        continue

                    # 检查这天-时段是否已被该班级占用
                    if (cls.id, day_num, period) in class_day_slots:
                        continue

                    # 硬性约束：只允许在preferred_days中的日期排课
                    if day_num not in preferred_days:
                        continue

                    # 计算可用的周
                    weeks_possible = []
                    for week in range(1, total_weeks + 1):
                        if (week, day_num) in holiday_week_day:
                            continue
                        # 检查教室是否可用（任意一个教室即可）
                        room_available = False
                        for room in rooms:
                            if room.capacity >= cls.student_count:
                                if (room.id, week, day_num, period) not in room_week_slots:
                                    room_available = True
                                    break
                        if room_available:
                            weeks_possible.append(week)

                    # 至少需要80%的周次能满足课时需求
                    if len(weeks_possible) < target_sessions * 0.8:
                        continue

                    # 评分：以集中排课为主
                    # 首选天有奖励
                    consecutive_bonus = 1000 if day_num in preferred_days else 0

                    score = len(weeks_possible) * 10 - period_h - consecutive_bonus

                    if score < best_score:
                        best_score = score
                        best_day = day_num
                        best_period = period
                        best_period_h = period_h
                        best_weeks = weeks_possible
                        best_target_sessions = target_sessions

            if best_day and best_weeks:
                # 记录占用
                teacher_day_slots[(teacher_id, best_day, best_period)] = set(best_weeks)
                class_day_slots[(cls.id, best_day, best_period)] = set(best_weeks)

                # 更新每天课时统计
                total_hours_scheduled = best_target_sessions * best_period_h
                day_usage_count[best_day] += total_hours_scheduled

                # 记录教师的排课日（用于集中排课）
                if best_day not in teacher_scheduled_days[teacher_id]:
                    teacher_scheduled_days[teacher_id].append(best_day)

                # 为每一周分配教室
                for week in best_weeks[:best_target_sessions]:
                    # 选择使用最少的教室
                    suitable_rooms = [r for r in rooms if r.capacity >= cls.student_count]
                    sorted_rooms = sorted(suitable_rooms, key=lambda r: room_usage_count[r.id])

                    room = None
                    for r in sorted_rooms:
                        if (r.id, week, best_day, best_period) not in room_week_slots:
                            room = r
                            break

                    if room is None:
                        continue

                    ScheduleEntry.create(
                        teaching_class=tc,
                        week=week,
                        day=best_day,
                        period=best_period,
                        room=room,
                        is_holiday=False,
                    )
                    room_week_slots[(room.id, week, best_day, best_period)] = True
                    room_usage_count[room.id] += 1

                scheduled_count += 1
            else:
                fail_count += 1

    total_entries = ScheduleEntry.select().count()
    return jsonify({
        'message': '排课完成',
        'success_count': scheduled_count,
        'failed_count': fail_count,
        'total_entries': total_entries,
    }), 200


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

    week_dates = {}
    for w in range(1, TOTAL_WEEKS + 1):
        monday = SEMESTER_START + timedelta(weeks=w-1)
        week_dates[str(w)] = {
            'monday': monday.strftime('%m-%d'),
            'dates': [(monday + timedelta(days=i)).strftime('%m-%d') for i in range(7)]
        }

    return jsonify({
        'courses': result,
        'week_dates': week_dates,
        'semester_start': SEMESTER_START.strftime('%Y-%m-%d'),
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


@schedule_bp.route('/schedule/clear-entries', methods=['POST'])
def clear_schedule_entries():
    """仅清除排课记录，保留基础数据（教室、教师、班级、课程、节假日）"""
    try:
        count = ScheduleEntry.delete().execute()
        return jsonify({'message': f'已清空 {count} 条排课记录', 'deleted_count': count}), 200
    except Exception as e:
        logger.error(f'清空排课记录失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'清空排课记录失败: {str(e)}'}), 500


@schedule_bp.route('/schedule/clear-all', methods=['POST'])
def clear_all_data():
    """清除所有数据（包括基础数据和排课记录）- 谨慎使用"""
    try:
        ScheduleEntry.delete().execute()
        TeachingClass.delete().execute()
        Course.delete().execute()
        Holiday.delete().execute()
        SchoolClass.delete().execute()
        Teacher.delete().execute()
        Room.delete().execute()
        return jsonify({'message': '所有数据已清空（包括基础数据）'}), 200
    except Exception as e:
        logger.error(f'清空数据失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'清空数据失败: {str(e)}'}), 500


@schedule_bp.route('/schedule/statistics', methods=['GET'])
def get_statistics():
    class_id = request.args.get('class_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)

    period_hours = {'morning': 4, 'afternoon': 4, 'evening': 3}

    # 获取教学班IDs
    all_tc_query = TeachingClass.select()
    if class_id:
        all_tc_query = all_tc_query.where(TeachingClass.school_class == class_id)
    if teacher_id:
        all_tc_query = all_tc_query.where(TeachingClass.teacher == teacher_id)
    all_tc_list = list(all_tc_query)
    all_tc_ids = [tc.id for tc in all_tc_list]

    # 获取排课记录（数据库级别过滤）
    entries_query = ScheduleEntry.select().where(ScheduleEntry.teaching_class.in_(all_tc_ids))
    entries = list(entries_query)

    # 计算统计数据
    total_hours = 0
    period_distribution = {'morning': 0, 'afternoon': 0, 'evening': 0}
    weekly_distribution = {}
    daily_distribution = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

    # 预建 TeachingClass ID -> 教师的映射（避免重复查询）
    tc_teacher_map = {}  # {tc_id: teacher_name}
    tc_teacher_id_map = {}  # {tc_id: teacher_id}
    tc_course_map = {}
    for tc in all_tc_list:
        if tc.teacher:
            tc_teacher_map[tc.id] = tc.teacher.name
            tc_teacher_id_map[tc.id] = tc.teacher.id
        if tc.course:
            tc_course_map[tc.id] = tc.course.id

    teacher_stats = {}
    room_stats = {}

    for entry in entries:
        hours = period_hours.get(entry.period, 0)
        total_hours += hours
        period_distribution[entry.period] = period_distribution.get(entry.period, 0) + hours
        weekly_distribution[str(entry.week)] = weekly_distribution.get(str(entry.week), 0) + hours
        daily_distribution[str(entry.day)] = daily_distribution.get(str(entry.day), 0) + hours

        # 教师统计
        tc_id = entry.teaching_class_id
        if tc_id in tc_teacher_map:
            t_name = tc_teacher_map[tc_id]
            if t_name not in teacher_stats:
                teacher_stats[t_name] = {'teacher_id': tc_teacher_id_map.get(tc_id), 'hours': 0, 'sessions': 0}
            teacher_stats[t_name]['hours'] += hours
            teacher_stats[t_name]['sessions'] += 1

        # 教室统计
        if entry.room:
            room_name = entry.room.name
            if room_name not in room_stats:
                room_stats[room_name] = {'room_id': entry.room.id, 'hours': 0, 'sessions': 0}
            room_stats[room_name]['hours'] += hours
            room_stats[room_name]['sessions'] += 1

    scheduled_tc_ids = set(e.teaching_class_id for e in entries)
    missing_tc = [tc for tc in all_tc_list if tc.id not in scheduled_tc_ids]

    total_tc_count = len(all_tc_ids)
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
        'missing_classes': [{'teaching_class_id': tc.id, 'course_id': tc_course_map.get(tc.id)} for tc in missing_tc],
        'completion_rate': round(completion_rate, 2),
        'total_classes': total_tc_count,
        'scheduled_classes': scheduled_tc_count,
    })
