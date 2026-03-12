from datetime import datetime
from app import db


class LeaveApplication(db.Model):
    __tablename__ = 'leave_applications'

    TYPES = ('sick', 'personal', 'annual', 'adjust', 'rest')
    TYPE_LABELS = {
        'sick': '病假', 'personal': '事假',
        'annual': '年假', 'adjust': '调班', 'rest': '补休',
    }
    STATUSES = ('pending', 'approved', 'rejected', 'cancelled')
    STATUS_LABELS = {
        'pending': '待审批', 'approved': '已批准',
        'rejected': '已拒绝', 'cancelled': '已撤回',
    }

    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    apply_type = db.Column(db.Enum(*TYPES), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Numeric(4, 1))
    reason = db.Column(db.String(500))
    swap_with = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)  # 调班对象
    swap_confirmed = db.Column(db.Boolean, default=False)  # 被调方是否确认
    status = db.Column(db.Enum(*STATUSES), default='pending')
    level1_reviewer = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    level1_time = db.Column(db.DateTime)
    level1_comment = db.Column(db.String(200))
    level2_reviewer = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    level2_time = db.Column(db.DateTime)
    level2_comment = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = db.relationship('Employee', foreign_keys=[applicant_id], backref='applications')
    swap_employee = db.relationship('Employee', foreign_keys=[swap_with])

    def needs_level2(self):
        """3天以上需要经理二级审批"""
        return float(self.days or 0) > 3

    def to_dict(self):
        return {
            'id': self.id,
            'applicant_id': self.applicant_id,
            'applicant_name': self.applicant.name if self.applicant else None,
            'apply_type': self.apply_type,
            'type_label': self.TYPE_LABELS.get(self.apply_type, self.apply_type),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'days': float(self.days or 0),
            'reason': self.reason,
            'swap_with': self.swap_with,
            'swap_with_name': self.swap_employee.name if self.swap_employee else None,
            'swap_confirmed': self.swap_confirmed,
            'status': self.status,
            'status_label': self.STATUS_LABELS.get(self.status, self.status),
            'level1_comment': self.level1_comment,
            'level2_comment': self.level2_comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
