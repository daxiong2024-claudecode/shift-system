"""
排班业务逻辑服务
"""
from datetime import date, timedelta
from app import db
from app.models.schedule import Schedule
from app.models.shift import Shift
from app.models.employee import Employee


def get_schedules(start_date: date, end_date: date, employee_ids=None, team_id=None):
    """查询排班记录，返回 Schedule 列表"""
    query = Schedule.query.filter(
        Schedule.work_date >= start_date,
        Schedule.work_date <= end_date,
    )
    if employee_ids:
        query = query.filter(Schedule.employee_id.in_(employee_ids))
    elif team_id:
        emp_ids = [e.id for e in Employee.query.filter_by(team_id=team_id, is_active=True).all()]
        query = query.filter(Schedule.employee_id.in_(emp_ids))
    return query.order_by(Schedule.work_date, Schedule.employee_id).all()


def batch_schedule(employee_ids, start_date: date, end_date: date, pattern: list, created_by_id: int):
    """
    批量排班。
    pattern: [{'weekday': 1-7, 'shift_id': int}, ...]  weekday: 1=周一 7=周日
    已有排班的日期跳过（不覆盖）。
    返回 (created_count, skipped_count, warnings)
    """
    weekday_map = {item['weekday']: item['shift_id'] for item in pattern}
    created, skipped = 0, 0
    warnings = []

    current = start_date
    while current <= end_date:
        weekday = current.isoweekday()  # 1=Mon ... 7=Sun
        shift_id = weekday_map.get(weekday)
        if shift_id is None:
            current += timedelta(days=1)
            continue

        for emp_id in employee_ids:
            existing = Schedule.query.filter_by(employee_id=emp_id, work_date=current).first()
            if existing:
                skipped += 1
                continue
            schedule = Schedule(
                employee_id=emp_id,
                work_date=current,
                shift_id=shift_id,
                status='scheduled',
                source='batch',
                created_by=created_by_id,
            )
            db.session.add(schedule)
            created += 1

        current += timedelta(days=1)

    # 检查最低人力保障
    warnings = check_min_agents_warnings(start_date, end_date)

    db.session.commit()
    return created, skipped, warnings


def update_schedule(schedule_id: int, shift_id: int, operator_id: int, remark: str = None):
    """手动修改单条排班"""
    schedule = Schedule.query.get_or_404(schedule_id)
    old_shift_id = schedule.shift_id
    schedule.shift_id = shift_id
    schedule.status = 'adjusted'
    schedule.source = 'manual'
    if remark:
        schedule.remark = remark

    # 写审计日志
    from app.models.audit_log import AuditLog
    import json
    log = AuditLog(
        operator_id=operator_id,
        action='UPDATE_SCHEDULE',
        target_type='schedule',
        target_id=schedule_id,
        old_value=json.dumps({'shift_id': old_shift_id}),
        new_value=json.dumps({'shift_id': shift_id, 'remark': remark}),
    )
    db.session.add(log)
    db.session.commit()
    return schedule


def copy_last_week(team_id: int, operator_id: int):
    """复制上周排班到本周"""
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(weeks=1)
    last_sunday = this_monday - timedelta(days=1)

    emp_ids = [e.id for e in Employee.query.filter_by(team_id=team_id, is_active=True).all()]
    last_week_schedules = get_schedules(last_monday, last_sunday, employee_ids=emp_ids)

    created, skipped = 0, 0
    for s in last_week_schedules:
        delta = s.work_date - last_monday
        new_date = this_monday + delta
        existing = Schedule.query.filter_by(employee_id=s.employee_id, work_date=new_date).first()
        if existing:
            skipped += 1
            continue
        new_schedule = Schedule(
            employee_id=s.employee_id,
            work_date=new_date,
            shift_id=s.shift_id,
            status='scheduled',
            source='batch',
            created_by=operator_id,
            remark='复制自上周',
        )
        db.session.add(new_schedule)
        created += 1

    db.session.commit()
    return created, skipped


def check_min_agents_warnings(start_date: date, end_date: date):
    """检查日期范围内每天每班次是否满足最低在岗人数，返回警告列表"""
    warnings = []
    current = start_date
    while current <= end_date:
        schedules = Schedule.query.filter_by(work_date=current).all()
        shift_counts = {}
        for s in schedules:
            if s.status not in ('leave', 'absent'):
                shift_counts[s.shift_id] = shift_counts.get(s.shift_id, 0) + 1

        shifts = Shift.query.filter(Shift.id.in_(shift_counts.keys()), Shift.min_agents > 0).all()
        for shift in shifts:
            actual = shift_counts.get(shift.id, 0)
            if actual < shift.min_agents:
                warnings.append({
                    'date': current.isoformat(),
                    'shift_name': shift.shift_name,
                    'required': shift.min_agents,
                    'actual': actual,
                })
        current += timedelta(days=1)
    return warnings
