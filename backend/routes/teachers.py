from flask import Blueprint, request, jsonify
import json
from peewee_manager import Teacher
from utils.validators import validate_teacher_weekly_sessions, validate_teacher_course_count

teachers_bp = Blueprint('teachers', __name__)


@teachers_bp.route('/teachers', methods=['GET'])
def get_teachers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name = request.args.get('name')

    query = Teacher.select()

    if name:
        query = query.where(Teacher.name.contains(name))

    total = query.count()
    teachers = list(query.order_by(Teacher.id).limit(per_page).offset((page - 1) * per_page))

    return jsonify({
        'teachers': [teacher_to_dict(t) for t in teachers],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })


@teachers_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': '教师不存在'}), 404
    return jsonify(teacher_to_dict(teacher))


@teachers_bp.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required_fields = ['teacher_number', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400

    if Teacher.get_or_none(Teacher.teacher_number == data['teacher_number']):
        return jsonify({'error': '教师编号已存在'}), 400

    teachable_courses = data.get('teachable_courses')
    if teachable_courses and len(teachable_courses) > 2:
        return jsonify({'error': '教师可授课程门数不能超过2门'}), 400

    teacher = Teacher.create(
        teacher_number=data['teacher_number'],
        name=data['name'],
        teachable_courses=json.dumps(teachable_courses) if teachable_courses else None,
        max_classes=data.get('max_classes', 5),
        max_weekly_sessions=data.get('max_weekly_sessions', 5),
        is_available=data.get('is_available', True)
    )

    return jsonify({
        'message': '教师创建成功',
        'teacher': teacher_to_dict(teacher)
    }), 201


@teachers_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': '教师不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    if 'teacher_number' in data and data['teacher_number'] != teacher.teacher_number:
        if Teacher.get_or_none(Teacher.teacher_number == data['teacher_number']):
            return jsonify({'error': '教师编号已存在'}), 400
        teacher.teacher_number = data['teacher_number']

    if 'name' in data:
        teacher.name = data['name']
    if 'teachable_courses' in data:
        if len(data['teachable_courses']) > 2:
            return jsonify({'error': '教师可授课程门数不能超过2门'}), 400
        teacher.teachable_courses = json.dumps(data['teachable_courses'])
    if 'max_classes' in data:
        teacher.max_classes = data['max_classes']
    if 'max_weekly_sessions' in data:
        teacher.max_weekly_sessions = data['max_weekly_sessions']
    if 'is_available' in data:
        teacher.is_available = data['is_available']

    teacher.save()

    return jsonify({
        'message': '教师更新成功',
        'teacher': teacher_to_dict(teacher)
    })


@teachers_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': '教师不存在'}), 404

    from peewee_manager import TeachingClass, Course
    if TeachingClass.select().where(TeachingClass.teacher == teacher).exists():
        return jsonify({'error': '该教师已有教学班，无法删除'}), 400
    if Course.select().where(Course.teacher == teacher).exists():
        return jsonify({'error': '该教师已有课程，无法删除'}), 400

    teacher.delete_instance()
    return jsonify({'message': '教师删除成功'})


@teachers_bp.route('/teachers/<int:teacher_id>/validate', methods=['GET'])
def validate_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': '教师不存在'}), 404

    weekly_valid, weekly_msg = validate_teacher_weekly_sessions(teacher)
    course_valid, course_msg = validate_teacher_course_count(teacher)

    return jsonify({
        'teacher_id': teacher_id,
        'teacher_name': teacher.name,
        'weekly_sessions': {'valid': weekly_valid, 'message': weekly_msg},
        'course_count': {'valid': course_valid, 'message': course_msg},
        'is_valid': weekly_valid and course_valid
    })


def teacher_to_dict(teacher):
    tc = teacher.teachable_courses
    if tc and isinstance(tc, str):
        try:
            tc = json.loads(tc)
        except:
            tc = None
    return {
        'id': teacher.id,
        'teacher_number': teacher.teacher_number,
        'name': teacher.name,
        'teachable_courses': tc,
        'max_classes': teacher.max_classes,
        'max_weekly_sessions': teacher.max_weekly_sessions,
        'is_available': getattr(teacher, 'is_available', True),
        'created_at': teacher.created_at.isoformat() if teacher.created_at else None,
        'updated_at': teacher.updated_at.isoformat() if teacher.updated_at else None
    }
