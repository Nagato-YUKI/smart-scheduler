from flask import Blueprint, request, jsonify
from peewee_manager import Teacher

teachers_bp = Blueprint('teachers', __name__, url_prefix='/teachers')


@teachers_bp.route('', methods=['GET'])
def get_teachers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Teacher.select()
    total = query.count()
    teachers = query.paginate(page, per_page)
    return jsonify({
        'teachers': [teacher_to_dict(t) for t in teachers],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    return jsonify(teacher_to_dict(teacher))


@teachers_bp.route('', methods=['POST'])
def create_teacher():
    data = request.get_json()
    teacher = Teacher.create(
        teacher_number=data['teacher_number'],
        name=data['name'],
        teachable_courses=data.get('teachable_courses'),
        max_weekly_sessions=data.get('max_weekly_sessions', 5),
    )
    return jsonify(teacher_to_dict(teacher)), 201


@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    data = request.get_json()
    teacher.teacher_number = data.get('teacher_number', teacher.teacher_number)
    teacher.name = data.get('name', teacher.name)
    teacher.teachable_courses = data.get('teachable_courses', teacher.teachable_courses)
    teacher.max_weekly_sessions = data.get('max_weekly_sessions', teacher.max_weekly_sessions)
    teacher.save()
    return jsonify(teacher_to_dict(teacher))


@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    teacher = Teacher.get_or_none(Teacher.id == teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    teacher.delete_instance()
    return jsonify({'message': 'Teacher deleted'})


def teacher_to_dict(teacher):
    return {
        'id': teacher.id,
        'teacher_number': teacher.teacher_number,
        'name': teacher.name,
        'teachable_courses': teacher.teachable_courses,
        'max_weekly_sessions': teacher.max_weekly_sessions,
        'created_at': teacher.created_at.isoformat() if teacher.created_at else None,
    }
