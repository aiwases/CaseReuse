import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # 默认使用 MySQL（如果没配置环境变量则用本地 root 用户）
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:m11203002@localhost:3306/huawei"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', str(BASE_DIR / 'projects'))
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB
