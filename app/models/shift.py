from datetime import datetime, time
from app import db

# 外呼合规全局约束（硬编码，不可修改）
COMPLIANCE_START = time(8, 0)
COMPLIANCE_END = time(21, 0)


class Shift(db.Model):
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True)
    shift_code = db.Column(db.String(30), unique=True, nullable=False)
    shift_name = db.Column(db.String(50), nullable=False)
    work_start = db.Column(db.Time, nullable=False)
    work_end = db.Column(db.Time, nullable=False)
    call_start = db.Column(db.Time, nullable=True)   # None 表示不外呼
    call_end = db.Column(db.Time, nullable=True)
    is_rest = db.Column(db.Boolean, default=False)
    min_agents = db.Column(db.Integer, default=0)
    color_tag = db.Column(db.String(10), default='#4A90E2')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def validate_compliance(self):
        """校验外呼时段是否在合规区间内，返回 (ok, error_msg)"""
        if self.is_rest or self.call_start is None:
            return True, None
        if self.call_start < COMPLIANCE_START:
            return False, f'外呼开始时间不能早于 {COMPLIANCE_START.strftime("%H:%M")}（法规限制）'
        if self.call_end > COMPLIANCE_END:
            return False, f'外呼结束时间不能晚于 {COMPLIANCE_END.strftime("%H:%M")}（法规限制）'
        if self.call_start < self.work_start:
            return False, '外呼开始时间不能早于上班时间'
        if self.call_end > self.work_end:
            return False, '外呼结束时间不能晚于下班时间'
        return True, None

    def is_in_call_window(self, check_time=None):
        """判断当前时间是否在外呼窗口内"""
        if self.is_rest or self.call_start is None:
            return False
        t = check_time or datetime.now().time()
        return self.call_start <= t <= self.call_end

    def to_dict(self):
        return {
            'id': self.id,
            'shift_code': self.shift_code,
            'shift_name': self.shift_name,
            'work_start': self.work_start.strftime('%H:%M') if self.work_start else None,
            'work_end': self.work_end.strftime('%H:%M') if self.work_end else None,
            'call_start': self.call_start.strftime('%H:%M') if self.call_start else None,
            'call_end': self.call_end.strftime('%H:%M') if self.call_end else None,
            'is_rest': self.is_rest,
            'min_agents': self.min_agents,
            'color_tag': self.color_tag,
            'is_active': self.is_active,
        }
