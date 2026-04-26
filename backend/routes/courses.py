from flask import Blueprint, request, jsonify
from peewee_manager import Course, Teacher, SchoolClass

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')


@courses_bp.route('', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Course.select()
    total = query.count()
    courses = query.paginate(page, per_page)
    return jsonify({
        'courses': [course_to_dict(c) for c in courses],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.get_or_none(Course.id == course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    return jsonify(course_to_dict(course))


@courses_bp.route('', methods=['POST'])
def create_course():
    data = request.get_json()
    teacher = Teacher.get_or_none(Teacher.id == data['teacher_id'])
    school_class = SchoolClass.get_or_none(SchoolClass.id == data['class_id'])
    if not teacher or not school_class:
        return jsonify({'error': 'Teacher or class not found'}), 404
    course = Course.create(
        course_number=data['course_number'],
        name=data['name'],
        course_type=data['course_type'],
        total_hours=data.get('total_hours', 64),
        teacher=teacher,
        school_class=school_class,
    )
    return jsonify(course_to_dict(course)), 201


@courses_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.get_or_none(Course.id == course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    data = request.get_json()
    course.course_number = data.get('course_number', course.course_number)
    course.name = data.get('name', course.name)
    course.course_type = data.get('course_type', course.course_type)
    course.total_hours = data.get('total_hours', course.total_hours)
    if 'teacher_id' in data:
        course.teacher = Teacher.get_or_none(Teacher.id == data['teacher_id'])
    if 'class_id' in data:
        course.school_class = SchoolClass.get_or_none(SchoolClass.id == data['class_id'])
    course.save()
    return jsonify(course_to_dict(course))


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.get_or_none(Course.id == course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    course.delete_instance()
    return jsonify({'message': 'Course deleted'})


def course_to_dict(course):
    return {
        'id': course.id,
        'course_number': course.course_number,
        'name': course.name,
        'course_type': course.course_type,
        'total_hours': course.total_hours,
        'teacher_id': course.teacher_id,
        'teacher_name': course.teacher.name if course.teacher else None,
        'class_id': course.school_class_id,
        'class_name': course.school_class.name if course.school_class else None,
        'created_at': course.created_at.isoformat() if course.created_at else None,
    }
