import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get('SHIFT_SECRET_KEY', 'dev-secret-key-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 外呼合规全局时段（硬编码，不可修改）
    CALL_COMPLIANCE_START = '08:00'
    CALL_COMPLIANCE_END = '21:00'


class DevelopmentConfig(Config):
    DEBUG = True
    # 开发环境使用 SQLite，无需安装 MySQL 即可运行
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SHIFT_DB_URI',
        f'sqlite:///{os.path.join(BASE_DIR, "shift_dev.db")}'
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('SHIFT_DB_USER', 'root')}:"
        f"{os.environ.get('SHIFT_DB_PASSWORD', '')}@"
        f"{os.environ.get('SHIFT_DB_HOST', 'localhost')}:"
        f"{os.environ.get('SHIFT_DB_PORT', '3306')}/"
        f"{os.environ.get('SHIFT_DB_NAME', 'shift_system')}"
        "?charset=utf8mb4"
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
