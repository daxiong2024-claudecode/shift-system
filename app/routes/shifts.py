from datetime import time
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.shift import Shift
from app.services.compliance_service import validate_call_window, get_compliance_info

shifts_bp = Blueprint('shifts', __name__)


def _parse_time(s):
    if not s:
        return None
    h, m = map(int, s.split(':'))
    return time(h, m)


@shifts_bp.route('/api/shifts', methods=['GET'])
@login_required
def list_shifts():
    shifts = Shift.query.filter_by(is_active=True).order_by(Shift.shift_code).all()
    return jsonify({
        'shifts': [s.to_dict() for s in shifts],
        'compliance': get_compliance_info(),
    })


@shifts_bp.route('/api/shifts', methods=['POST'])
@login_required
def create_shift():
    if current_user.role_level < 3:  # 经理以上
        return jsonify({'error': '权限不足'}), 403

    data = request.get_json() or {}
    required = ['shift_name', 'work_start', 'work_end']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'缺少字段：{f}'}), 400

    shift_code = data.get('shift_code') or data['shift_name'].upper().replace(' ', '_')
    if Shift.query.filter_by(shift_code=shift_code).first():
        return jsonify({'error': f'班次编码 {shift_code} 已存在'}), 400

    work_start = _parse_time(data['work_start'])
    work_end = _parse_time(data['work_end'])
    call_start = _parse_time(data.get('call_start'))
    call_end = _parse_time(data.get('call_end'))
    is_rest = data.get('is_rest', False)

    if not is_rest and call_start and call_end:
        ok, err = validate_call_window(call_start, call_end, work_start, work_end)
        if not ok:
            return jsonify({'error': err}), 400

    shift = Shift(
        shift_code=shift_code,
        shift_name=data['shift_name'],
        work_start=work_start,
        work_end=work_end,
        call_start=call_start,
        call_end=call_end,
        is_rest=is_rest,
        min_agents=data.get('min_agents', 0),
        color_tag=data.get('color_tag', '#4A90E2'),
        created_by=current_user.id,
    )
    db.session.add(shift)
    db.session.commit()
    return jsonify({'shift': shift.to_dict()}), 201


@shifts_bp.route('/api/shifts/<int:shift_id>', methods=['PUT'])
@login_required
def update_shift(shift_id):
    if current_user.role_level < 3:
        return jsonify({'error': '权限不足'}), 403

    shift = Shift.query.get_or_404(shift_id)
    data = request.get_json() or {}

    if 'shift_name' in data:
        shift.shift_name = data['shift_name']
    if 'work_start' in data:
        shift.work_start = _parse_time(data['work_start'])
    if 'work_end' in data:
        shift.work_end = _parse_time(data['work_end'])
    if 'call_start' in data:
        shift.call_start = _parse_time(data['call_start'])
    if 'call_end' in data:
        shift.call_end = _parse_time(data['call_end'])
    if 'min_agents' in data:
        shift.min_agents = data['min_agents']
    if 'color_tag' in data:
        shift.color_tag = data['color_tag']
    if 'is_rest' in data:
        shift.is_rest = data['is_rest']

    if not shift.is_rest and shift.call_start and shift.call_end:
        ok, err = validate_call_window(shift.call_start, shift.call_end, shift.work_start, shift.work_end)
        if not ok:
            return jsonify({'error': err}), 400

    db.session.commit()
    return jsonify({'shift': shift.to_dict()})


@shifts_bp.route('/api/shifts/<int:shift_id>', methods=['DELETE'])
@login_required
def delete_shift(shift_id):
    if current_user.role_level < 3:
        return jsonify({'error': '权限不足'}), 403
    shift = Shift.query.get_or_404(shift_id)
    shift.is_active = False
    db.session.commit()
    return jsonify({'message': '已停用'})
