from datetime import datetime
from app import db


class Attendance(db.Model):
    __tablename__ = 'attendances'

    STATUSES = ('normal', 'late', 'early_leave', 'absent', 'leave', 'clock_miss', 'adjusted')
    STATUS_LABELS = {
        'normal': '正常',
        'late': '迟到',
        'early_leave': '早退',
        'absent': '旷工',
        'leave': '请假',
        'clock_miss': '漏打卡',
        'adjusted': '已修正',
    }

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=True)
    clock_in = db.Column(db.DateTime, nullable=True)
    clock_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(*STATUSES), default='clock_miss')
    late_minutes = db.Column(db.Integer, default=0)
    early_minutes = db.Column(db.Integer, default=0)
    adjusted_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    adjust_reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'work_date', name='uniq_att_emp_date'),
    )

    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='attendances')
    schedule = db.relationship('Schedule', backref='attendance')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'work_date': self.work_date.isoformat(),
            'clock_in': self.clock_in.strftime('%H:%M:%S') if self.clock_in else None,
            'clock_out': self.clock_out.strftime('%H:%M:%S') if self.clock_out else None,
            'status': self.status,
            'status_label': self.STATUS_LABELS.get(self.status, self.status),
            'late_minutes': self.late_minutes,
            'early_minutes': self.early_minutes,
            'adjust_reason': self.adjust_reason,
        }
