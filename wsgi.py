from datetime import time, date
from app import create_app, db

app = create_app('development')


def init_db():
    from app.models.employee import Employee, Team
    from app.models.shift import Shift

    db.create_all()

    if Team.query.count() == 0:
        teams = [Team(name='电销一组'), Team(name='电销二组'), Team(name='电销三组')]
        db.session.add_all(teams)
        db.session.flush()

    team1 = Team.query.filter_by(name='电销一组').first()

    if Shift.query.count() == 0:
        shifts = [
            Shift(shift_code='MORNING', shift_name='早班', work_start=time(8,0), work_end=time(16,0), call_start=time(8,0), call_end=time(16,0), min_agents=3, color_tag='#4A90E2'),
            Shift(shift_code='AFTERNOON', shift_name='中班', work_start=time(11,0), work_end=time(19,0), call_start=time(11,0), call_end=time(19,0), min_agents=4, color_tag='#27AE60'),
            Shift(shift_code='EVENING', shift_name='晚班', work_start=time(13,0), work_end=time(21,0), call_start=time(13,0), call_end=time(21,0), min_agents=3, color_tag='#E67E22'),
            Shift(shift_code='FULLDAY', shift_name='全天班', work_start=time(9,0), work_end=time(18,0), call_start=time(9,0), call_end=time(18,0), min_agents=2, color_tag='#9B59B6'),
            Shift(shift_code='REST', shift_name='休息', work_start=time(0,0), work_end=time(0,0), is_rest=True, color_tag='#555570'),
        ]
        db.session.add_all(shifts)

    if Employee.query.count() == 0:
        employees = [
            {'no': 'admin', 'name': '系统管理员', 'role': 'director', 'pwd': 'admin123'},
            {'no': 'MGR001', 'name': '李经理', 'role': 'manager', 'pwd': 'mgr123'},
            {'no': 'LDR001', 'name': '王组长', 'role': 'leader', 'team': '电销一组', 'pwd': 'ldr123'},
            {'no': 'AGT001', 'name': '张三', 'role': 'agent', 'team': '电销一组', 'pwd': 'agent123'},
            {'no': 'AGT002', 'name': '李四', 'role': 'agent', 'team': '电销一组', 'pwd': 'agent123'},
        ]
        team_map = {t.name: t.id for t in Team.query.all()}
        for e in employees:
            emp = Employee(
                employee_no=e['no'], name=e['name'], role=e['role'],
                department='信贷电销部', team_id=team_map.get(e.get('team')),
                hire_date=date(2024, 1, 1), annual_leave=10,
            )
            emp.set_password(e['pwd'])
            db.session.add(emp)

    db.session.commit()


with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run()
