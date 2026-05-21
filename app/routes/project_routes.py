import json

from flask import Blueprint, session, url_for, request, jsonify, send_file, \
    current_app
from app.models import Project, FileRecord
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
import os
from app import db
import shutil
import re

from app.routes.file_routes import refresh_file_status
# from ..services.task import task1, task2, task3, task4
# from ..services.task_reuse import task_reuse1, task_reuse2, task_reuse3, task_reuse4
# from ..services.test_task import task1, task2, task3, task4

project_bp = Blueprint('project', __name__)

ALLOWED = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

@project_bp.route('/projects')
def list_projects():
    if 'user_id' not in session:
        return jsonify({"error": "请先登录"}), 401

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)
    keyword = request.args.get('keyword', '', type=str).strip()
    filename = request.args.get('filename', '', type=str).strip()
    status_filter = request.args.get('status', '', type=str).strip()
    sort_by = request.args.get('sort', 'updated_desc', type=str)
    search_type = request.args.get('search_type', 'project')
    file_id = request.args.get('file_id', type=str)
    print(file_id)
    # 合法化分页参数
    per_page = max(1, min(per_page, 100))
    page = max(1, page)

    # 基础查询
    query = Project.query.options(
        joinedload(Project.user),
        joinedload(Project.file_record)
    )

    # 文件 ID 筛选
    if file_id:
        query = query.filter(Project.file_record_id == file_id)
    else:
        if search_type == 'project' and keyword:
            query = query.filter(
                or_(
                    Project.name.ilike(f"%{keyword}%"),
                    Project.description.ilike(f"%{keyword}%")
                )
            )
        elif search_type == 'file' and filename:
            query = query.join(Project.file_record).filter(FileRecord.filename.ilike(f"%{filename}%"))

    # 状态筛选
    if status_filter == 'running':
        query = query.filter(Project.status.in_(['stage1', 'stage2', 'stage3', 'running']))
    elif status_filter:
        query = query.filter(Project.status == status_filter)

    # 排序
    if sort_by == 'updated_desc':
        query = query.order_by(Project.updated_at.desc())
    elif sort_by == 'created_desc':
        query = query.order_by(Project.created_at.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(Project.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Project.name.desc())
    else:
        query = query.order_by(Project.updated_at.desc())

    # 分页
    pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)

    # 构造前端需要的 JSON 格式
    projects_data = {
        "items": [
            {
                "id": p.id,
                "description": p.description,
                "process_type": p.process_type,
                "name": p.name,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
                # 关联用户信息
                "user": {
                    "id": p.user.id,
                    "name": p.user.name
                } if p.user else None,
                # 关联文件信息
                "file_record": {
                    "id": p.file_record.id,
                    "filename": p.file_record.filename,
                    "file_type": p.file_record.file_type  # ✅ 添加这个字段
                } if p.file_record else None
            }
            for p in pagination_obj.items
        ],
        "page": pagination_obj.page,
        "per_page": pagination_obj.per_page,
        "total": pagination_obj.total,
        "pages": pagination_obj.pages,
        "has_prev": pagination_obj.has_prev,
        "has_next": pagination_obj.has_next,
        "prev_num": pagination_obj.prev_num,
        "next_num": pagination_obj.next_num,
        "iter_pages": list(pagination_obj.iter_pages())
    }

    # 统计信息
    stats = {
        'total': Project.query.count(),
        'ready': Project.query.filter_by(status='ready').count(),
        'running': Project.query.filter(Project.status.in_(['stage1','stage2','stage3','running'])).count(),
        'completed': Project.query.filter_by(status='completed').count(),
        'failed': Project.query.filter_by(status='failed').count(),
    }

    return jsonify({
        "projects": projects_data,
        "stats": stats
    })

