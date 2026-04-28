from flask import Blueprint, request, jsonify
from peewee_manager import (
    ScheduleEntry, TeachingClass, Course, SchoolClass,
    Teacher, Room, Holiday
)
from datetime import datetime, timedelta
import json
from scheduler.main_scheduler import SchedulerCourse

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/run', methods=['POST'])
def run_schedule():
    data = request.get_json() or {}
    start_date_str = data.get('start_date')
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = datetime.now().date()

    from scheduler.main_scheduler import AdvancedScheduler
    from peewee_manager import Room, Teacher, SchoolClass, Course, TeachingClass, Holiday
    
    scheduler = AdvancedScheduler()
    
    rooms = list(Room.select().where(Room.is_available == True))
    
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

    scheduler.schedule_courses(courses_to_schedule)
    results = scheduler.get_schedule_results()

    success_count = 0
    failed_entries = []
    
    for entry in results:
        try:
            teaching_class = TeachingClass.get_by_id(int(entry['teaching_class_id']))
            room = Room.get_by_id(int(entry['room_id']))
            
            week_num = entry['week']
            
            ScheduleEntry.create(
                teaching_class=teaching_class,
                week=week_num,
                day=entry['day'],
                period=entry['period'],
                room=room,
                is_holiday=False,
            )
            success_count += 1
        except Exception as e:
            failed_entries.append({
                'entry': entry,
                'error': str(e),
            })

    return jsonify({
        'success_count': success_count,
        'total': len(results),
        'failed_entries': failed_entries[:10],
    })


@schedule_bp.route('/results', methods=['GET'])
def get_schedule_results():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    query = ScheduleEntry.select().join(TeachingClass).join(Course).join(SchoolClass).join(Teacher).join(Room)
    total = query.count()
    entries = query.paginate(page, per_page)
    results = []
    for entry in entries:
        results.append({
            'id': entry.id,
            'week': entry.week,
            'day': entry.day,
            'period': entry.period,
            'course_name': entry.teaching_class.course.name,
            'teacher_name': entry.teaching_class.teacher.name,
            'class_name': entry.teaching_class.school_class.name,
            'room_name': entry.room.name,
            'is_holiday': entry.is_holiday,
            'created_at': entry.created_at.isoformat() if entry.created_at else None,
        })
    return jsonify({
        'results': results,
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@schedule_bp.route('/weekly', methods=['GET'])
def get_weekly_schedule():
    week = request.args.get('week', 1, type=int)
    entries = ScheduleEntry.select().where(ScheduleEntry.week == week).join(TeachingClass).join(Course).join(SchoolClass).join(Teacher).join(Room)
    courses = []
    for entry in entries:
        courses.append({
            'id': entry.id,
            'week': entry.week,
            'day': entry.day,
            'period': entry.period,
            'course_name': entry.teaching_class.course.name,
            'teacher_name': entry.teaching_class.teacher.name,
            'class_name': entry.teaching_class.school_class.name,
            'room_name': entry.room.name,
        })
    return jsonify({'courses': courses})


@schedule_bp.route('/statistics', methods=['GET'])
def get_schedule_statistics():
    total_entries = ScheduleEntry.select().count()
    total_courses = Course.select().count()
    total_teachers = Teacher.select().count()
    total_rooms = Room.select().count()
    scheduled_courses = ScheduleEntry.select(ScheduleEntry.teaching_class).distinct().count()
    
    return jsonify({
        'total_entries': total_entries,
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'total_rooms': total_rooms,
        'scheduled_courses': scheduled_courses,
        'completion_rate': round((scheduled_courses / total_courses * 100), 2) if total_courses > 0 else 0,
    })


@schedule_bp.route('/clear', methods=['DELETE'])
def clear_schedule():
    count = ScheduleEntry.delete().execute()
    return jsonify({'deleted_count': count, 'message': 'Schedule cleared'})


@schedule_bp.route('/teacher/<int:teacher_id>', methods=['GET'])
def get_teacher_schedule(teacher_id):
    week = request.args.get('week', 1, type=int)
    entries = ScheduleEntry.select().join(TeachingClass).where(
        (TeachingClass.teacher_id == teacher_id) & (ScheduleEntry.week == week)
    ).join(Course).join(SchoolClass).join(Room)
    courses = []
    for entry in entries:
        courses.append({
            'id': entry.id,
            'week': entry.week,
            'day': entry.day,
            'period': entry.period,
            'course_name': entry.teaching_class.course.name,
            'teacher_name': entry.teaching_class.teacher.name,
            'class_name': entry.teaching_class.school_class.name,
            'room_name': entry.room.name,
        })
    return jsonify({'courses': courses})


@schedule_bp.route('/room/<int:room_id>', methods=['GET'])
def get_room_schedule(room_id):
    week = request.args.get('week', 1, type=int)
    entries = ScheduleEntry.select().join(Room).where(
        (Room.id == room_id) & (ScheduleEntry.week == week)
    ).join(TeachingClass).join(Course).join(SchoolClass).join(Teacher)
    courses = []
    for entry in entries:
        courses.append({
            'id': entry.id,
            'week': entry.week,
            'day': entry.day,
            'period': entry.period,
            'course_name': entry.teaching_class.course.name,
            'teacher_name': entry.teaching_class.teacher.name,
            'class_name': entry.teaching_class.school_class.name,
            'room_name': entry.room.name,
        })
    return jsonify({'courses': courses})


@schedule_bp.route('/class/<int:class_id>', methods=['GET'])
def get_class_schedule(class_id):
    week = request.args.get('week', 1, type=int)
    entries = ScheduleEntry.select().join(TeachingClass).where(
        (TeachingClass.school_class_id == class_id) & (ScheduleEntry.week == week)
    ).join(Course).join(SchoolClass).join(Teacher).join(Room)
    courses = []
    for entry in entries:
        courses.append({
            'id': entry.id,
            'week': entry.week,
            'day': entry.day,
            'period': entry.period,
            'course_name': entry.teaching_class.course.name,
            'teacher_name': entry.teaching_class.teacher.name,
            'class_name': entry.teaching_class.school_class.name,
            'room_name': entry.room.name,
        })
    return jsonify({'courses': courses})
