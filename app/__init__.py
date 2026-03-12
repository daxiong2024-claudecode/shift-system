from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 注册路由蓝图
    from .routes.auth import auth_bp
    from .routes.shifts import shifts_bp
    from .routes.schedules import schedules_bp
    from .routes.attendance import attendance_bp
    from .routes.applications import applications_bp
    from .routes.report import report_bp
    from .routes.external_api import external_bp
    from .routes.views import views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shifts_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(external_bp)
    app.register_blueprint(views_bp)

    return app
