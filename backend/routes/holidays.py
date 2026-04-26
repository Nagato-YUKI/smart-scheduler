from flask import Blueprint, request, jsonify
from peewee_manager import Holiday
from datetime import datetime

holidays_bp = Blueprint('holidays', __name__, url_prefix='/holidays')


@holidays_bp.route('', methods=['GET'])
def get_holidays():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Holiday.select().order_by(Holiday.date)
    total = query.count()
    holidays = query.paginate(page, per_page)
    return jsonify({
        'holidays': [holiday_to_dict(h) for h in holidays],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@holidays_bp.route('', methods=['POST'])
def create_holiday():
    data = request.get_json()
    holiday = Holiday.create(
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        name=data['name'],
    )
    return jsonify(holiday_to_dict(holiday)), 201


@holidays_bp.route('/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    holiday = Holiday.get_or_none(Holiday.id == holiday_id)
    if not holiday:
        return jsonify({'error': 'Holiday not found'}), 404
    holiday.delete_instance()
    return jsonify({'message': 'Holiday deleted'})


def holiday_to_dict(holiday):
    return {
        'id': holiday.id,
        'date': holiday.date.isoformat(),
        'name': holiday.name,
        'created_at': holiday.created_at.isoformat() if holiday.created_at else None,
    }
