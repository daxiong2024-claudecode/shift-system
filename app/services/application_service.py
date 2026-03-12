"""
请假/调班申请审批流服务
"""
from datetime import datetime
from app import db
from app.models.application import LeaveApplication
from app.models.schedule import Schedule


def submit_application(applicant_id, apply_type, start_date, end_date, days, reason, swap_with=None):
    """提交申请"""
    app = LeaveApplication(
        applicant_id=applicant_id,
        apply_type=apply_type,
        start_date=start_date,
        end_date=end_date,
        days=days,
        reason=reason,
        swap_with=swap_with,
        status='pending',
    )
    db.session.add(app)
    db.session.commit()
    return app


def approve(app_id: int, reviewer_id: int, comment: str, reviewer_role: str):
    """审批通过"""
    app = LeaveApplication.query.get_or_404(app_id)
    if app.status != 'pending':
        return None, '申请状态已变更，无法操作'

    now = datetime.utcnow()
    if reviewer_role in ('leader',):
        app.level1_reviewer = reviewer_id
        app.level1_time = now
        app.level1_comment = comment
        # 需要二级审批的情况
        if app.needs_level2():
            # 保持 pending，等待经理审批
            db.session.commit()
            return app, None
    elif reviewer_role in ('manager', 'director'):
        app.level2_reviewer = reviewer_id
        app.level2_time = now
        app.level2_comment = comment

    # 最终批准
    app.status = 'approved'
    _apply_to_schedule(app)
    db.session.commit()
    return app, None


def reject(app_id: int, reviewer_id: int, comment: str, reviewer_role: str):
    """审批拒绝"""
    app = LeaveApplication.query.get_or_404(app_id)
    if app.status != 'pending':
        return None, '申请状态已变更，无法操作'

    now = datetime.utcnow()
    if reviewer_role in ('leader',):
        app.level1_reviewer = reviewer_id
        app.level1_time = now
        app.level1_comment = comment
    else:
        app.level2_reviewer = reviewer_id
        app.level2_time = now
        app.level2_comment = comment

    app.status = 'rejected'
    db.session.commit()
    return app, None


def cancel_application(app_id: int, applicant_id: int):
    """申请人撤回"""
    app = LeaveApplication.query.get_or_404(app_id)
    if app.applicant_id != applicant_id:
        return None, '只能撤回自己的申请'
    if app.status != 'pending':
        return None, '只能撤回待审批的申请'
    app.status = 'cancelled'
    db.session.commit()
    return app, None


def _apply_to_schedule(application: LeaveApplication):
    """申请批准后更新排班"""
    from datetime import timedelta
    current = application.start_date
    while current <= application.end_date:
        if application.apply_type == 'adjust' and application.swap_with:
            # 调班：互换两人指定日期的班次
            s1 = Schedule.query.filter_by(employee_id=application.applicant_id, work_date=current).first()
            s2 = Schedule.query.filter_by(employee_id=application.swap_with, work_date=current).first()
            if s1 and s2:
                s1.shift_id, s2.shift_id = s2.shift_id, s1.shift_id
                s1.status = s2.status = 'adjusted'
                s1.source = s2.source = 'apply'
        else:
            # 请假：将排班状态标为 leave
            s = Schedule.query.filter_by(employee_id=application.applicant_id, work_date=current).first()
            if s:
                s.status = 'leave'
                s.source = 'apply'
        current += timedelta(days=1)