@project_bp.route('/create_project', methods=['POST'])
def create_project_api():
    """前端 axios 创建项目接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    file_id = data.get('file_id')
    process_type = data.get('process_type')

    if not name:
        return jsonify({"success": False, "message": "项目名称不能为空"}), 400

    user_id = session['user_id']

    # 检查项目名唯一性
    existing_project = Project.query.filter_by(user_id=user_id, name=name).first()
    if existing_project:
        return jsonify({
            "success": False,
            "message": f'您已有名为 "{name}" 的项目，请更换项目名称'
        }), 409

    # 获取 file_record
    rec = None
    if file_id:
        rec = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()
        if not rec:
            return jsonify({"success": False, "message": "文件不存在或无权限"}), 404

    # 创建项目
    project = Project(
        name=name,
        description=description,
        process_type=process_type,
        user_id=user_id,
        file_record_id=rec.id if rec else None,
        status='ready',
        upload_path=rec.upload_path if rec else None
    )
    db.session.add(project)
    db.session.flush()  # 获取 project.id

    # 创建项目独立文件夹
    project_folder = os.path.join(current_app.config['PROJECT_FOLDER'], f"project_{project.id}")
    os.makedirs(project_folder, exist_ok=True)

    # ✅ 更新文件状态（放在 commit 前，使用当前上下文）
    if rec:
        rec.status = 'processing'   # 例如 'uploaded' → 'used'
        db.session.add(rec)

    db.session.commit()

    return jsonify({"success": True, "message": "项目创建成功", "project_id": project.id})

@project_bp.route('/check_name', methods=['GET'])
def check_name():
    user_id = session.get('user_id')
    project_name = request.args.get('name', '')
    exists = Project.query.filter_by(user_id=user_id, name=project_name).first() is not None
    return jsonify({'exists': exists})

# =========================
# 更新项目名称和描述
# =========================
@project_bp.route('/update_info/<int:project_id>', methods=['POST'])
def update_info(project_id):
    """更新项目名称和描述"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_id = session['user_id']
    data = request.get_json()
    new_name = data.get('name', '').strip()
    new_desc = data.get('description', '').strip()

    if not new_name:
        return jsonify({"success": False, "message": "项目名称不能为空"}), 400

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"success": False, "message": "项目不存在或无权访问"}), 404

    # 检查是否重名
    existing = Project.query.filter_by(user_id=user_id, name=new_name).first()
    if existing and existing.id != project.id:
        return jsonify({"success": False, "message": "已有同名项目，请更换名称"}), 400

    project.name = new_name
    project.description = new_desc
    db.session.commit()

    return jsonify({"success": True, "message": "项目信息已更新"})

# =========================
# 删除项目
# =========================
@project_bp.route('/delete_project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
    user_id = session['user_id']
    print(project_id,"and",user_id)
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"success": False, "message": "项目不存在或无权访问"}), 404

    file_record_id = project.file_record_id

    # 删除项目文件夹
    project_folder = os.path.join(current_app.config['PROJECT_FOLDER'], f"project_{project.id}")
    if os.path.exists(project_folder):
        try:
            shutil.rmtree(project_folder)
        except Exception as e:
            current_app.logger.warning(f"删除项目文件夹失败: {e}")

    db.session.delete(project)
    db.session.commit()
    # =======================
    # 同步刷新文件状态
    # =======================
    if file_record_id is not None:
        refresh_file_status(file_record_id)  # 直接调用刷新函数
    return jsonify({
        "success": True,
        "message": "项目已删除",
        "redirect_url": url_for('project.list_projects')
    })

