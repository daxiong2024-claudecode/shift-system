from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('Employee', foreign_keys='Employee.team_id', backref='team', lazy='dynamic')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class Employee(UserMixin, db.Model):
    __tablename__ = 'employees'

    ROLES = ('agent', 'leader', 'manager', 'director')
    ROLE_LABELS = {
        'agent': '坐席',
        'leader': '组长',
        'manager': '经理',
        'director': '总监',
    }
    # 角色权重（越大权限越高）
    ROLE_LEVEL = {'agent': 1, 'leader': 2, 'manager': 3, 'director': 4}

    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(*ROLES), nullable=False, default='agent')
    department = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    hire_date = db.Column(db.Date)
    annual_leave = db.Column(db.Numeric(4, 1), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_level(self):
        return self.ROLE_LEVEL.get(self.role, 0)

    def can_manage(self, other_employee):
        """是否有权管理另一员工（role 更高，且同部门/组）"""
        return self.role_level > other_employee.role_level

    def to_dict(self):
        return {
            'id': self.id,
            'employee_no': self.employee_no,
            'name': self.name,
            'role': self.role,
            'role_label': self.ROLE_LABELS.get(self.role, self.role),
            'department': self.department,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'is_active': self.is_active,
            'annual_leave': float(self.annual_leave or 0),
        }


@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))
