import time
import shutil

from flask import Blueprint, session, jsonify, send_file
from app.models import Project
import os

reuse_bp = Blueprint('reuse', __name__, url_prefix='/reuse')

def background_process_reuse_full(app, project_id):
    """
    全流程模式：顺序执行所有必需的任务（task1(old/new) → task2(old/new) → task3 → task4 → task5 → task6）。
    若某一步缺少前置输入且无法执行，将直接失败并返回原因。
    """
    from app import db
    from app.models import Project
    from app.services.task_reuse_test import task1, task2, task3, task4, task5, task6
    from datetime import datetime
    import traceback
    
    def is_file_ready(path: str | None) -> bool:
        return bool(path) and os.path.isfile(path)
    
    # 全流程任务序列（包含 task1/task2 的新旧文档分支）
    full_task_plan = [
        (1, "old"),
        (1, "new"),
        (2, "old"),
        (2, "new"),
        (3, None),
        (4, None),
        (5, None),
        (6, None),
    ]

    output_field_map = {
        (1, "old"): "intermediate_path1",
        (1, "new"): "intermediate_path2",
        (2, "old"): "intermediate_path3",
        (2, "new"): "new_test_scenarios_path",
        (3, None): "intermediate_path4",
        (4, None): "intermediate_path5",
        (5, None): "intermediate_path6",
        (6, None): "result_path",
    }

    required_fields_map = {
        (1, "old"): ["__old_upload__"],
        (1, "new"): ["new_document_path"],
        (2, "old"): ["intermediate_path1"],
        (2, "new"): ["intermediate_path2"],
        (3, None): ["intermediate_path3", "old_test_case_path"],
        (4, None): ["intermediate_path1", "intermediate_path2", "intermediate_path3", "new_test_scenarios_path"],
        (5, None): ["intermediate_path3", "intermediate_path4", "intermediate_path5"],
        (6, None): ["intermediate_path2", "intermediate_path3", "intermediate_path4", "old_test_case_path"],
    }

    field_producer_task = {
        "intermediate_path1": 1,
        "intermediate_path2": 1,
        "intermediate_path3": 2,
        "new_test_scenarios_path": 2,
        "intermediate_path4": 3,
        "intermediate_path5": 4,
        "intermediate_path6": 5,
        "result_path": 6,
        "new_document_path": 1,
        "old_test_case_path": 3,
    }
    
    with app.app_context():
        project = Project.query.get(project_id)
        if not project:
            print(f"[后台任务] 项目 {project_id} 不存在")
            return
        
        try:
            project_folder = os.path.join(
                app.config['PROJECT_FOLDER'], f"project_{project_id}"
            )
            os.makedirs(project_folder, exist_ok=True)
            
            log_lines = [
                f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 全流程模式启动"
            ]
            
            def fail_and_commit(message: str):
                project.log_info = (project.log_info or "") + "\n".join(log_lines + [f"[失败] {message}"]) + "\n"
                project.is_running = False
                project.status = "failed"
                db.session.commit()
            
            # 逐个执行任务
            for target_task, document_type in full_task_plan:
                print(f"准备执行 task{target_task}，document_type={document_type}")
                plan_key = (target_task, document_type)
                output_field_name = output_field_map.get(plan_key)
                if not output_field_name:
                    continue
                task_label = f"task{target_task}" if document_type is None else f"task{target_task}-{document_type}"
                
                # 全流程强制重跑：不因已有输出而跳过
                log_lines.append(f"[{task_label}] 全量重跑（忽略已有输出）")
                
                # 检查前置条件
                required_fields = required_fields_map.get(plan_key, [])
                missing_messages = []
                
                for f in required_fields:
                    if f == "__old_upload__":
                        upload_path = project.upload_path
                        if not is_file_ready(upload_path):
                            missing_messages.append("缺少旧文档上传文件（请先完成上传）")
                        continue

                    path_value = getattr(project, f, None)
                    if not is_file_ready(path_value):
                        producer = field_producer_task.get(f)
                        if producer:
                            missing_messages.append(f"缺少 {f}（需要任务{producer}生成）")
                        else:
                            missing_messages.append(f"缺少 {f}")
                
                if missing_messages:
                    fail_and_commit(f"{task_label} 前置条件不满足：" + "；".join(missing_messages))
                    return
                
                # 执行任务
                start_time = time.time()
                start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                out_path = None
                task_logs = []
                status = "failed"
                
                try:
                    if target_task == 1:
                        input_doc_path = project.upload_path if document_type == "old" else project.new_document_path
                        out_path, task_logs, status = task1(
                            document_type,
                            # input_doc_path,
                            project_folder
                        )
                    elif target_task == 2:
                        task2_input = project.intermediate_path1 if document_type == "old" else project.intermediate_path2
                        out_path, task_logs, status = task2(
                            task2_input,
                            project_folder,
                            document_type
                        )
                    elif target_task == 3:
                        out_path, task_logs, status = task3(
                            project.intermediate_path3,
                            project_folder,
                            project.old_test_case_path,
                        )
                    elif target_task == 4:
                        out_path, task_logs, status = task4(
                            project.intermediate_path1,
                            project.intermediate_path2,
                            project.intermediate_path3,
                            project.new_test_scenarios_path,
                            project_folder
                        )
                    elif target_task == 5:
                        out_path, task_logs, status = task5(
                            project.intermediate_path3,
                            project.intermediate_path4,
                            project.intermediate_path5,
                            project_folder
                        )
                    elif target_task == 6:
                        out_path, task_logs, status = task6(
                            project.intermediate_path2,
                            project.new_test_scenarios_path,
                            project.intermediate_path4,
                            project.intermediate_path5,
                            project.old_test_case_path,
                            project_folder
                        )
                    else:
                        log_lines.append(f"[{task_label}] 未知任务")
                        continue

                    # task1/task2 在新文档分支下写固定文件名，会覆盖旧文档结果，这里转存成 *_new.json
                    if status != "failed" and out_path and target_task in (1, 2) and document_type == "new":
                        try:
                            new_filename = "1_out_new.json" if target_task == 1 else "2_out_new.json"
                            new_out_path = os.path.join(project_folder, new_filename)
                            shutil.copyfile(out_path, new_out_path)
                            out_path = new_out_path
                        except Exception as copy_err:
                            fail_and_commit(f"{task_label} 新文档结果转存失败: {copy_err}")
                            return
                    
                    end_time = time.time()
                    end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    elapsed = end_time - start_time
                    
                    log_lines.append(f"[{task_label}] 开始执行时间：{start_str}")
                    log_lines.extend(task_logs)
                    
                    if status == "failed" or not out_path:
                        log_lines.append(f"[{task_label}] 执行失败，未生成输出文件")
                        # 任务失败，停止整个流程
                        fail_and_commit(f"{task_label} 执行失败")
                        return
                    else:
                        log_lines.append(f"[{task_label}完成] {out_path}")
                        log_lines.append(f"[{task_label}结束时间] {end_str}")
                        log_lines.append(f"[{task_label}耗时] {elapsed:.2f} 秒")
                        setattr(project, output_field_name, out_path)
                        
                except Exception as e:
                    log_lines.append(f"[{task_label}] 执行异常：{str(e)}")
                    fail_and_commit(f"{task_label} 执行异常")
                    return
            
            # 所有任务完成
            project.log_info = (project.log_info or "") + "\n".join(log_lines) + "\n"
            project.is_running = False
            project.status = "completed"
            project.reuse_status = "Completed"
            project.completed_at = datetime.now()
            db.session.commit()
            
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            project = Project.query.get(project_id)
            if project:
                project.status = "failed"
                project.is_running = False
                db.session.commit()
            print(f"[后台任务] 全流程项目 {project_id} 处理失败：{e}")

