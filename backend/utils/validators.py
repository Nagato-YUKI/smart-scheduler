# -*- coding: utf-8 -*-

def validate_room_data(data):
    errors = []
    if not data.get('room_number'):
        errors.append('教室编号不能为空')
    if not data.get('name'):
        errors.append('教室名称不能为空')
    capacity = data.get('capacity')
    if capacity is None or not isinstance(capacity, (int, float)) or capacity <= 0:
        errors.append('教室容量必须为正整数')
    room_type = data.get('room_type')
    valid_types = ['normal', 'computer', 'lab', 'meeting', 'other']
    if room_type and room_type not in valid_types:
        errors.append(f'教室类型无效，可选值: {", ".join(valid_types)}')
    return errors


def validate_teacher_data(data):
    errors = []
    if not data.get('teacher_number'):
        errors.append('教师工号不能为空')
    if not data.get('name'):
        errors.append('教师姓名不能为空')
    max_sessions = data.get('max_weekly_sessions')
    if max_sessions is not None:
        if not isinstance(max_sessions, int) or max_sessions < 1:
            errors.append('每周最大课次数必须为正整数')
    return errors


def validate_class_data(data):
    errors = []
    if not data.get('class_number'):
        errors.append('班级编号不能为空')
    if not data.get('name'):
        errors.append('班级名称不能为空')
    student_count = data.get('student_count')
    if student_count is None or not isinstance(student_count, (int, float)) or student_count <= 0:
        errors.append('学生人数必须为正整数')
    return errors


def validate_course_data(data):
    errors = []
    if not data.get('course_number'):
        errors.append('课程编号不能为空')
    if not data.get('name'):
        errors.append('课程名称不能为空')
    if not data.get('teacher_id'):
        errors.append('教师ID不能为空')
    if not data.get('class_id'):
        errors.append('班级ID不能为空')
    total_hours = data.get('total_hours')
    if total_hours is None or not isinstance(total_hours, (int, float)) or total_hours <= 0:
        errors.append('总课时必须为正整数')
    return errors
