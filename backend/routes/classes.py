from flask import Blueprint, request, jsonify
from peewee_manager import SchoolClass

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('', methods=['GET'])
def get_classes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = SchoolClass.select()
    total = query.count()
    classes = query.paginate(page, per_page)
    return jsonify({
        'classes': [class_to_dict(c) for c in classes],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@classes_bp.route('/<int:class_id>', methods=['GET'])
def get_class(class_id):
    cls = SchoolClass.get_or_none(SchoolClass.id == class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    return jsonify(class_to_dict(cls))


@classes_bp.route('', methods=['POST'])
def create_class():
    data = request.get_json()
    cls = SchoolClass.create(
        class_number=data['class_number'],
        name=data['name'],
        student_count=data['student_count'],
        department=data.get('department'),
    )
    return jsonify(class_to_dict(cls)), 201


@classes_bp.route('/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    cls = SchoolClass.get_or_none(SchoolClass.id == class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    data = request.get_json()
    cls.class_number = data.get('class_number', cls.class_number)
    cls.name = data.get('name', cls.name)
    cls.student_count = data.get('student_count', cls.student_count)
    cls.department = data.get('department', cls.department)
    cls.save()
    return jsonify(class_to_dict(cls))


@classes_bp.route('/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    cls = SchoolClass.get_or_none(SchoolClass.id == class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    cls.delete_instance()
    return jsonify({'message': 'Class deleted'})


def class_to_dict(cls):
    return {
        'id': cls.id,
        'class_number': cls.class_number,
        'name': cls.name,
        'student_count': cls.student_count,
        'department': cls.department,
        'created_at': cls.created_at.isoformat() if cls.created_at else None,
    }