def background_process_reuse(app, project_id, stage_index, page_type):
    """
    只运行单个任务（根据 pageType + stage_index 映射到 task1~task6）。
    若任务前置条件不满足（例如运行 task4 但 task1 的 intermediate_path1 不存在），
    则直接失败并告知缺少哪些任务。
    """
    from app import db
    from app.models import Project
    from app.services.task_reuse_test import task1, task2, task3, task4, task5, task6
    from datetime import datetime
    import os, traceback, time

    def is_file_ready(path: str | None) -> bool:
        return bool(path) and os.path.isfile(path)
    print("stage_index", stage_index)
    print("page_type", page_type)
    print("project_id", project_id)
    with app.app_context():
        project = Project.query.get(project_id)
        if not project:
            print(f"[后台任务] 项目 {project_id} 不存在")
            return

        try:
            project_folder = os.path.join(
                app.config['PROJECT_FOLDER'], f"project_{project_id}"
            )
            os.makedirs(project_folder, exist_ok=True)

            log_lines = [
                f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Reuse任务开始执行，page_type={page_type}，stage_index={stage_index}"
            ]

            def fail_and_commit(message: str):
                # 把失败原因写入日志，前端可通过进度接口读取 status/reuse_status/log_info（如已实现）
                project.log_info = (project.log_info or "") + "\n".join(log_lines + [f"[失败] {message}"]) + "\n"
                project.is_running = False
                project.status = "failed"
                db.session.commit()

            # 只运行一个目标 task（完全由前端 pageType + stageIndex 决定）
            # tuple: (task_no, document_type)
            # document_type 仅用于 task1/task2，分别区分 old/new 文档执行
            if page_type == "dependency-modeling":
                task_plan_map = {
                    0: (1, "old"),  # 原文档（旧） + 独立需求生成
                    1: (2, "old"),  # 独立需求（旧） + 测试场景合成
                    2: (3, None),    # 场景-测试用例对齐关系图
                }
                status_map = {0: "stage1", 1: "stage2", 2: "stage3"}
            elif page_type == "effect-aware-reuse":
                task_plan_map = {
                    0: (1, "old"),  # 原文档（旧） + 独立需求生成
                    1: (1, "new"),  # 原文档（新） + 独立需求生成
                    2: (2, "old"),  # 独立需求（旧） + 测试场景合成
                    3: (2, "new"),  # 独立需求（新） + 测试场景合成
                    4: (4, None),    # 监管变更识别结果
                    5: (5, None),    # 级联影响范围分析结果
                    6: (6, None),    # 级联影响范围分析 + 测试套件重用与更新
                }
                status_map = {
                    0: "stage1",
                    1: "stage2",
                    2: "stage3",
                    3: "stage4",
                    4: "stage5",
                    5: "stage5",
                    6: "completed",
                }
            else:
                fail_and_commit("pageType 无效")
                return

            if stage_index not in task_plan_map:
                fail_and_commit("stageIndex 无效，无法确定任务")
                return

            target_task, document_type = task_plan_map[stage_index]
            target_status = status_map[stage_index]
            reuse_status_map = {
                5: "Step5_Done",
                6: "Completed",
            }

            # 若目标输出文件已存在，直接标记状态并返回
            if target_task == 1:
                output_field = "intermediate_path1" if document_type == "old" else "intermediate_path2"
            elif target_task == 2:
                output_field = "intermediate_path3" if document_type == "old" else "new_test_scenarios_path"
            else:
                output_field = {
                    3: "intermediate_path4",
                    4: "intermediate_path5",
                    5: "intermediate_path6",
                    6: "result_path",
                }[target_task]

            if is_file_ready(getattr(project, output_field, None)):
                project.is_running = False
                project.status = target_status
                if target_task in reuse_status_map:
                    project.reuse_status = reuse_status_map[target_task]
                if target_status == "completed":
                    project.completed_at = datetime.now()
                project.log_info = (project.log_info or "") + "\n".join(log_lines + ["[跳过] 目标输出已存在，未重复运行任务"]) + "\n"
                db.session.commit()
                return

            # 任务前置字段（只检查一次需要的输入）
            # missing_fields 中每个 field 对应的前置任务为其“生成者”
            field_producer_task = {
                "intermediate_path1": 1,
                "intermediate_path2": 2,
                "intermediate_path3": 3,
                "intermediate_path4": 4,
                "intermediate_path5": 5,
                "intermediate_path6": 6,
                "new_document_path": 1,
                "new_test_scenarios_path": 1,
                "old_test_case_path": 3,
            }

            if target_task == 1:
                required_fields = ["__old_upload__"] if document_type == "old" else ["new_document_path"]
            elif target_task == 2:
                required_fields = ["intermediate_path1"] if document_type == "old" else ["intermediate_path2"]
            elif target_task == 3:
                required_fields = ["intermediate_path3", "old_test_case_path"]
            elif target_task == 4:
                required_fields = ["intermediate_path1", "intermediate_path2", "intermediate_path3", "new_test_scenarios_path"]
            elif target_task == 5:
                required_fields = ["intermediate_path3", "intermediate_path4", "intermediate_path5"]
            elif target_task == 6:
                required_fields = ["intermediate_path2", "intermediate_path3", "intermediate_path4", "old_test_case_path"]
            else:
                fail_and_commit(f"未知 target_task: {target_task}")
                return

            missing_messages = []

            # 检查上传文件
            if required_fields == ["__old_upload__"]:
                upload_path = project.upload_path
                if not is_file_ready(upload_path):
                    missing_messages.append("缺少上传文件（请先完成上传）")
            else:
                for f in required_fields:
                    path_value = getattr(project, f, None)
                    if not is_file_ready(path_value):
                        producer = field_producer_task.get(f)
                        if producer:
                            missing_messages.append(f"缺少 {f}（请先运行任务{producer}）")
                        else:
                            missing_messages.append(f"缺少 {f}")

            if missing_messages:
                fail_and_commit("前置条件不满足：" + "、".join(missing_messages))
                return

            # =========================
            # 执行目标任务
            # =========================
            start_time = time.time()
            start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if target_task == 1:
                input_doc_path = project.upload_path if document_type == "old" else project.new_document_path
                out_path, task_logs, status = task1(
                    document_type,
                    project_folder
                )
            elif target_task == 2:
                task2_input = project.intermediate_path1 if document_type == "old" else project.intermediate_path2
                out_path, task_logs, status = task2(
                    task2_input,
                    project_folder,
                    document_type
                )
            elif target_task == 3:
                out_path, task_logs, status = task3(
                    project.intermediate_path3,
                    project_folder,
                    project.old_test_case_path,
                )
            elif target_task == 4:
                out_path, task_logs, status = task4(
                    project.intermediate_path1,
                    project.intermediate_path2,
                    project.intermediate_path3,
                    project.new_test_scenarios_path,
                    project_folder
                )
            elif target_task == 5:
                out_path, task_logs, status = task5(
                    project.intermediate_path3,
                    project.intermediate_path4,
                    project.intermediate_path5,
                    project_folder
                )
            elif target_task == 6:
                out_path, task_logs, status = task6(
                    project.intermediate_path2,
                    project.new_test_scenarios_path,
                    project.intermediate_path4,
                    project.intermediate_path5,
                    project.old_test_case_path,
                    project_folder
                )
            else:
                fail_and_commit(f"未知 target_task: {target_task}")
                return

            # task1/task2 在新文档分支下，必要时转存成 *_new.json
            if status != "failed" and out_path and target_task in (1, 2) and document_type == "new":
                try:
                    new_filename = "1_out_new.json" if target_task == 1 else "2_out_new.json"
                    new_out_path = os.path.join(project_folder, new_filename)
                    if os.path.abspath(out_path) != os.path.abspath(new_out_path):
                        shutil.copyfile(out_path, new_out_path)
                    out_path = new_out_path
                except Exception as copy_err:
                    fail_and_commit(f"task{target_task} 新文档结果转存失败: {copy_err}")
                    return

            end_time = time.time()
            end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elapsed = end_time - start_time

            log_lines.append(f"[task{target_task}] 开始执行时间：{start_str}")
            log_lines.extend(task_logs)
            log_lines.append(f"[task{target_task}完成] {out_path}")
            log_lines.append(f"[task{target_task}结束时间] {end_str}")
            log_lines.append(f"[task{target_task}耗时] {elapsed:.2f} 秒")

            if status == "failed" or not out_path:
                fail_and_commit(f"task{target_task} 执行失败，未生成输出文件")
                return

            setattr(project, output_field, out_path)
            project.log_info = (project.log_info or "") + "\n".join(log_lines) + "\n"
            project.is_running = False
            project.status = target_status
            if target_task in reuse_status_map:
                project.reuse_status = reuse_status_map[target_task]
            if target_status == "completed":
                project.completed_at = datetime.now()

            db.session.commit()
            return

        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            project = Project.query.get(project_id)
            if project:
                project.status = "failed"
                project.is_running = False
                db.session.commit()
            print(f"[后台任务] Reuse项目 {project_id} 处理失败：{e}")

