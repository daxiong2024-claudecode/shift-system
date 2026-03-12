from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.employee import Employee
from app.models.schedule import Schedule
from app.models.shift import Shift
from app.services.attendance_service import get_attendance_stats

report_bp = Blueprint('report', __name__)


def _get_emp_ids():
    """根据当前用户权限返回可查询的员工 ID 列表"""
    if current_user.role in ('manager', 'director'):
        return [e.id for e in Employee.query.filter_by(is_active=True).all()]
    elif current_user.role == 'leader' and current_user.team_id:
        return [e.id for e in Employee.query.filter_by(team_id=current_user.team_id, is_active=True).all()]
    else:
        return [current_user.id]


@report_bp.route('/api/report/attendance', methods=['GET'])
@login_required
def attendance_report():
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    start = date.fromisoformat(request.args.get('start_date', date.today().replace(day=1).isoformat()))
    end = date.fromisoformat(request.args.get('end_date', date.today().isoformat()))
    emp_ids = _get_emp_ids()
    stats = get_attendance_stats(emp_ids, start, end)

    # 附上员工姓名
    emp_map = {e.id: e.name for e in Employee.query.filter(Employee.id.in_(emp_ids)).all()}
    for s in stats:
        s['employee_name'] = emp_map.get(s['employee_id'], '')

    return jsonify({'stats': stats, 'start_date': start.isoformat(), 'end_date': end.isoformat()})


@report_bp.route('/api/report/shift-distribution', methods=['GET'])
@login_required
def shift_distribution():
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    start = date.fromisoformat(request.args.get('start_date', date.today().replace(day=1).isoformat()))
    end = date.fromisoformat(request.args.get('end_date', date.today().isoformat()))

    schedules = Schedule.query.filter(
        Schedule.work_date >= start,
        Schedule.work_date <= end,
    ).all()

    from collections import defaultdict
    # 每天各班次人数
    daily = defaultdict(lambda: defaultdict(int))
    shift_total = defaultdict(int)
    for s in schedules:
        if s.shift and not s.shift.is_rest:
            daily[s.work_date.isoformat()][s.shift.shift_name] += 1
            shift_total[s.shift.shift_name] += 1

    return jsonify({
        'daily': dict(daily),
        'shift_total': dict(shift_total),
        'start_date': start.isoformat(),
        'end_date': end.isoformat(),
    })


@report_bp.route('/api/report/call-coverage', methods=['GET'])
@login_required
def call_coverage():
    if current_user.role_level < 3:
        return jsonify({'error': '权限不足'}), 403
    target_date = date.fromisoformat(request.args.get('date', date.today().isoformat()))

    schedules = Schedule.query.filter_by(work_date=target_date).all()
    # 每小时在岗人数
    hourly = {h: 0 for h in range(8, 22)}
    for s in schedules:
        if s.shift and s.shift.call_start and s.shift.call_end and not s.shift.is_rest:
            for h in range(s.shift.call_start.hour, s.shift.call_end.hour):
                if h in hourly:
                    hourly[h] += 1

    return jsonify({'date': target_date.isoformat(), 'hourly': hourly})