def background_process_file(app, project_id):
    """后台处理函数（支持分阶段继续执行）"""
    from app import db
    from app.models import Project
    from datetime import datetime
    import os, traceback

    with app.app_context():
        project = Project.query.get(project_id)
        if not project:
            print(f"[后台任务] 项目 {project_id} 不存在")
            return

        try:
            project_folder = os.path.join(app.config['PROJECT_FOLDER'], f"project_{project_id}")
            os.makedirs(project_folder, exist_ok=True)
            log_lines = [f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 后台任务开始处理"]

            # 根据状态判断执行步骤
            import time
            from datetime import datetime

            if project.status == 'ready':
                # ========= 任务1 =========
                start_time = time.time()
                start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                md_file_path, task_logs = task1(project.file_record.upload_path, project_folder)
                end_time = time.time()
                end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elapsed = end_time - start_time

                # ========= 记录日志 =========
                log_lines.append(f"[任务1] 开始执行时间：{start_str}")
                log_lines.extend(task_logs)
                log_lines.append(f"[任务1完成] 生成 md_file：{md_file_path}")
                log_lines.append(f"[任务1结束时间] {end_str}")
                log_lines.append(f"[任务1耗时] {elapsed:.2f} 秒")

                # ========= 更新数据库 =========
                existing_log = project.log_info or ""
                project.log_info = existing_log + "\n".join(log_lines) + "\n"

                project.intermediate_path1 = md_file_path
                project.status = 'stage1'
                project.is_running = False
                db.session.commit()

                return {"success": True, "next_status": "stage1", "message": "任务1完成，等待继续解析"}

            if project.status in ['stage1']:
                # ========= 任务2 =========
                start_time = time.time()
                start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                intermediate_path1 = project.intermediate_path1
                intermediate_path2, task_logs, status = task2(intermediate_path1, project_folder)
                end_time = time.time()
                end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elapsed = end_time - start_time

                # ========= 记录日志 =========
                log_lines.append(f"[任务2] 开始执行时间：{start_str}")
                log_lines.extend(task_logs)
                log_lines.append(f"[任务2完成] 生成中间文件2：{intermediate_path2}")
                log_lines.append(f"[任务2结束时间] {end_str}")
                log_lines.append(f"[任务2耗时] {elapsed:.2f} 秒")

                # ========= 更新数据库 =========
                existing_log = project.log_info or ""
                project.log_info = existing_log + "\n".join(log_lines) + "\n"

                if status=='failed':
                    project.status = 'stage1'
                else:
                    project.intermediate_path2 = intermediate_path2
                    project.status = 'stage2'
                project.is_running = False
                db.session.commit()

                return {"success": True, "next_status": "stage2", "message": "任务2完成，等待继续解析"}
            
            if project.status in ['stage2']:
                # ========= 任务3 =========
                start_time = time.time()
                start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                intermediate_path2 = project.intermediate_path2
                intermediate_path3,task_logs, status = task3(intermediate_path2, project_folder)
                end_time = time.time()
                end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elapsed = end_time - start_time

                # ========= 记录日志 =========
                log_lines.append(f"[任务3] 开始执行时间：{start_str}")
                log_lines.extend(task_logs)
                log_lines.append(f"[任务3完成] 生成中间文件3：{intermediate_path3}")
                log_lines.append(f"[任务3结束时间] {end_str}")
                log_lines.append(f"[任务3耗时] {elapsed:.2f} 秒")

                # ========= 更新数据库 =========
                existing_log = project.log_info or ""
                project.log_info = existing_log + "\n".join(log_lines) + "\n"

                if status=='failed':
                    project.status = 'stage2'
                else:
                    project.intermediate_path3 = intermediate_path3
                    project.status = 'stage3'
                project.is_running = False
                db.session.commit()

                return {"success": True, "next_status": "stage3", "message": "任务3完成，等待继续解析"}

            if project.status in ['stage3']:
                # ========= 任务4 =========
                start_time = time.time()
                start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                intermediate_path3 = project.intermediate_path3
                result_path,task_logs, status = task4(intermediate_path3, project_folder)
                end_time = time.time()
                end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elapsed = end_time - start_time


                # ========= 记录日志 =========
                log_lines.append(f"[任务4] 开始执行时间：{start_str}")
                log_lines.extend(task_logs)
                log_lines.append(f"[任务4完成] 最终结果生成：{result_path}")
                log_lines.append(f"[任务4结束时间] {end_str}")
                log_lines.append(f"[任务4耗时] {elapsed:.2f} 秒")

                # ========= 更新数据库 =========
                existing_log = project.log_info or ""
                project.log_info = existing_log + "\n".join(log_lines) + "\n"

                if status=='failed':
                    project.status = 'stage3'
                else:
                    project.completed_at = datetime.now()
                    project.result_path = result_path
                    project.status = 'completed'
                project.is_running = False
                db.session.commit()
                return {"success": True, "next_status": "completed", "message": "任务3完成，项目解析完成"}

            print(f"[后台任务] 项目 {project_id} 处理完成")

        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            project = Project.query.get(project_id)
            if project:
                project.status = 'failed'
                project.is_running = False
                db.session.commit()
            print(f"[后台任务] 项目 {project_id} 处理失败：{e}")


@project_bp.route('/start/<int:project_id>', methods=['POST'])
def start_project(project_id):
    from threading import Thread
    from app import create_app, db
    from app.models import Project, FileRecord
    from datetime import datetime
    from flask import request
    import os

    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_id = session['user_id']
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"success": False, "message": "项目不存在或无权限"}), 404

    # 对于 generation 类型项目，必须有文件
    file_record = None
    if project.process_type == "generation":
        file_record = FileRecord.query.filter_by(id=project.file_record_id, user_id=user_id).first()
        if not file_record:
            return jsonify({"success": False, "message": "关联文件不存在"}), 404

    # 检查 is_running 状态
    if project.is_running:
        return jsonify({
            "success": False,
            "message": "该项目正在运行中，请稍后再试。"
        }), 400

    try:
        # 更新为正在运行
        project.is_running = True
        project.started_at = datetime.now()
        db.session.commit()

        # 创建 app context
        app = create_app()

        # =========================
        # 根据 process_type 选择任务
        # =========================
        if project.process_type == "generation":

            t = Thread(
                target=background_process_file,
                args=(app, project.id)
            )

        else:
            return jsonify({
                "success": False,
                "message": f"未知的 process_type: {project.process_type}"
            }), 400

        # 启动线程
        t.start()

        return jsonify({
            "success": True,
            "message": "任务已启动，后台处理中..."
        })

    except Exception as e:
        db.session.rollback()
        project.is_running = False
        db.session.commit()
        return jsonify({
            "success": False,
            "message": f"启动任务失败：{str(e)}"
        })


