import json

from flask import Blueprint, request, jsonify
from app.models import Project
import os

reuse_second_stage_bp = Blueprint('reuse_second_stage', __name__, url_prefix='/reuse')


def normalize_regulatory_changes_payload(payload):
    return {
        "delete_rules": payload.get("delete_rules", []) if isinstance(payload, dict) else [],
        "add_rules": payload.get("add_rules", []) if isinstance(payload, dict) else [],
    }


def normalize_cascading_impacts_payload(payload):
    if not isinstance(payload, dict):
        return {
            "to_delete_scenarios": [],
            "to_delete_testcases": []
        }

    scenarios = payload.get("to_delete_scenarios", [])
    testcases = payload.get("to_delete_testcases", [])

    if not isinstance(scenarios, list):
        scenarios = []
    if not isinstance(testcases, list):
        testcases = []

    return {
        "to_delete_scenarios": scenarios,
        "to_delete_testcases": testcases
    }


def normalize_test_suite_reuse_payload(payload):
    if not isinstance(payload, dict):
        return {"testcases": []}

    raw_testcases = payload.get("testcases", [])
    if not isinstance(raw_testcases, list):
        return {"testcases": []}

    normalized_groups = []
    for group in raw_testcases:
        if isinstance(group, list):
            normalized_group = [item for item in group if isinstance(item, dict)]
            normalized_groups.append(normalized_group)
        elif isinstance(group, dict):
            normalized_groups.append([group])

    return {"testcases": normalized_groups}


@reuse_second_stage_bp.route('/<int:project_id>/intermediate5', methods=['GET'])
def get_project_intermediate5(project_id):
    # 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path5

    # 校验文件存在
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "监管变更识别结果文件无效或不存在"}), 400

    # 读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        return jsonify({"error": f"failed to read json file: {str(e)}"}), 500

    # 构建规则数据
    data = raw.get("data", {})
    to_add_rules = data.get("to_add_rules", [])
    to_delete_rules = data.get("to_delete_rules", [])

    return jsonify({
        "delete_rules": to_delete_rules,
        "add_rules": to_add_rules
    })


@reuse_second_stage_bp.route('/<int:project_id>/intermediate5', methods=['PUT'])
def update_project_intermediate5(project_id):
    project = Project.query.get_or_404(project_id)

    file_path = project.intermediate_path5
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "监管变更识别结果文件无效或不存在"}), 400

    payload = request.get_json(silent=True) or {}
    normalized = normalize_regulatory_changes_payload(payload)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"error": f"failed to read json file: {str(e)}"}), 500

    if not isinstance(existing_data, dict):
        existing_data = {"code": 200, "data": {}}

    existing_data.setdefault("code", 200)
    existing_data.setdefault("data", {})
    existing_data["data"]["to_delete_rules"] = normalized["delete_rules"]
    existing_data["data"]["to_add_rules"] = normalized["add_rules"]

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"error": f"failed to write json file: {str(e)}"}), 500

    return jsonify({
        "code": 200,
        "msg": "regulatory change identification updated",
        "data": existing_data.get("data", {})
    })


@reuse_second_stage_bp.route('/<int:project_id>/intermediate6', methods=['GET'])
def get_project_intermediate6(project_id):
    """
    读取 intermediate_path6 文件，保留原本的数据结构传给前端
    """

    # ===== 1. 查询项目 =====
    project = Project.query.get_or_404(project_id)

    file_path = project.intermediate_path6

    # ===== 2. 校验路径 =====
    if not file_path:
        return jsonify({"error": "级联影响范围分析结果文件为空"}), 400

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

    # ===== 4. 返回 data 里的数据 =====
    return jsonify(raw_data.get("data", {}))


@reuse_second_stage_bp.route('/<int:project_id>/intermediate6', methods=['PUT'])
def update_project_intermediate6(project_id):
    project = Project.query.get_or_404(project_id)

    file_path = project.intermediate_path6
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "级联影响范围分析结果文件无效或不存在"}), 400

    payload = request.get_json(silent=True) or {}
    normalized = normalize_cascading_impacts_payload(payload)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"error": f"failed to read json file: {str(e)}"}), 500

    if not isinstance(existing_data, dict):
        existing_data = {"code": 200, "data": {}}

    existing_data.setdefault("code", 200)
    existing_data.setdefault("data", {})
    existing_data["data"]["to_delete_scenarios"] = normalized["to_delete_scenarios"]
    existing_data["data"]["to_delete_testcases"] = normalized["to_delete_testcases"]

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"error": f"failed to write json file: {str(e)}"}), 500

    return jsonify({
        "code": 200,
        "msg": "cascading impact scope analysis updated",
        "data": existing_data.get("data", {})
    })


