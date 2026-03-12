from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models.employee import Employee

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    employee_no = data.get('employee_no', '').strip()
    password = data.get('password', '')

    if not employee_no or not password:
        return jsonify({'error': '请输入工号和密码'}), 400

    emp = Employee.query.filter_by(employee_no=employee_no, is_active=True).first()
    if not emp or not emp.check_password(password):
        return jsonify({'error': '工号或密码错误'}), 401

    login_user(emp, remember=True)
    return jsonify({'message': '登录成功', 'user': emp.to_dict()})


@auth_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': '已登出'})


@auth_bp.route('/auth/me')
@login_required
def me():
    return jsonify(current_user.to_dict())
