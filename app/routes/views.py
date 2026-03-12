"""
前端页面路由（返回 HTML 模板）
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@views_bp.route('/login')
def login_page():
    return render_template('login.html')


@views_bp.route('/schedule')
@login_required
def schedule():
    return render_template('schedule.html')


@views_bp.route('/attendance')
@login_required
def attendance():
    return render_template('attendance.html')


@views_bp.route('/apply')
@login_required
def apply():
    return render_template('apply.html')


@views_bp.route('/approval')
@login_required
def approval():
    if current_user.role_level < 2:
        return redirect(url_for('views.index'))
    return render_template('approval.html')


@views_bp.route('/report')
@login_required
def report():
    if current_user.role_level < 2:
        return redirect(url_for('views.index'))
    return render_template('report.html')


@views_bp.route('/settings')
@login_required
def settings():
    if current_user.role_level < 3:
        return redirect(url_for('views.index'))
    return render_template('settings.html')