@reuse_second_stage_bp.route('/<int:project_id>/result', methods=['GET'])
def get_project_result(project_id):
    """
    读取 result_path 文件，返回 data 部分的数据
    """

    # ===== 1. 查询项目 =====
    project = Project.query.get_or_404(project_id)
    file_path = project.result_path

    # ===== 2. 校验路径 =====
    if not file_path:
        return jsonify({"error": "测试套件重用与更新结果文件为空"}), 400

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

    # ===== 4. 返回 data 部分的数据 =====
    return jsonify(raw_data.get("data", {}))


@reuse_second_stage_bp.route('/<int:project_id>/result', methods=['PUT'])
def update_project_result(project_id):
    project = Project.query.get_or_404(project_id)

    file_path = project.result_path
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "测试套件重用与更新结果文件无效或不存在"}), 400

    payload = request.get_json(silent=True) or {}
    normalized = normalize_test_suite_reuse_payload(payload)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"error": f"failed to read json file: {str(e)}"}), 500

    if not isinstance(existing_data, dict):
        existing_data = {"code": 200, "data": {}}

    existing_data.setdefault("code", 200)
    existing_data.setdefault("data", {})
    if not isinstance(existing_data.get("data"), dict):
        existing_data["data"] = {}

    existing_data["data"]["testcases"] = normalized["testcases"]

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"error": f"failed to write json file: {str(e)}"}), 500

    return jsonify({
        "code": 200,
        "msg": "test suite reuse update result updated",
        "data": existing_data.get("data", {})
    })

@reuse_second_stage_bp.route('/<int:project_id>/test_case_file', methods=['GET'])
def get_project_test_case_file(project_id):
    project = Project.query.get_or_404(project_id)

    def flatten_records(value):
        if not isinstance(value, list):
            return []
        flattened = []
        for item in value:
            if isinstance(item, dict):
                flattened.append(item)
            elif isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, dict):
                        flattened.append(sub_item)
        return flattened

    def get_list_field(container, key):
        if isinstance(container, dict):
            return flatten_records(container.get(key))
        return []

    def extract_records_from_raw(raw_data):
        if isinstance(raw_data, list):
            return flatten_records(raw_data)

        if isinstance(raw_data, dict):
            nested_data = raw_data.get("data") if isinstance(raw_data.get("data"), dict) else {}
            return (
                get_list_field(raw_data, "old_test_cases")
                or get_list_field(raw_data, "old_testcases")
                or get_list_field(raw_data, "test_cases")
                or get_list_field(raw_data, "testcases")
                or get_list_field(nested_data, "old_test_cases")
                or get_list_field(nested_data, "old_testcases")
                or get_list_field(nested_data, "test_cases")
                or get_list_field(nested_data, "testcases")
            )

        return []

    try:
        candidate_paths = []
        if isinstance(project.old_test_case_path, str) and project.old_test_case_path.strip():
            candidate_paths.append(project.old_test_case_path)

        if isinstance(project.intermediate_path3, str) and project.intermediate_path3.strip():
            project_folder = os.path.dirname(project.intermediate_path3)
            candidate_paths.extend([
                os.path.join(project_folder, "old_testcase.json"),
                os.path.join(project_folder, "oldTestcase.json")
            ])

        # Fallback to conventional project folder even when DB path is stale.
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        project_folder_default = os.path.join(project_root, "projects", f"project_{project_id}")
        candidate_paths.extend([
            os.path.join(project_folder_default, "old_testcase.json"),
            os.path.join(project_folder_default, "oldTestcase.json")
        ])

        # Keep order but remove duplicates.
        unique_paths = []
        for path in candidate_paths:
            if isinstance(path, str) and path and path not in unique_paths:
                unique_paths.append(path)

        existing_paths = [path for path in unique_paths if os.path.isfile(path)]
        if not existing_paths:
            return jsonify({
                "project_id": project_id,
                "source_type": "old_test_case",
                "old_test_cases": [],
                "test_cases": [],
                "source_path": None,
                "warning": "old test case file not found"
            })

        file_path = None
        records = []
        parse_errors = []
        for path in existing_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                extracted = extract_records_from_raw(raw_data)
                if extracted:
                    file_path = path
                    records = extracted
                    break
                if file_path is None:
                    # Keep a parsed fallback path even when data is empty.
                    file_path = path
                    records = extracted
            except Exception as e:
                parse_errors.append(f"{path}: {str(e)}")

        warning = None
        if not records and parse_errors:
            warning = "no usable old test case records found"

        return jsonify({
            "project_id": project_id,
            "source_type": "old_test_case",
            "old_test_cases": records,
            "test_cases": records,
            "source_path": file_path,
            "warning": warning,
        })
    except Exception as e:
        return jsonify({
            "project_id": project_id,
            "source_type": "old_test_case",
            "old_test_cases": [],
            "test_cases": [],
            "source_path": None,
            "warning": f"test case parsing fallback: {str(e)}"
        })
