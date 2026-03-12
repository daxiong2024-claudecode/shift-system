"""
对外接口 - 供现有电销策略系统（经营_app）调用
查询当前在岗且在外呼时段内的坐席列表
"""
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.services.compliance_service import is_in_call_window

external_bp = Blueprint('external', __name__)


@external_bp.route('/api/v1/on-duty-agents', methods=['GET'])
def on_duty_agents():
    """
    查询当前时间在岗且外呼时段内的坐席列表。
    供外呼系统调用，无需登录（内网接口）。
    可选参数：check_time=HH:MM（用于测试指定时间）
    """
    now = datetime.now()
    check_time_str = request.args.get('check_time')
    if check_time_str:
        h, m = map(int, check_time_str.split(':'))
        from datetime import time
        check_time = time(h, m)
    else:
        check_time = now.time()

    today = date.today()
    schedules = Schedule.query.filter_by(work_date=today).all()

    agents = []
    total_on_duty = 0

    for s in schedules:
        if s.status in ('absent', 'leave'):
            continue
        emp = s.employee
        if not emp or not emp.is_active or emp.role != 'agent':
            continue

        total_on_duty += 1
        in_window = is_in_call_window(s.shift, check_time) if s.shift else False

        agents.append({
            'employee_no': emp.employee_no,
            'name': emp.name,
            'team_id': emp.team_id,
            'shift_name': s.shift.shift_name if s.shift else None,
            'call_start': s.shift.call_start.strftime('%H:%M') if s.shift and s.shift.call_start else None,
            'call_end': s.shift.call_end.strftime('%H:%M') if s.shift and s.shift.call_end else None,
            'is_in_call_window': in_window,
        })

    in_window_count = sum(1 for a in agents if a['is_in_call_window'])

    return jsonify({
        'timestamp': now.strftime('%Y-%m-%dT%H:%M:%S'),
        'check_time': check_time.strftime('%H:%M'),
        'total_on_duty': total_on_duty,
        'total_in_call_window': in_window_count,
        'agents': [a for a in agents if a['is_in_call_window']],  # 只返回在外呼窗口的
        'all_agents': agents,
    })
