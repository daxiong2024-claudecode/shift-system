from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.application import LeaveApplication
from app.services import application_service

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('/api/applications', methods=['GET'])
@login_required
def list_applications():
    mode = request.args.get('mode', 'mine')  # mine | pending_review
    if mode == 'pending_review' and current_user.role_level >= 2:
        # 待我审批：下属员工的 pending 申请
        from app.models.employee import Employee
        if current_user.role == 'leader' and current_user.team_id:
            emp_ids = [e.id for e in Employee.query.filter_by(team_id=current_user.team_id).all()]
        else:
            emp_ids = [e.id for e in Employee.query.filter_by(department=current_user.department).all()]
        apps = LeaveApplication.query.filter(
            LeaveApplication.applicant_id.in_(emp_ids),
            LeaveApplication.status == 'pending',
        ).order_by(LeaveApplication.created_at.desc()).all()
    else:
        apps = LeaveApplication.query.filter_by(
            applicant_id=current_user.id
        ).order_by(LeaveApplication.created_at.desc()).all()

    return jsonify({'applications': [a.to_dict() for a in apps]})


@applications_bp.route('/api/applications', methods=['POST'])
@login_required
def submit():
    data = request.get_json() or {}
    required = ['apply_type', 'start_date', 'end_date', 'days']
    for f in required:
        if data.get(f) is None:
            return jsonify({'error': f'缺少字段：{f}'}), 400

    app = application_service.submit_application(
        applicant_id=current_user.id,
        apply_type=data['apply_type'],
        start_date=date.fromisoformat(data['start_date']),
        end_date=date.fromisoformat(data['end_date']),
        days=data['days'],
        reason=data.get('reason', ''),
        swap_with=data.get('swap_with'),
    )
    return jsonify({'application': app.to_dict()}), 201


@applications_bp.route('/api/applications/<int:app_id>/approve', methods=['PUT'])
@login_required
def approve(app_id):
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    data = request.get_json() or {}
    result, err = application_service.approve(app_id, current_user.id, data.get('comment', ''), current_user.role)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'application': result.to_dict()})


@applications_bp.route('/api/applications/<int:app_id>/reject', methods=['PUT'])
@login_required
def reject(app_id):
    if current_user.role_level < 2:
        return jsonify({'error': '权限不足'}), 403
    data = request.get_json() or {}
    result, err = application_service.reject(app_id, current_user.id, data.get('comment', ''), current_user.role)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'application': result.to_dict()})


@applications_bp.route('/api/applications/<int:app_id>/cancel', methods=['PUT'])
@login_required
def cancel(app_id):
    result, err = application_service.cancel_application(app_id, current_user.id)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'application': result.to_dict()})
