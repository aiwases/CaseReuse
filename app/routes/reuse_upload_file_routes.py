from flask import Blueprint, request, jsonify
from app.models import Project
from app import db
import os

reuse_upload_bp = Blueprint('reuse_upload', __name__, url_prefix='/reuse/upload')


@reuse_upload_bp.route('/old-document/<int:project_id>', methods=['POST'])
def upload_old_document(project_id):
    """上传旧文档（支持PDF/TXT文件或字符串）"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目文件夹路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_folder = os.path.join(project_root, "projects", f"project_{project_id}")
    
    # 确保项目文件夹存在
    os.makedirs(project_folder, exist_ok=True)
    
    if 'file' in request.files:
        # 文件上传模式
        file = request.files['file']
        if file.filename == '':
            return jsonify({"code": 400, "msg": "请选择文件"}), 400
        
        # 检查文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.pdf', '.txt']:
            return jsonify({"code": 400, "msg": "只支持PDF和TXT文件"}), 400
        
        # 保存文件
        filename = f"old_document{file_ext}"
        file_path = os.path.join(project_folder, filename)
        file.save(file_path)
        
        # 更新项目记录
        project.upload_path = file_path
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "旧文档上传成功",
            "data": {
                "file_path": file_path,
                "filename": filename,
                "type": "file"
            }
        })
    else:
        # 字符串模式
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"code": 400, "msg": "缺少content字段"}), 400
        
        content = data['content']
        filename = "old_document.txt"
        file_path = os.path.join(project_folder, filename)
        
        # 保存字符串为TXT文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新项目记录
        project.upload_path = file_path
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "旧文档字符串保存成功",
            "data": {
                "file_path": file_path,
                "filename": filename,
                "type": "string"
            }
        })


@reuse_upload_bp.route('/new-document/<int:project_id>', methods=['POST'])
def upload_new_document(project_id):
    """上传新文档（支持PDF/TXT文件或字符串）"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目文件夹路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_folder = os.path.join(project_root, "projects", f"project_{project_id}")
    
    # 确保项目文件夹存在
    os.makedirs(project_folder, exist_ok=True)
    
    if 'file' in request.files:
        # 文件上传模式
        file = request.files['file']
        if file.filename == '':
            return jsonify({"code": 400, "msg": "请选择文件"}), 400
        
        # 检查文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.pdf', '.txt']:
            return jsonify({"code": 400, "msg": "只支持PDF和TXT文件"}), 400
        
        # 保存文件
        filename = f"new_document{file_ext}"
        file_path = os.path.join(project_folder, filename)
        file.save(file_path)
        
        # 更新项目记录
        project.new_document_path = file_path
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "新文档上传成功",
            "data": {
                "file_path": file_path,
                "filename": filename,
                "type": "file"
            }
        })
    else:
        # 字符串模式
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"code": 400, "msg": "缺少content字段"}), 400
        
        content = data['content']
        filename = "new_document.txt"
        file_path = os.path.join(project_folder, filename)
        
        # 保存字符串为TXT文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新项目记录
        project.new_document_path = file_path
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "新文档字符串保存成功",
            "data": {
                "file_path": file_path,
                "filename": filename,
                "type": "string"
            }
        })


@reuse_upload_bp.route('/old-testcase/<int:project_id>', methods=['POST'])
def upload_old_testcase(project_id):
    """上传旧测试用例文件（仅支持JSON文件）"""
    project = Project.query.get_or_404(project_id)
    
    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "请选择文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "请选择文件"}), 400
    
    # 检查文件类型（仅支持JSON）
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != '.json':
        return jsonify({"code": 400, "msg": "只支持JSON文件"}), 400
    
    # 获取项目文件夹路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_folder = os.path.join(project_root, "projects", f"project_{project_id}")
    
    # 确保项目文件夹存在
    os.makedirs(project_folder, exist_ok=True)
    
    # 保存文件
    filename = f"old_testcase{file_ext}"
    file_path = os.path.join(project_folder, filename)
    file.save(file_path)
    
    # 更新项目记录
    project.old_test_case_path = file_path
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "msg": "旧测试用例文件上传成功",
        "data": {
            "file_path": file_path,
            "filename": filename
        }
    })
