from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.services import schedule_service

schedules_bp = Blueprint('schedules', __name__)


def _parse_date(s):
    return date.fromisoformat(s) if s else None


@schedules_bp.route('/api/schedules', methods=['GET'])
@login_required
def list_schedules():
    start = _parse_date(request.args.get('start_date')) or date.today().replace(day=1)
    end = _parse_date(request.args.get('end_date')) or date.today()
    team_id = request.args.get('team_id', type=int)
    emp_id = request.args.get('employee_id', type=int)

    # 权限过滤：坐席只能看自己
    if current_user.role == 'agent':
        emp_ids = [current_user.id]
    elif emp_id:
        emp_ids = [emp_id]
    elif team_id:
        emp_ids = None
    elif current_user.role == 'leader' and current_user.team_id:
        team_id = current_user.team_id
        emp_ids = None
    else:
        emp_ids = None

    schedules = schedule_service.get_schedules(start, end, employee_ids=emp_ids, team_id=team_id)
    return jsonify({'schedules': [s.to_dict() for s in schedules]})


@schedules_bp.route('/api/schedules/batch', methods=['POST'])
@login_required
def batch_schedule():
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403

    data = request.get_json() or {}
    employee_ids = data.get('employee_ids', [])
    start = _parse_date(data.get('start_date'))
    end = _parse_date(data.get('end_date'))
    pattern = data.get('pattern', [])

    if not employee_ids or not start or not end or not pattern:
        return jsonify({'error': '缺少必要参数'}), 400

    created, skipped, warnings = schedule_service.batch_schedule(
        employee_ids, start, end, pattern, current_user.id
    )
    return jsonify({'created': created, 'skipped': skipped, 'warnings': warnings})


@schedules_bp.route('/api/schedules/copy-week', methods=['POST'])
@login_required
def copy_week():
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    data = request.get_json() or {}
    team_id = data.get('team_id') or current_user.team_id
    if not team_id:
        return jsonify({'error': '请指定团队'}), 400
    created, skipped = schedule_service.copy_last_week(team_id, current_user.id)
    return jsonify({'created': created, 'skipped': skipped})


@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    data = request.get_json() or {}
    shift_id = data.get('shift_id')
    if not shift_id:
        return jsonify({'error': '缺少 shift_id'}), 400
    s = schedule_service.update_schedule(schedule_id, shift_id, current_user.id, data.get('remark'))
    return jsonify({'schedule': s.to_dict()})


@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    s = Schedule.query.get_or_404(schedule_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': '已删除'})