@project_bp.route('/projects/<int:project_id>/progress', methods=['GET'])
def get_project_progress(project_id):
    """
    获取项目进度接口
    """
    # 从数据库获取项目信息
    project = Project.query.get_or_404(project_id)

    # 构建项目进度数据
    progress_data = {
        'id': project.id,
        'name': project.name,
        'process_type': project.process_type,
        'description': project.description,
        'status': project.status,
        'is_running': project.is_running,
        'current_step': get_current_step_from_status(project.status),
        'steps': [
            {'id': 1, 'name': '准备阶段', 'status': 'ready', 'completed': project.status != 'ready'},
            {'id': 2, 'name': '阶段一', 'status': 'stage1',
             'completed': project.status in ['stage2', 'stage3', 'completed', 'failed']},
            {'id': 3, 'name': '阶段二', 'status': 'stage2',
             'completed': project.status in ['stage3', 'completed', 'failed']},
            {'id': 4, 'name': '阶段三', 'status': 'stage3', 'completed': project.status in ['completed', 'failed']},
            {'id': 5, 'name': '完成', 'status': 'completed', 'completed': project.status == 'completed'}
        ],
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None,
        'started_at': project.started_at.isoformat() if project.started_at else None,
        'completed_at': project.completed_at.isoformat() if project.completed_at else None,
        'upload_path': project.upload_path,
        'intermediate_path1': project.intermediate_path1,
        'intermediate_path2': project.intermediate_path2,
        'intermediate_path3': project.intermediate_path3,
        'intermediate_path4': project.intermediate_path4,
        'intermediate_path5': project.intermediate_path5,
        'intermediate_path6': project.intermediate_path6,
        'result_path': project.result_path,
        'log_info': project.log_info,
    }

    return jsonify(progress_data)


def get_current_step_from_status(status):
    """
    根据项目状态获取当前步骤
    """
    step_map = {
        'ready': 1,
        'stage1': 2,
        'stage2': 3,
        'stage3': 4,
        'completed': 5,
        'failed': 5
    }
    return step_map.get(status, 1)


