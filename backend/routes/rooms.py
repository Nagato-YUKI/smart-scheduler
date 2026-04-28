from flask import Blueprint, request, jsonify
from peewee_manager import Room

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('', methods=['GET'])
def get_rooms():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Room.select()
    total = query.count()
    rooms = query.paginate(page, per_page)
    return jsonify({
        'rooms': [room_to_dict(r) for r in rooms],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.get_or_none(Room.id == room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    return jsonify(room_to_dict(room))


@rooms_bp.route('', methods=['POST'])
def create_room():
    data = request.get_json()
    room = Room.create(
        room_number=data['room_number'],
        name=data['name'],
        capacity=data['capacity'],
        room_type=data['room_type'],
    )
    return jsonify(room_to_dict(room)), 201


@rooms_bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.get_or_none(Room.id == room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    data = request.get_json()
    room.room_number = data.get('room_number', room.room_number)
    room.name = data.get('name', room.name)
    room.capacity = data.get('capacity', room.capacity)
    room.room_type = data.get('room_type', room.room_type)
    room.save()
    return jsonify(room_to_dict(room))


@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.get_or_none(Room.id == room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    room.delete_instance()
    return jsonify({'message': 'Room deleted'})


def room_to_dict(room):
    return {
        'id': room.id,
        'room_number': room.room_number,
        'name': room.name,
        'capacity': room.capacity,
        'room_type': room.room_type,
        'is_available': room.is_available,
        'created_at': room.created_at.isoformat() if room.created_at else None,
    }
