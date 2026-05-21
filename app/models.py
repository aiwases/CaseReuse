from datetime import datetime
from app import db
from sqlalchemy.dialects.mysql import ENUM


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    files = db.relationship('FileRecord', backref='user', lazy=True)
    # 添加用户与项目的一对多关系
    projects = db.relationship('Project', backref='user', lazy=True,
                             foreign_keys='Project.user_id')
class FileRecord(db.Model):
    __tablename__ = "file_record"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')
    upload_path = db.Column(db.String(300))
    uploaded_at = db.Column(db.DateTime, default=datetime.now())
    log_info = db.Column(db.Text)
    file_type = db.Column(db.String(50))

    # 添加文件与项目的一对多关系
    projects = db.relationship('Project', backref='file_record', lazy=True,
                              foreign_keys='Project.file_record_id')

class Project(db.Model):
    """
    项目模型 - 对应数据库中的project表
    """
    __tablename__ = 'project'

    # 主键字段
    id = db.Column(db.Integer, primary_key=True, comment='项目ID')

    # 基本信息字段
    name = db.Column(db.String(255), nullable=False, comment='项目名称')
    description = db.Column(db.Text, comment='项目描述')
    process_type = db.Column(
        ENUM('reuse','generation'),
        default='generation',
        comment='项目类型'
    )

    # 外键关联字段
    file_record_id = db.Column(db.Integer, db.ForeignKey('file_record.id'), nullable=False, comment='关联的文件ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='项目创建者ID')

    # 状态管理字段
    status = db.Column(
        ENUM('ready', 'stage1', 'stage2', 'stage3', 'stage4', 'stage5', 'completed', 'failed'),
        default='ready',
        comment='项目状态'
    )
    reuse_status = db.Column(
        ENUM('Ready','Process','Merge_Ready','Step5_Done','Completed'),
        default='Ready',
        comment='项目状态'
    )
    is_running = db.Column(db.Boolean, default=False)  # ✅ 运行状态

    # 时间戳字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='项目创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='最后更新时间')
    started_at = db.Column(db.DateTime, comment='项目开始时间')
    completed_at = db.Column(db.DateTime, comment='项目完成时间')

    # 结果和配置字段
    upload_path = db.Column(db.String(300))
    new_document_path = db.Column(db.String(300))
    old_test_case_path = db.Column(db.String(300))
    intermediate_path1 = db.Column(db.String(300))
    intermediate_path2 = db.Column(db.String(300))
    intermediate_path3 = db.Column(db.String(300))
    new_test_scenarios_path = db.Column(db.String(300))
    intermediate_path4 = db.Column(db.String(300))
    intermediate_path5 = db.Column(db.String(300))
    intermediate_path6 = db.Column(db.String(300))
    result_path = db.Column(db.String(300))
    log_info = db.Column(db.Text)

