from flask import jsonify


class ValidationError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def handle_validation_error(error):
    return jsonify({"error": error.message}), error.status_code


def validate_teacher_weekly_sessions(teacher):
    from peewee_manager import TeachingClass

    teaching_classes = list(TeachingClass.select().where(TeachingClass.teacher == teacher))

    if not teaching_classes:
        return True, "教师暂无排课"

    weekly_sessions = len(teaching_classes)

    if weekly_sessions > teacher.max_weekly_sessions:
        return False, f"教师每周课次({weekly_sessions})已超过上限({teacher.max_weekly_sessions})"

    return True, f"教师每周课次正常({weekly_sessions}/{teacher.max_weekly_sessions})"


def validate_teacher_course_count(teacher):
    from peewee_manager import Course

    current_courses = list(Course.select().where(Course.teacher == teacher))
    current_count = len(current_courses)

    if current_count > 2:
        return False, f"教师可授课程门数({current_count})已超过上限(2)"

    return True, f"教师可授课程门数正常({current_count}/2)"


def validate_room_capacity(rooms, required_capacity):
    if not rooms:
        return False, "没有可用的教室"

    total_capacity = sum(room.capacity for room in rooms if room.is_available)
    available_count = sum(1 for room in rooms if room.is_available)

    if available_count == 0:
        return False, "没有可用的教室"

    if total_capacity < required_capacity:
        return False, f"教室总容量({total_capacity})不足({required_capacity})"

    return True, f"教室满足需求(可用{available_count}间，总容量{total_capacity})"


def validate_room_minimum_count(rooms, minimum_count):
    available_rooms = [room for room in rooms if room.is_available]
    available_count = len(available_rooms)

    if available_count < minimum_count:
        return False, f"可用教室数量({available_count})少于最低需求({minimum_count})"

    return True, f"教室数量满足需求({available_count}/{minimum_count})"
