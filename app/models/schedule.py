from datetime import datetime
from app import db


class Schedule(db.Model):
    __tablename__ = 'schedules'

    STATUSES = ('scheduled', 'adjusted', 'leave', 'absent')
    SOURCES = ('batch', 'manual', 'apply')

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=False)
    status = db.Column(db.Enum(*STATUSES), default='scheduled')
    source = db.Column(db.Enum(*SOURCES), default='batch')
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    remark = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'work_date', name='uniq_emp_date'),
    )

    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='schedules')
    shift = db.relationship('Shift', backref='schedules')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'work_date': self.work_date.isoformat(),
            'shift_id': self.shift_id,
            'shift_name': self.shift.shift_name if self.shift else None,
            'shift_code': self.shift.shift_code if self.shift else None,
            'color_tag': self.shift.color_tag if self.shift else '#ccc',
            'call_start': self.shift.call_start.strftime('%H:%M') if self.shift and self.shift.call_start else None,
            'call_end': self.shift.call_end.strftime('%H:%M') if self.shift and self.shift.call_end else None,
            'is_rest': self.shift.is_rest if self.shift else False,
            'status': self.status,
            'source': self.source,
            'remark': self.remark,
        }
