"""
外呼合规校验服务
核心规则：外呼时段必须在 08:00-21:00 内（法规硬约束，不可绕过）
"""
from datetime import time

COMPLIANCE_START = time(8, 0)
COMPLIANCE_END = time(21, 0)


def validate_call_window(call_start: time, call_end: time, work_start: time, work_end: time):
    """
    校验外呼时段合规性。
    返回 (is_valid: bool, error_message: str | None)
    """
    if call_start is None or call_end is None:
        return True, None

    if call_start >= call_end:
        return False, '外呼开始时间必须早于结束时间'

    if call_start < COMPLIANCE_START:
        return False, f'外呼开始时间不能早于 {COMPLIANCE_START.strftime("%H:%M")}（法规限制：营销外呼不得早于08:00）'

    if call_end > COMPLIANCE_END:
        return False, f'外呼结束时间不能晚于 {COMPLIANCE_END.strftime("%H:%M")}（法规限制：营销外呼不得晚于21:00）'

    if call_start < work_start:
        return False, '外呼开始时间不能早于上班时间'

    if call_end > work_end:
        return False, '外呼结束时间不能晚于下班时间'

    return True, None


def is_in_call_window(shift, check_time=None):
    """
    判断给定时间是否在班次的外呼窗口内。
    shift: Shift 模型实例
    check_time: time 对象，None 则取当前时间
    """
    from datetime import datetime
    if shift is None or shift.is_rest or shift.call_start is None:
        return False
    t = check_time or datetime.now().time()
    return shift.call_start <= t <= shift.call_end


def get_compliance_info():
    """返回全局合规时段信息（供前端展示）"""
    return {
        'call_compliance_start': COMPLIANCE_START.strftime('%H:%M'),
        'call_compliance_end': COMPLIANCE_END.strftime('%H:%M'),
        'note': '根据工业和信息化部规定，营销外呼不得在21:00至次日8:00之间进行',
    }
