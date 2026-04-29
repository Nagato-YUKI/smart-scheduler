from flask import Blueprint, request, jsonify
from peewee_manager import Holiday
from datetime import date

holidays_bp = Blueprint('holidays', __name__)


@holidays_bp.route('/holidays', methods=['GET'])
def get_holidays():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name = request.args.get('name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Holiday.select()

    if name:
        query = query.where(Holiday.name.contains(name))
    if start_date:
        try:
            s = date.fromisoformat(start_date)
            query = query.where(Holiday.date >= s)
        except ValueError:
            return jsonify({'error': '开始日期格式错误，应为 YYYY-MM-DD'}), 400
    if end_date:
        try:
            e = date.fromisoformat(end_date)
            query = query.where(Holiday.date <= e)
        except ValueError:
            return jsonify({'error': '结束日期格式错误，应为 YYYY-MM-DD'}), 400

    total = query.count()
    holidays = list(query.order_by(Holiday.date).limit(per_page).offset((page - 1) * per_page))

    return jsonify({
        'holidays': [holiday_to_dict(h) for h in holidays],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })


@holidays_bp.route('/holidays/<int:holiday_id>', methods=['GET'])
def get_holiday(holiday_id):
    holiday = Holiday.get_or_none(Holiday.id == holiday_id)
    if not holiday:
        return jsonify({'error': '节假日不存在'}), 404
    return jsonify(holiday_to_dict(holiday))


@holidays_bp.route('/holidays', methods=['POST'])
def create_holiday():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required_fields = ['date', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400

    try:
        holiday_date = date.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400

    if Holiday.get_or_none(Holiday.date == holiday_date):
        return jsonify({'error': '该日期已有节假日记录'}), 400

    holiday = Holiday.create(date=holiday_date, name=data['name'])

    return jsonify({
        'message': '节假日创建成功',
        'holiday': holiday_to_dict(holiday)
    }), 201


@holidays_bp.route('/holidays/<int:holiday_id>', methods=['PUT'])
def update_holiday(holiday_id):
    holiday = Holiday.get_or_none(Holiday.id == holiday_id)
    if not holiday:
        return jsonify({'error': '节假日不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    if 'date' in data:
        try:
            holiday_date = date.fromisoformat(data['date'])
            if holiday_date != holiday.date:
                if Holiday.get_or_none(Holiday.date == holiday_date):
                    return jsonify({'error': '该日期已有节假日记录'}), 400
                holiday.date = holiday_date
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400

    if 'name' in data:
        holiday.name = data['name']

    holiday.save()
    return jsonify({
        'message': '节假日更新成功',
        'holiday': holiday_to_dict(holiday)
    })


@holidays_bp.route('/holidays/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    holiday = Holiday.get_or_none(Holiday.id == holiday_id)
    if not holiday:
        return jsonify({'error': '节假日不存在'}), 404

    holiday.delete_instance()
    return jsonify({'message': '节假日删除成功'})


def holiday_to_dict(holiday):
    return {
        'id': holiday.id,
        'date': holiday.date.isoformat() if holiday.date else None,
        'name': holiday.name,
        'created_at': holiday.created_at.isoformat() if holiday.created_at else None,
        'updated_at': holiday.updated_at.isoformat() if holiday.updated_at else None
    }
