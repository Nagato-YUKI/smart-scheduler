from flask import Blueprint, request, jsonify
from peewee_manager import Room

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('/rooms', methods=['GET'])
def get_rooms():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    room_type = request.args.get('room_type')
    is_available = request.args.get('is_available', type=str)

    query = Room.select()

    if room_type:
        query = query.where(Room.room_type == room_type)

    if is_available is not None:
        query = query.where(Room.is_available == (is_available.lower() == 'true'))

    total = query.count()
    rooms = list(query.order_by(Room.id).limit(per_page).offset((page - 1) * per_page))

    return jsonify({
        'rooms': [room_to_dict(room) for room in rooms],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })


@rooms_bp.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.get_or_none(Room.id == room_id)
    if not room:
        return jsonify({'error': '教室不存在'}), 404
    return jsonify(room_to_dict(room))


@rooms_bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required_fields = ['room_number', 'name', 'capacity', 'room_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400

    room_types = ['普通教室', '多媒体教室', '机房', '实验室']
    if data['room_type'] not in room_types:
        return jsonify({'error': f'教室类型必须是: {", ".join(room_types)}'}), 400

    if Room.get_or_none(Room.room_number == data['room_number']):
        return jsonify({'error': '教室编号已存在'}), 400

    room = Room.create(
        room_number=data['room_number'],
        name=data['name'],
        capacity=data['capacity'],
        room_type=data['room_type'],
        is_available=data.get('is_available', True)
    )

    return jsonify({
        'message': '教室创建成功',
        'room': room_to_dict(room)
    }), 201


@rooms_bp.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.get_or_none(Room.id == room_id)
    if not room:
        return jsonify({'error': '教室不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    room_types = ['普通教室', '多媒体教室', '机房', '实验室']

    if 'room_number' in data and data['room_number'] != room.room_number:
        if Room.get_or_none(Room.room_number == data['room_number']):
            return jsonify({'error': '教室编号已存在'}), 400
        room.room_number = data['room_number']

    if 'name' in data:
        room.name = data['name']
    if 'capacity' in data:
        room.capacity = data['capacity']
    if 'room_type' in data:
        if data['room_type'] not in room_types:
            return jsonify({'error': f'教室类型必须是: {", ".join(room_types)}'}), 400
        room.room_type = data['room_type']
    if 'is_available' in data:
        room.is_available = data['is_available']

    room.save()

    return jsonify({
        'message': '教室更新成功',
        'room': room_to_dict(room)
    })


@rooms_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.get_or_none(Room.id == room_id)
    if not room:
        return jsonify({'error': '教室不存在'}), 404

    from peewee_manager import TeachingClass, ScheduleEntry
    if TeachingClass.select().where(TeachingClass.assigned_room == room).exists():
        return jsonify({'error': '该教室已被教学班使用，无法删除'}), 400
    if ScheduleEntry.select().where(ScheduleEntry.room == room).exists():
        return jsonify({'error': '该教室已有排课记录，无法删除'}), 400

    room.delete_instance()

    return jsonify({'message': '教室删除成功'})


def room_to_dict(room):
    return {
        'id': room.id,
        'room_number': room.room_number,
        'name': room.name,
        'capacity': room.capacity,
        'room_type': room.room_type,
        'is_available': room.is_available,
        'created_at': room.created_at.isoformat() if room.created_at else None,
        'updated_at': room.updated_at.isoformat() if room.updated_at else None
    }
