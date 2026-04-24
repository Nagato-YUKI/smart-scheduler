from flask import Blueprint, request, jsonify
from peewee_manager import Course

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    course_type = request.args.get('course_type')
    teacher_id = request.args.get('teacher_id', type=int)
    class_id = request.args.get('class_id', type=int)

    query = Course.select()
    if course_type:
        query = query.where(Course.course_type == course_type)
    if teacher_id:
        query = query.where(Course.teacher == teacher_id)
    if class_id:
        query = query.where(Course.school_class == class_id)

    total = query.count()
    courses = list(query.order_by(Course.id).limit(per_page).offset((page - 1) * per_page))

    return jsonify({
        'courses': [course_to_dict(c) for c in courses],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })


@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.get_or_none(Course.id == course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404
    return jsonify(course_to_dict(course))


@courses_bp.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required_fields = ['course_number', 'name', 'course_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400

    course_types = ['普通授课', '实验', '上机']
    if data['course_type'] not in course_types:
        return jsonify({'error': f'课程类型必须是: {", ".join(course_types)}'}), 400

    if Course.get_or_none(Course.course_number == data['course_number']):
        return jsonify({'error': '课程编号已存在'}), 400

    from peewee_manager import Teacher, SchoolClass
    teacher = Teacher.get_or_none(Teacher.id == data.get('teacher_id')) if data.get('teacher_id') else None
    school_class = SchoolClass.get_or_none(SchoolClass.id == data.get('class_id')) if data.get('class_id') else None

    course = Course.create(
        course_number=data['course_number'],
        name=data['name'],
        course_type=data['course_type'],
        total_hours=data.get('total_hours', 64),
        teacher=teacher,
        school_class=school_class
    )

    return jsonify({
        'message': '课程创建成功',
        'course': course_to_dict(course)
    }), 201


@courses_bp.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.get_or_none(Course.id == course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    course_types = ['普通授课', '实验', '上机']

    if 'course_number' in data and data['course_number'] != course.course_number:
        if Course.get_or_none(Course.course_number == data['course_number']):
            return jsonify({'error': '课程编号已存在'}), 400
        course.course_number = data['course_number']
    if 'name' in data:
        course.name = data['name']
    if 'course_type' in data:
        if data['course_type'] not in course_types:
            return jsonify({'error': f'课程类型必须是: {", ".join(course_types)}'}), 400
        course.course_type = data['course_type']
    if 'total_hours' in data:
        course.total_hours = data['total_hours']
    if 'teacher_id' in data:
        from peewee_manager import Teacher
        course.teacher = Teacher.get_or_none(Teacher.id == data['teacher_id']) if data['teacher_id'] else None
    if 'class_id' in data:
        from peewee_manager import SchoolClass
        course.school_class = SchoolClass.get_or_none(SchoolClass.id == data['class_id']) if data['class_id'] else None

    course.save()
    return jsonify({
        'message': '课程更新成功',
        'course': course_to_dict(course)
    })


@courses_bp.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.get_or_none(Course.id == course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404

    from peewee_manager import TeachingClass
    if TeachingClass.select().where(TeachingClass.course == course).exists():
        return jsonify({'error': '该课程已有教学班，无法删除'}), 400

    course.delete_instance()
    return jsonify({'message': '课程删除成功'})


def course_to_dict(course):
    return {
        'id': course.id,
        'course_number': course.course_number,
        'name': course.name,
        'course_type': course.course_type,
        'total_hours': course.total_hours,
        'teacher_id': course.teacher.id if course.teacher else None,
        'teacher_name': course.teacher.name if course.teacher else '-',
        'class_id': course.school_class.id if course.school_class else None,
        'class_name': course.school_class.name if course.school_class else '-',
        'created_at': course.created_at.isoformat() if course.created_at else None,
        'updated_at': course.updated_at.isoformat() if course.updated_at else None
    }
