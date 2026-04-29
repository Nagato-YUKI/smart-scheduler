from flask import Blueprint, request, jsonify
from peewee_manager import SchoolClass

classes_bp = Blueprint('classes', __name__)


@classes_bp.route('/classes', methods=['GET'])
def get_classes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    department = request.args.get('department')
    name = request.args.get('name')

    query = SchoolClass.select()

    if department:
        query = query.where(SchoolClass.department == department)
    if name:
        query = query.where(SchoolClass.name.contains(name))

    total = query.count()
    classes = list(query.order_by(SchoolClass.id).limit(per_page).offset((page - 1) * per_page))

    return jsonify({
        'classes': [class_to_dict(c) for c in classes],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })


@classes_bp.route('/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    cls = SchoolClass.get_or_none(SchoolClass.id == class_id)
    if not cls:
        return jsonify({'error': '班级不存在'}), 404
    return jsonify(class_to_dict(cls))


@classes_bp.route('/classes', methods=['POST'])
def create_class():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required_fields = ['class_number', 'name', 'student_count']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400

    if SchoolClass.get_or_none(SchoolClass.class_number == data['class_number']):
        return jsonify({'error': '班级编号已存在'}), 400

    cls = SchoolClass.create(
        class_number=data['class_number'],
        name=data['name'],
        student_count=data['student_count'],
        department=data.get('department'),
        is_available=data.get('is_available', True)
    )

    return jsonify({
        'message': '班级创建成功',
        'class': class_to_dict(cls)
    }), 201


@classes_bp.route('/classes/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    cls = SchoolClass.get_or_none(SchoolClass.id == class_id)
    if not cls:
        return jsonify({'error': '班级不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    if 'class_number' in data and data['class_number'] != cls.class_number:
        if SchoolClass.get_or_none(SchoolClass.class_number == data['class_number']):
            return jsonify({'error': '班级编号已存在'}), 400
        cls.class_number = data['class_number']
    if 'name' in data:
        cls.name = data['name']
    if 'student_count' in data:
        cls.student_count = data['student_count']
    if 'department' in data:
        cls.department = data['department']
    if 'is_available' in data:
        cls.is_available = data['is_available']

    cls.save()

    return jsonify({
        'message': '班级更新成功',
        'class': class_to_dict(cls)
    })


@classes_bp.route('/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    cls = SchoolClass.get_or_none(SchoolClass.id == class_id)
    if not cls:
        return jsonify({'error': '班级不存在'}), 404

    from peewee_manager import TeachingClass, Course
    if TeachingClass.select().where(TeachingClass.school_class == cls).exists():
        return jsonify({'error': '该班级已有教学班，无法删除'}), 400
    if Course.select().where(Course.school_class == cls).exists():
        return jsonify({'error': '该班级已有课程，无法删除'}), 400

    cls.delete_instance()
    return jsonify({'message': '班级删除成功'})


def class_to_dict(cls):
    return {
        'id': cls.id,
        'class_number': cls.class_number,
        'name': cls.name,
        'student_count': cls.student_count,
        'department': cls.department,
        'is_available': getattr(cls, 'is_available', True),
        'created_at': cls.created_at.isoformat() if cls.created_at else None,
        'updated_at': cls.updated_at.isoformat() if cls.updated_at else None
    }
