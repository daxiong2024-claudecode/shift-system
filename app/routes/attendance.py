from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.attendance import Attendance
from app.services import attendance_service

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/api/attendance/clock-in', methods=['POST'])
@login_required
def clock_in():
    att, err = attendance_service.clock_in(current_user.id)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'attendance': att.to_dict()})


@attendance_bp.route('/api/attendance/clock-out', methods=['POST'])
@login_required
def clock_out():
    att, err = attendance_service.clock_out(current_user.id)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'attendance': att.to_dict()})


@attendance_bp.route('/api/attendance', methods=['GET'])
@login_required
def list_attendance():
    from datetime import date
    start_str = request.args.get('start_date')
    end_str = request.args.get('end_date')
    emp_id = request.args.get('employee_id', type=int)

    start = date.fromisoformat(start_str) if start_str else date.today().replace(day=1)
    end = date.fromisoformat(end_str) if end_str else date.today()

    query = Attendance.query.filter(
        Attendance.work_date >= start,
        Attendance.work_date <= end,
    )
    if current_user.role == 'agent':
        query = query.filter_by(employee_id=current_user.id)
    elif emp_id:
        query = query.filter_by(employee_id=emp_id)
    elif current_user.role == 'leader' and current_user.team_id:
        from app.models.employee import Employee
        emp_ids = [e.id for e in Employee.query.filter_by(team_id=current_user.team_id, is_active=True).all()]
        query = query.filter(Attendance.employee_id.in_(emp_ids))

    records = query.order_by(Attendance.work_date.desc(), Attendance.employee_id).all()
    return jsonify({'records': [r.to_dict() for r in records]})


@attendance_bp.route('/api/attendance/<int:att_id>/adjust', methods=['PUT'])
@login_required
def adjust(att_id):
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足，需要组长以上'}), 403
    data = request.get_json() or {}
    reason = data.get('reason', '')
    att = attendance_service.adjust_attendance(att_id, current_user.id, reason)
    return jsonify({'attendance': att.to_dict()})