@reuse_bp.route('/start/<int:project_id>', methods=['POST'])
def start_project(project_id):
    from threading import Thread
    from app import create_app, db
    from app.models import Project
    from datetime import datetime
    from flask import request
    import os

    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_id = session['user_id']
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"success": False, "message": "项目不存在或无权限"}), 404

    # 检查 is_running 状态
    if project.is_running:
        return jsonify({
            "success": False,
            "message": "该项目正在运行中，请稍后再试。"
        }), 400

    try:
        # 更新为正在运行
        # project.is_running = True
        project.started_at = datetime.now()
        db.session.commit()

        # 创建 app context
        app = create_app()

        if project.process_type == "reuse":

            # 从前端获取参数，按 pageType + stage 直接决定执行任务
            data = request.get_json(silent=True) or {}
            stage_raw = data.get("stage")
            page_type = data.get("pageType")
            run_all = bool(data.get("runAll"))

            # 首页/文档详情页通常不带 stage/pageType，默认按全流程执行
            if run_all or stage_raw is None:
                def is_file_ready(path: str | None) -> bool:
                    return bool(path) and os.path.isfile(path)

                old_doc_path = project.upload_path
                new_doc_path = project.new_document_path
                old_test_case_path = project.old_test_case_path

                missing_inputs = []
                if not is_file_ready(old_doc_path):
                    missing_inputs.append("旧文档")
                if not is_file_ready(new_doc_path):
                    missing_inputs.append("新文档")
                if not is_file_ready(old_test_case_path):
                    missing_inputs.append("旧测试用例")

                if missing_inputs:
                    project.is_running = False
                    db.session.commit()
                    return jsonify({
                        "success": False,
                        "message": "自动执行前置检查失败，缺少：" + "、".join(missing_inputs)
                    }), 400

                t = Thread(
                    target=background_process_reuse_full,
                    args=(app, project.id)
                )
            else:
                if page_type not in ["dependency-modeling", "effect-aware-reuse"]:
                    project.is_running = False
                    db.session.commit()
                    return jsonify({
                        "success": False,
                        "message": "pageType 无效，允许值：dependency-modeling 或 effect-aware-reuse"
                    }), 400

                # 前端 stage 是 0-based，这里兼容 1-based 和 stageX/taskX 字符串
                # 解析 stage -> stage_num
                if isinstance(stage_raw, (int, float)):
                    if isinstance(stage_raw, float) and not stage_raw.is_integer():
                        project.is_running = False
                        db.session.commit()
                        return jsonify({"success": False, "message": "stage 必须是整数"}), 400
                    stage_num = int(stage_raw)
                else:
                    stage_str = str(stage_raw).strip().lower()
                    if stage_str.startswith("stage") and stage_str[5:].isdigit():
                        stage_num = int(stage_str[5:])
                    elif stage_str.startswith("task") and stage_str[4:].isdigit():
                        stage_num = int(stage_str[4:])
                    elif stage_str.isdigit():
                        stage_num = int(stage_str)
                    else:
                        project.is_running = False
                        db.session.commit()
                        return jsonify({"success": False, "message": "stage 无效，必须是整数或 stageX"}), 400

                if page_type == "dependency-modeling":
                    # stage_index: 0..2
                    valid_zero = (0, 2)
                    valid_one = (1, 3)
                else:
                    # stage_index: 0..6
                    valid_zero = (0, 6)
                    valid_one = (1, 7)

                if valid_zero[0] <= stage_num <= valid_zero[1]:
                    stage_index = stage_num
                elif valid_one[0] <= stage_num <= valid_one[1]:
                    stage_index = stage_num - 1
                else:
                    project.is_running = False
                    db.session.commit()
                    return jsonify({
                        "success": False,
                        "message": f"stage 无效：pageType={page_type}，允许范围 {valid_zero[0]}..{valid_zero[1]}（或 {valid_one[0]}..{valid_one[1]} 1-based）"
                    }), 400

                # =========================
                # 同步校验前置条件：不满足则直接返回给前端
                # =========================
                def is_file_ready(path: str | None) -> bool:
                    return bool(path) and os.path.isfile(path)

                if page_type == "dependency-modeling":
                    task_plan_map = {
                        0: (1, "old"),
                        1: (2, "old"),
                        2: (3, None),
                    }
                else:
                    task_plan_map = {
                        0: (1, "old"),
                        1: (1, "new"),
                        2: (2, "old"),
                        3: (2, "new"),
                        4: (4, None),
                        5: (5, None),
                        6: (6, None),
                    }

                if stage_index not in task_plan_map:
                    project.is_running = False
                    db.session.commit()
                    return jsonify({
                        "success": False,
                        "message": "stageIndex 无效，无法确定任务"
                    }), 400

                target_task, document_type = task_plan_map[stage_index]

                if target_task == 1:
                    required_fields = ["__old_upload__"] if document_type == "old" else ["new_document_path"]
                elif target_task == 2:
                    required_fields = ["intermediate_path1"] if document_type == "old" else ["intermediate_path2"]
                elif target_task == 3:
                    required_fields = ["intermediate_path3", "old_test_case_path"]
                elif target_task == 4:
                    required_fields = ["intermediate_path1", "intermediate_path2", "intermediate_path3", "new_test_scenarios_path"]
                elif target_task == 5:
                    required_fields = ["intermediate_path3", "intermediate_path4", "intermediate_path5"]
                elif target_task == 6:
                    required_fields = ["intermediate_path2", "intermediate_path3", "intermediate_path4", "old_test_case_path"]
                else:
                    required_fields = []

                field_producer_task = {
                    "intermediate_path1": 1,
                    "intermediate_path2": 1,
                    "intermediate_path3": 2,
                    "new_test_scenarios_path": 2,
                    "intermediate_path4": 3,
                    "intermediate_path5": 4,
                    "intermediate_path6": 5,
                    "result_path": 6,
                    "new_document_path": 1,
                    "old_test_case_path": 3,
                }

                missing_tasks = []
                for f in required_fields:
                    if f == "__old_upload__":
                        upload_path = project.upload_path
                        if not is_file_ready(upload_path):
                            missing_tasks.append(1)
                    else:
                        path_value = getattr(project, f, None)
                        if not is_file_ready(path_value):
                            producer = field_producer_task.get(f)
                            if producer and producer not in missing_tasks:
                                missing_tasks.append(producer)

                if missing_tasks:
                    project.is_running = False
                    db.session.commit()
                    return jsonify({
                        "success": False,
                        "message": "前置条件不满足，请先运行任务" + "、".join(str(x) for x in missing_tasks)
                    }), 400

                t = Thread(
                    target=background_process_reuse,
                    args=(app, project.id, stage_index, page_type)
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
    



@reuse_bp.route('/<int:project_id>/progress', methods=['GET'])
def get_project_progress(project_id):
    """
    获取项目进度接口（计算分支状态，整体状态直接读取）
    """
    project = Project.query.get_or_404(project_id)

    # 计算分支 A 状态（2 -> 3）
    if project.intermediate_path4:
        branch_a_status = 'Step3_Done'
    elif project.intermediate_path3:
        branch_a_status = 'Step2_Done'
    elif project.intermediate_path1:
        branch_a_status = 'Step1_old_ready'
    else:
        branch_a_status = 'Ready'

    # 计算分支 B 状态（4）
    if project.intermediate_path5:
        branch_b_status = 'Step4_Done'
    elif project.intermediate_path1 and project.intermediate_path2:
        branch_b_status = 'Step1_all_ready'
    elif project.intermediate_path1:
        branch_b_status = 'Step1_old_ready'
    else:
        branch_b_status = 'Ready'

    # 构建返回数据
    progress_data = {
        'id': project.id,
        'branch_a_status': branch_a_status,
        'branch_b_status': branch_b_status,
        'reuse_status': project.reuse_status,  # 直接从数据库读取
        'is_running': project.is_running,
    }

    return jsonify(progress_data)


@reuse_bp.route('/<int:project_id>/upload_file', methods=['GET'])
def get_project_upload_file(project_id):
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.upload_path

    # 2. 基本校验
    if not file_path:
        return jsonify({"error": "旧文档文件为空，请先上传旧文档"}), 400

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