@project_bp.route('/project/<int:project_id>/intermediate2', methods=['GET'])
def get_project_intermediate2(project_id):
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path2

    # 2. 校验路径
    if not file_path:
        return jsonify({"error": "intermediate_path2 is empty"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # 3. 读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({"error": "failed to read json file", "detail": str(e)}), 500

    # 4. 构造「有序 section 列表」
    sections = []
    section_map = {}  # section -> items（仅用于查找，不用于输出）

    for item in data:
        if not isinstance(item, dict):
            continue
        if "id" not in item:
            continue

        section = item["id"].split("_")[0]

        if section not in section_map:
            section_map[section] = []
            sections.append({
                "section": section,
                "items": section_map[section]
            })

        section_map[section].append(item)

    # 5. 返回（list 不会被排序）
    return jsonify({
        "project_id": project.id,
        "intermediate_path2": file_path,
        "data": sections
    })

@project_bp.route('/project/<int:project_id>/upload_file', methods=['GET'])
def get_project_upload_file(project_id):
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.upload_path

    # 2. 基本校验
    if not file_path:
        return jsonify({"error": "upload_path is empty"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # 3. 判断文件类型
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # 4. PDF：直接返回文件流
    if ext == '.pdf':
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=False  # 前端可预览；如需下载改为 True
        )

    # 5. TXT：读取并返回字符串
    if ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return jsonify({
                "error": "failed to read txt file",
                "detail": str(e)
            }), 500

        return jsonify({
            "project_id": project.id,
            "file_type": "txt",
            "content": content
        })

    # 6. 不支持的类型
    return jsonify({
        "error": "unsupported file type",
        "extension": ext
    }), 415
def bio_to_entities(text: str, label_str: str):
    labels = label_str.split()
    entities = []

    if len(text) != len(labels):
        # 数据异常，直接返回空实体，避免前端炸
        return entities

    i = 0
    n = len(labels)

    while i < n:
        tag = labels[i]

        if tag == "O":
            i += 1
            continue

        if tag.startswith("B-"):
            entity_type = tag[2:]
            start = i
            i += 1

            while i < n and labels[i] == f"I-{entity_type}":
                i += 1

            end = i  # 左闭右开
            entities.append({
                "type": entity_type,
                "start": start,
                "end": end
            })
        else:
            # 非法 I-，跳过
            i += 1

    return entities


@project_bp.route('/project/<int:project_id>/intermediate3', methods=['GET'])
def get_project_intermediate3(project_id):
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)

    file_path = project.intermediate_path3

    # 2. 校验路径
    if not file_path:
        return jsonify({"error": "intermediate_path3 is empty"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # 3. 读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        return jsonify({
            "error": "failed to read json file",
            "detail": str(e)
        }), 500

    # 4. 转换数据结构（BIO → entities）
    result = []

    for item in raw_data:
        if not isinstance(item, dict):
            continue

        text = item.get("text")
        label = item.get("label")
        item_id = item.get("id")

        if not text or not label or not item_id:
            continue

        entities = bio_to_entities(text, label)

        result.append({
            "id": item_id,
            "text": text,
            "entities": entities
        })

    # 5. 返回给前端
    return jsonify({
        "project_id": project.id,
        "intermediate_path3": file_path,
        "data": result
    })

def parse_rule_text(text: str):
    if_part, then_part = text.strip().split("then")

    def parse_conditions(part):
        conditions = []
        parts = part.replace("if", "").strip().split(" and ")
        for p in parts:
            m = re.match(r'(.+?)\s+is\s+"(.+?)"', p.strip())
            if m:
                conditions.append({
                    "field": m.group(1).strip(),
                    "operator": "is",
                    "value": m.group(2)
                })
        return conditions

    return {
        "if": parse_conditions(if_part),
        "then": parse_conditions(then_part)
    }
def build_rule_text(rule: dict) -> str:
    """
    将结构化规则逆向转换回原始 DSL text
    rule: {
        "if": [{"field": "...", "value": "..."}, ...],
        "then": [{"field": "...", "value": "..."}, ...],
        "rule": "...",
        "focus": "...",
        "sourceId": "..."
    }
    返回值：字符串形式的 rule.text
    """
    def build_part(conds):
        return " and ".join(f'{c["field"]} is "{c["value"]}"' for c in conds)

    if_part = build_part(rule.get("if", []))
    then_part = build_part(rule.get("then", []))

    return f"if {if_part}\nthen {then_part}\n"

@project_bp.route('/project/<int:project_id>/intermediate4', methods=['GET'])
def get_project_intermediate4(project_id):
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path4

    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "invalid intermediate_path4"}), 400

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    rules_out = []

    for r in raw.get("rules", []):
        parsed = parse_rule_text(r.get("text", ""))

        rules_out.append({
            "rule": r.get("rule"),
            "focus": r.get("focus"),
            "sourceId": r.get("sourceId"),
            "if": parsed["if"],
            "then": parsed["then"]
        })

    return jsonify({
        "project_id": project.id,
        "rules": rules_out
    })

def parse_rule_text5(text: str):
    """
    将 rule.text 解析为结构化 if/then 条件，去掉 operator（所有都是 is）
    """
    try:
        if_part, then_part = text.strip().split("then")
    except ValueError:
        return {"if": [], "then": []}

    def parse(part):
        conds = []
        part = part.replace("if", "").strip()
        # 按 and 分割每个条件
        for p in part.split(" and "):
            m = re.match(r"(.+?)\s+is\s+'(.+?)'", p.strip())
            if m:
                conds.append({
                    "field": m.group(1).strip(),
                    "value": m.group(2)
                })
        return conds

    return {
        "if": parse(if_part),
        "then": parse(then_part)
    }

@project_bp.route('/project/<int:project_id>/intermediate5', methods=['GET'])
def get_project_intermediate5(project_id):
    # 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path5

    # 校验文件存在
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "invalid intermediate_path5"}), 400

    # 读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        return jsonify({"error": f"failed to read json file: {str(e)}"}), 500

    # 解析规则
    rules_out = []
    for r in raw:
        parsed = parse_rule_text5(r.get("text", ""))
        rules_out.append({
            "rule": r.get("rule"),
            "focus": r.get("focus"),
            "sourceId": r.get("sourceId"),
            "if": parsed["if"],
            "then": parsed["then"]
        })
    return jsonify({
        "project_id": project.id,
        "rules": rules_out
    })

