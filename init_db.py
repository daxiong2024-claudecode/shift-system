"""
数据库初始化脚本
运行：python init_db.py
会创建所有表并插入初始数据（默认账号、4种班次、示例员工）
"""
from datetime import time, date
from app import create_app, db
from app.models.employee import Employee, Team
from app.models.shift import Shift

app = create_app('development')

with app.app_context():
    print('正在创建数据库表...')
    db.create_all()
    print('✅ 表结构创建完成')

    # ===== 初始化团队 =====
    if Team.query.count() == 0:
        teams = [
            Team(name='电销一组'),
            Team(name='电销二组'),
            Team(name='电销三组'),
        ]
        db.session.add_all(teams)
        db.session.flush()
        print(f'✅ 创建团队：{[t.name for t in teams]}')

    team1 = Team.query.filter_by(name='电销一组').first()

    # ===== 初始化班次 =====
    if Shift.query.count() == 0:
        shifts = [
            Shift(
                shift_code='MORNING', shift_name='早班',
                work_start=time(8, 0), work_end=time(16, 0),
                call_start=time(8, 0), call_end=time(16, 0),
                min_agents=3, color_tag='#4A90E2',
            ),
            Shift(
                shift_code='AFTERNOON', shift_name='中班',
                work_start=time(11, 0), work_end=time(19, 0),
                call_start=time(11, 0), call_end=time(19, 0),
                min_agents=4, color_tag='#27AE60',
            ),
            Shift(
                shift_code='EVENING', shift_name='晚班',
                work_start=time(13, 0), work_end=time(21, 0),
                call_start=time(13, 0), call_end=time(21, 0),
                min_agents=3, color_tag='#E67E22',
            ),
            Shift(
                shift_code='FULLDAY', shift_name='全天班',
                work_start=time(9, 0), work_end=time(18, 0),
                call_start=time(9, 0), call_end=time(18, 0),
                min_agents=2, color_tag='#9B59B6',
            ),
            Shift(
                shift_code='REST', shift_name='休息',
                work_start=time(0, 0), work_end=time(0, 0),
                is_rest=True, color_tag='#555570',
            ),
        ]
        db.session.add_all(shifts)
        print(f'✅ 创建班次：{[s.shift_name for s in shifts]}')

    # ===== 初始化员工 =====
    if Employee.query.count() == 0:
        employees = [
            # 管理员/总监
            {'no': 'admin', 'name': '系统管理员', 'role': 'director', 'pwd': 'admin123'},
            # 经理
            {'no': 'MGR001', 'name': '李经理', 'role': 'manager', 'pwd': 'mgr123'},
            # 组长
            {'no': 'LDR001', 'name': '王组长', 'role': 'leader', 'team': '电销一组', 'pwd': 'ldr123'},
            {'no': 'LDR002', 'name': '陈组长', 'role': 'leader', 'team': '电销二组', 'pwd': 'ldr123'},
            # 坐席
            {'no': 'AGT001', 'name': '张三', 'role': 'agent', 'team': '电销一组', 'pwd': 'agent123'},
            {'no': 'AGT002', 'name': '李四', 'role': 'agent', 'team': '电销一组', 'pwd': 'agent123'},
            {'no': 'AGT003', 'name': '王五', 'role': 'agent', 'team': '电销一组', 'pwd': 'agent123'},
            {'no': 'AGT004', 'name': '赵六', 'role': 'agent', 'team': '电销二组', 'pwd': 'agent123'},
            {'no': 'AGT005', 'name': '钱七', 'role': 'agent', 'team': '电销二组', 'pwd': 'agent123'},
        ]
        team_map = {t.name: t.id for t in Team.query.all()}
        for e in employees:
            emp = Employee(
                employee_no=e['no'],
                name=e['name'],
                role=e['role'],
                department='信贷电销部',
                team_id=team_map.get(e.get('team')),
                hire_date=date(2024, 1, 1),
                annual_leave=10,
            )
            emp.set_password(e['pwd'])
            db.session.add(emp)
        print(f'✅ 创建员工：{len(employees)} 人')

    db.session.commit()

    print('\n===== 初始化完成 =====')
    print('默认账号：')
    print('  管理员：admin / admin123')
    print('  经理：MGR001 / mgr123')
    print('  组长：LDR001 / ldr123')
    print('  坐席：AGT001 / agent123')
    print('\n启动服务：python run.py')
    print('访问：http://localhost:5000')
