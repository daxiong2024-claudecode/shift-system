"""
考勤业务逻辑服务
"""
from datetime import datetime, date, timedelta
from app import db
from app.models.attendance import Attendance
from app.models.schedule import Schedule

LATE_THRESHOLD_MINUTES = 15    # 迟到阈值（分钟）
EARLY_LEAVE_THRESHOLD_MINUTES = 30  # 早退阈值（分钟）


def clock_in(employee_id: int):
    """上班打卡"""
    today = date.today()
    now = datetime.now()

    att = Attendance.query.filter_by(employee_id=employee_id, work_date=today).first()
    if att and att.clock_in:
        return None, '今日已打过上班卡'

    schedule = Schedule.query.filter_by(employee_id=employee_id, work_date=today).first()

    if not att:
        att = Attendance(employee_id=employee_id, work_date=today, schedule_id=schedule.id if schedule else None)
        db.session.add(att)

    att.clock_in = now
    att.status = _calc_status(att, schedule)
    db.session.commit()
    return att, None


def clock_out(employee_id: int):
    """下班打卡"""
    today = date.today()
    now = datetime.now()

    att = Attendance.query.filter_by(employee_id=employee_id, work_date=today).first()
    if not att or not att.clock_in:
        return None, '请先打上班卡'
    if att.clock_out:
        return None, '今日已打过下班卡'

    schedule = Schedule.query.filter_by(employee_id=employee_id, work_date=today).first()
    att.clock_out = now
    att.status = _calc_status(att, schedule)
    db.session.commit()
    return att, None


def _calc_status(att: Attendance, schedule: Schedule):
    """根据打卡时间和排班时间计算考勤状态"""
    if not schedule or schedule.shift.is_rest:
        return 'normal'

    shift = schedule.shift
    work_start = datetime.combine(att.work_date, shift.work_start)
    work_end = datetime.combine(att.work_date, shift.work_end)

    if not att.clock_in:
        return 'clock_miss'

    late_minutes = max(0, int((att.clock_in - work_start).total_seconds() / 60))
    att.late_minutes = late_minutes

    early_minutes = 0
    if att.clock_out:
        early_minutes = max(0, int((work_end - att.clock_out).total_seconds() / 60))
        att.early_minutes = early_minutes

    if late_minutes > LATE_THRESHOLD_MINUTES:
        return 'late'
    if early_minutes > EARLY_LEAVE_THRESHOLD_MINUTES:
        return 'early_leave'
    if not att.clock_out:
        return 'clock_miss'
    return 'normal'


def adjust_attendance(att_id: int, operator_id: int, reason: str):
    """组长修正考勤异常"""
    att = Attendance.query.get_or_404(att_id)
    att.adjusted_by = operator_id
    att.adjust_reason = reason
    att.status = 'adjusted'
    db.session.commit()
    return att


def get_attendance_stats(employee_ids, start_date: date, end_date: date):
    """统计指定人员在日期范围内的考勤数据"""
    records = Attendance.query.filter(
        Attendance.employee_id.in_(employee_ids),
        Attendance.work_date >= start_date,
        Attendance.work_date <= end_date,
    ).all()

    from collections import defaultdict
    stats = defaultdict(lambda: {
        'total': 0, 'normal': 0, 'late': 0,
        'early_leave': 0, 'absent': 0, 'leave': 0,
    })
    for r in records:
        s = stats[r.employee_id]
        s['total'] += 1
        if r.status in s:
            s[r.status] += 1

    result = []
    for emp_id, s in stats.items():
        total = s['total']
        normal = s['normal']
        result.append({
            'employee_id': emp_id,
            'total_days': total,
            'normal': normal,
            'late': s['late'],
            'early_leave': s['early_leave'],
            'absent': s['absent'],
            'leave': s['leave'],
            'attendance_rate': round(normal / total * 100, 1) if total > 0 else 0,
        })
    return result