@project_bp.route('/project/<int:project_id>/intermediate6', methods=['GET'])
def get_project_intermediate6(project_id):
    """
    从数据库的 intermediate_path6 读取规则前后关系 JSON，
    并额外返回 ruleTextMap: rule_id -> text
    """

    # ===== 1. 查询项目 =====
    project = Project.query.get_or_404(project_id)

    file_path = project.intermediate_path6

    # ===== 2. 校验路径 =====
    if not file_path:
        return jsonify({"error": "intermediate_path6 is empty"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # ===== 3. 读取 JSON 文件 =====
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
    except Exception as e:
        return jsonify({
            "error": "failed to read json file",
            "detail": str(e)
        }), 500

    # ===== 4. 构建 ruleTextMap =====
    rule_text_map = {}

    for item in rules_data:
        # 4.1 当前规则自身
        rule_id = item.get("rule")
        text = item.get("text", "")

        if rule_id:
            rule_text_map[rule_id] = text

        # 4.2 before 规则
        for before_id in item.get("before", []):
            if before_id not in rule_text_map:
                rule_text_map[before_id] = ""

        # 4.3 after 规则（支持逗号拼接）
        for after_id in item.get("after", []):
            parts = [p.strip() for p in after_id.split(",")]
            for pid in parts:
                if pid and pid not in rule_text_map:
                    rule_text_map[pid] = ""

    # ===== 5. 返回 =====
    return jsonify({
        "project_id": project.id,
        "intermediate_path6": file_path,
        "rules": rules_data,
        "ruleTextMap": rule_text_map
    })


@project_bp.route('/project/<int:project_id>/result', methods=['GET'])
def get_project_result(project_id):
    """
    从数据库的 result_path 读取测试结果 JSON，
    按 rule 维度组织后返回给前端
    """

    # ===== 1. 查询项目 =====
    project = Project.query.get_or_404(project_id)
    file_path = project.result_path

    # ===== 2. 校验路径 =====
    if not file_path:
        return jsonify({"error": "result_path is empty"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # ===== 3. 读取 JSON 文件 =====
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        return jsonify({
            "error": "failed to read json file",
            "detail": str(e)
        }), 500

    # ===== 4. 组织为 rule 分组结构 =====
    groups = []

    for case_list in raw_data:
        if not case_list:
            continue

        rule_id = case_list[0].get("rule")

        groups.append({
            "rule": rule_id,
            "cases": case_list
        })

    # ===== 5. 返回 =====
    return jsonify({
        "project_id": project.id,
        "result_path": file_path,
        "groups": groups
    })


# @project_bp.route('/project/<int:project_id>/rule-filter-graph', methods=['GET'])
# def get_project_rule_filter_graph(project_id):
#     """
#     从 project.intermediate_path6 读取规则中间结果，
#     构建规则前后关系图（nodes + edges）
#     对 before 中的“累计依赖”做一次传递约简，去除冗余边
#     """
#
#     # ===== 1. 查询项目 =====
#     project = Project.query.get_or_404(project_id)
#     file_path = project.intermediate_path6
#
#     # ===== 2. 校验路径 =====
#     if not file_path:
#         return jsonify({"error": "intermediate_path6 is empty"}), 400
#
#     if not os.path.isabs(file_path):
#         return jsonify({"error": "path is not absolute"}), 400
#
#     if not os.path.isfile(file_path):
#         return jsonify({
#             "error": "file not found",
#             "path": file_path
#         }), 404
#
#     # ===== 3. 读取 JSON 文件 =====
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             raw_data = json.load(f)
#     except Exception as e:
#         return jsonify({
#             "error": "failed to read intermediate6 json",
#             "detail": str(e)
#         }), 500
#
#     # ===== 4. 构建规则前后关系图（候选） =====
#     nodes = {}
#     candidate_edges = set()
#
#     def add_node(node_id, node_type, label=None, raw=None):
#         if node_id not in nodes:
#             nodes[node_id] = {
#                 "id": node_id,
#                 "type": node_type,
#                 "label": label or node_id,
#                 "raw": raw
#             }
#
#     def add_candidate_edge(src, tgt):
#         candidate_edges.add((src, tgt))
#
#     def split_path(path):
#         return [p.strip() for p in path.split(',') if p.strip()]
#
#     for item in raw_data:
#         rule_id = item.get("rule")
#         if not rule_id:
#             continue
#
#         # —— 规则节点 ——
#         add_node(
#             node_id=rule_id,
#             node_type="rule",
#             label=item.get("focus", rule_id),
#             raw={
#                 "rule": rule_id,
#                 "focus": item.get("focus"),
#                 "sourceId": item.get("sourceId"),
#                 "text": item.get("text")
#             }
#         )
#
#         # —— before → rule（只加入候选边） ——
#         for b in item.get("before", []):
#             add_node(b, "before")
#             add_candidate_edge(b, rule_id)
#
#         # —— rule → after（支持多级链路） ——
#         for after_path in item.get("after", []):
#             parts = split_path(after_path)
#             prev = rule_id
#             for p in parts:
#                 add_node(p, "after")
#                 add_candidate_edge(prev, p)
#                 prev = p
#
#     # ===== 4.5 过滤传递冗余边（核心修改） =====
#     from collections import defaultdict, deque
#
#     def is_reachable(src, tgt, adj):
#         """
#         判断在不使用 (src -> tgt) 这条边的情况下，
#         src 是否仍然可以到达 tgt
#         """
#         visited = set()
#         queue = deque([src])
#
#         while queue:
#             cur = queue.popleft()
#             for nxt in adj.get(cur, []):
#                 if nxt == tgt:
#                     return True
#                 if nxt not in visited:
#                     visited.add(nxt)
#                     queue.append(nxt)
#         return False
#
#     # 构建邻接表
#     adj = defaultdict(set)
#     for s, t in candidate_edges:
#         adj[s].add(t)
#
#     final_edges = set()
#
#     for s, t in candidate_edges:
#         # 临时移除当前边
#         adj[s].remove(t)
#
#         # 如果移除后不可达，说明这条边是“必要的”
#         if not is_reachable(s, t, adj):
#             final_edges.add((s, t))
#
#         # 加回去
#         adj[s].add(t)
#
#     # ===== 5. 返回 =====
#     return jsonify({
#         "project_id": project.id,
#         "intermediate_path6": file_path,
#         "graph": {
#             "nodes": list(nodes.values()),
#             "edges": [
#                 {"source": s, "target": t}
#                 for s, t in final_edges
#             ]
#         }
#     })


# {
#   "project_id": 12,
#   "intermediate_path6": "/abs/path/intermediate6.json",
#   "graph": {
#     "nodes": [
#       {
#         "id": "2.2.1.1.1.1.1",
#         "type": "rule",
#         "label": "订单连续性操作"
#       }
#     ],
#     "edges": [
#       {
#         "source": "3.2.3.1.1.1.1.1",
#         "target": "2.2.1.1.1.1.1"
#       }
#     ]
#   }
# }

@project_bp.route('/project/<int:project_id>/rule-filter-graph', methods=['POST'])
def get_project_rule_filter_graph(project_id):
    """
    从 project.intermediate_path6 读取规则中间结果，构建规则级依赖图（nodes + edges）

    特点：
    - 节点 = 规则（不再区分 before / after）
    - before / after 统一转为 规则 → 规则 的边
    - 对累计依赖做传递约简（去冗余边）
    - 支持前端 POST 传筛选节点，只返回相关子图
      且保留筛选节点的直接相连节点
    """

    import os, json
    from collections import defaultdict, deque
    from flask import jsonify, request

    # ===== 1. 查询项目 =====
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path6

    # ===== 2. 校验路径 =====
    if not file_path:
        return jsonify({"error": "intermediate_path6 is empty"}), 400
    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400
    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # ===== 3. 读取 JSON 文件 =====
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        return jsonify({"error": "failed to read intermediate6 json", "detail": str(e)}), 500

    # ===== 3.5 读取前端筛选条件（POST JSON） =====
    payload = request.get_json(silent=True) or {}
    selected_nodes = set(payload.get("nodes", []))

    # ===== 4. 构建规则级候选图 =====
    nodes = {}
    candidate_edges = set()

    def add_rule(rule_id, item=None):
        """添加规则节点"""
        if rule_id not in nodes:
            nodes[rule_id] = {
                "id": rule_id,
                "type": "rule",
                "label": rule_id,
                "raw": item.get("text", rule_id) if item else rule_id
            }

    def add_edge(src, tgt):
        if src != tgt:
            candidate_edges.add((src, tgt))

    def split_path(path):
        return [p.strip() for p in path.split(',') if p.strip()]

    for item in raw_data:
        rule_id = item.get("rule")
        if not rule_id:
            continue

        # 当前规则节点
        add_rule(rule_id, {
            "rule": rule_id,
            "focus": item.get("focus"),
            "sourceId": item.get("sourceId"),
            "text": item.get("text")
        })

        # before → rule
        for b in item.get("before", []):
            add_rule(b)
            add_edge(b, rule_id)

        # rule → after（只取最终规则）
        for after_path in item.get("after", []):
            parts = split_path(after_path)
            if parts:
                target = parts[-1]
                add_rule(target)
                add_edge(rule_id, target)

    # ===== 5. 传递约简（去冗余边） =====
    def is_reachable(src, tgt, adj):
        visited = set()
        queue = deque([src])
        while queue:
            cur = queue.popleft()
            for nxt in adj.get(cur, []):
                if nxt == tgt:
                    return True
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return False

    adj = defaultdict(set)
    for s, t in candidate_edges:
        adj[s].add(t)

    final_edges = set()
    for s, t in candidate_edges:
        # ===== 如果边与筛选节点相连，强制保留 =====
        if selected_nodes and (s in selected_nodes or t in selected_nodes):
            final_edges.add((s, t))
            continue

        adj[s].remove(t)
        if not is_reachable(s, t, adj):
            final_edges.add((s, t))
        adj[s].add(t)

    # ===== 6. 子图裁剪（只保留筛选节点及直接相连节点） =====
    if selected_nodes:
        related_nodes = set(selected_nodes)
        related_edges = set()
        for s, t in final_edges:
            if s in selected_nodes or t in selected_nodes:
                related_edges.add((s, t))
                related_nodes.add(s)
                related_nodes.add(t)
        nodes = {k: v for k, v in nodes.items() if k in related_nodes}
        final_edges = related_edges

    # ===== 7. 返回 =====
    return jsonify({
        "project_id": project.id,
        "intermediate_path6": file_path,
        # "filter": list(selected_nodes),
        "graph": {
            "nodes": list(nodes.values()),
            "edges": [{"source": s, "target": t} for s, t in final_edges]
        }
    })


@project_bp.route('/project/<int:project_id>/trace-rule', methods=['POST'])
def trace_rule(project_id):
    """
    追踪某条规则在多个中间文件中的衍生关系，每一步只和上一层直接衍生节点关联。
    前端传 JSON：
    {
        "rule_id": "2.2.1",
        "paths": [
            "intermediate_path3",
            "intermediate_path4",
            "intermediate_path5",
            "intermediate_path6"
        ]
    }
    返回 ECharts graph 格式：
    {
        "nodes": [...],
        "links": [{"source": ..., "target": ...}]
    }
    """
    import os, json

    project = Project.query.get_or_404(project_id)
    payload = request.get_json(silent=True) or {}
    rule_id = payload.get("rule_id")
    paths = payload.get("paths", [])

    if not rule_id or not paths:
        return jsonify({"error": "rule_id or paths missing"}), 400

    nodes = {}
    links = []

    # 每个文件对应父节点长度（固定值）
    parent_len_map = {
        "intermediate_path3": None,  # 根节点，没有父节点
        "intermediate_path4": 3,     # 4位ID父节点前3位
        "intermediate_path5": 4,     # 6位ID父节点前4位
        "intermediate_path6": 6,     # 7+位ID父节点前6位
    }

    for file_attr in paths:
        file_path = getattr(project, file_attr, None)
        if not file_path or not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        # 当前层节点集合
        current_ids = []

        # 文件可能是 list 或 dict
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "rules" in data:
            items = data["rules"]
        else:
            items = []

        for item in items:
            nid = item.get("id") or item.get("rule")
            if not nid or not nid.startswith(rule_id[:3]):
                continue
            nodes[nid] = {
                "id": nid,
                "label": nid,
                "text": item.get("text", nid)
            }
            current_ids.append(nid)

        parent_len = parent_len_map.get(file_attr)
        if parent_len is None:
            continue  # 根节点层

        # 构建上一层 → 当前层的边
        for nid in current_ids:
            parent_id = ".".join(nid.split(".")[:parent_len])
            if parent_id not in nodes:
                # 父节点可能还没加入，先创建
                nodes[parent_id] = {"id": parent_id, "label": parent_id, "text": parent_id}
            links.append({"source": parent_id, "target": nid})

    # 确保起始规则在 nodes 中
    if rule_id not in nodes:
        nodes[rule_id] = {"id": rule_id, "label": rule_id, "text": rule_id}

    return jsonify({
        "project_id": project.id,
        "rule_id": rule_id,
        "graph": {
            "nodes": list(nodes.values()),
            "links": links
        }
    })

