from flask import Blueprint, request, jsonify
from app.models import Project
import json
import os

reuse_first_stage_edit_bp = Blueprint('reuse_first_stage_edit', __name__, url_prefix='/reuse/first-stage/edit')


def transform_blocks_to_text(blocks):
    """
    将结构化的 blocks 转换回原始文本格式
    blocks 格式: [{"name": "rule 1", "if": [...], "then": [...]}]
    返回格式: "if field1 is value1 and field2 is value2\nthen field3 is value3\n"
    """
    if not blocks:
        return ""
    
    lines = []

    for block in blocks:
        if_list = block.get("if", [])
        then_list = block.get("then", [])

        if_conditions = []
        for cond in if_list:
            if_conditions.append(f"{cond.get('field')} is {cond.get('value')}")

        if if_conditions:
            if_text = "if " + " and ".join(if_conditions)
        else:
            if_text = "if"

        then_conditions = []
        for cond in then_list:
            then_conditions.append(f"{cond.get('field')} is {cond.get('value')}")

        if then_conditions:
            then_text = "then " + " and ".join(then_conditions)
        else:
            then_text = "then"

        lines.extend([if_text, then_text])

    return "\n".join(lines) + "\n"


def normalize_scenario_for_storage(scenario):
    """将前端编辑后的场景对象还原为 2_out.json 的扁平结构。"""
    normalized = {}

    rule_value = scenario.get("rule") or scenario.get("id") or ""
    source_id = scenario.get("sourceId") or scenario.get("source_id") or ""

    if rule_value:
        normalized["rule"] = rule_value
    if source_id:
        normalized["sourceId"] = source_id

    # 兼容历史字段，保留 before / after 等原始关系信息
    for key in ("before", "after"):
        if key in scenario:
            normalized[key] = scenario.get(key)

    text_value = scenario.get("text", "")
    if text_value:
        normalized["text"] = text_value
    elif "blocks" in scenario:
        normalized["text"] = transform_blocks_to_text(scenario.get("blocks", []))
    else:
        normalized["text"] = ""

    return normalized


def normalize_scenarios_payload(data):
    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list):
        return []

    return [normalize_scenario_for_storage(scenario) for scenario in scenarios if isinstance(scenario, dict)]


@reuse_first_stage_edit_bp.route('/<int:project_id>/intermediate1', methods=['PUT'])
def update_intermediate1(project_id):
    """更新 intermediate1 数据"""
    project = Project.query.get_or_404(project_id)
    
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400
    
    # 获取文件路径
    file_path = project.intermediate_path1
    if not file_path or not os.path.exists(file_path):
        return jsonify({"code": 404, "msg": "intermediate1 文件不存在"}), 404
    
    # 读取现有数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"读取文件失败: {str(e)}"}), 500
    
    # 更新数据
    # 直接从 data 中获取 rules 和 requirements，赋值给 existing_data['data']
    if 'rules' in data:
        existing_data['data']['rules'] = data['rules']
    
    if 'requirements' in data:
        # 如果更新的是 requirements，需要将 blocks 转换回 text
        for req in data['requirements']:
            if 'blocks' in req and 'text' not in req:
                req['text'] = transform_blocks_to_text(req['blocks'])
        existing_data['data']['requirements'] = data['requirements']
    
    # 保存更新后的数据
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存文件失败: {str(e)}"}), 500
    
    return jsonify({
        "code": 200,
        "msg": "intermediate1 更新成功",
        "data": {
            "file_path": file_path
        }
    })


@reuse_first_stage_edit_bp.route('/<int:project_id>/intermediate2', methods=['PUT'])
def update_intermediate2(project_id):
    """更新 intermediate2 数据"""
    project = Project.query.get_or_404(project_id)
    
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400
    
    # 获取文件路径
    file_path = project.intermediate_path2
    if not file_path or not os.path.exists(file_path):
        return jsonify({"code": 404, "msg": "intermediate2 文件不存在"}), 404
    
    # 读取现有数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"读取文件失败: {str(e)}"}), 500
    
    # 更新数据
    # 直接从 data 中获取 rules 和 requirements，赋值给 existing_data['data']
    if 'rules' in data:
        existing_data['data']['rules'] = data['rules']
    
    if 'requirements' in data:
        # 如果更新的是 requirements，需要将 blocks 转换回 text
        for req in data['requirements']:
            if 'blocks' in req and 'text' not in req:
                req['text'] = transform_blocks_to_text(req['blocks'])
        existing_data['data']['requirements'] = data['requirements']
    
    # 保存更新后的数据
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存文件失败: {str(e)}"}), 500
    
    return jsonify({
        "code": 200,
        "msg": "intermediate2 更新成功",
        "data": {
            "file_path": file_path
        }
    })


@reuse_first_stage_edit_bp.route('/<int:project_id>/intermediate3', methods=['PUT'])
def update_intermediate3(project_id):
    """更新 intermediate3 数据"""
    project = Project.query.get_or_404(project_id)
    
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400
    
    # 获取文件路径
    file_path = project.intermediate_path3
    if not file_path or not os.path.exists(file_path):
        return jsonify({"code": 404, "msg": "intermediate3 文件不存在"}), 404
    
    # 读取现有数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"读取文件失败: {str(e)}"}), 500
    # 更新数据
    # 直接从 data 中获取 scenarios，赋值给 existing_data['data']
    if 'scenarios' in data:
        existing_data['data']['scenarios'] = normalize_scenarios_payload(data)
    
    # 保存更新后的数据
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存文件失败: {str(e)}"}), 500
    
    return jsonify({
        "code": 200,
        "msg": "intermediate3 更新成功",
        "data": {
            "file_path": file_path
        }
    })


@reuse_first_stage_edit_bp.route('/<int:project_id>/new_test_scenarios', methods=['PUT'])
def update_new_test_scenarios(project_id):
    """更新 new_test_scenarios 数据"""
    project = Project.query.get_or_404(project_id)
    
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400
    
    # 获取文件路径
    file_path = project.new_test_scenarios_path
    if not file_path or not os.path.exists(file_path):
        return jsonify({"code": 404, "msg": "new_test_scenarios 文件不存在"}), 404
    
    # 读取现有数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"读取文件失败: {str(e)}"}), 500
    
    # 更新数据
    # 直接从 data 中获取 scenarios，赋值给 existing_data['data']
    if 'scenarios' in data:
        existing_data['data']['scenarios'] = normalize_scenarios_payload(data)
    
    # 保存更新后的数据
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存文件失败: {str(e)}"}), 500
    
    return jsonify({
        "code": 200,
        "msg": "new_test_scenarios 更新成功",
        "data": {
            "file_path": file_path
        }
    })


@reuse_first_stage_edit_bp.route('/<int:project_id>/intermediate4', methods=['PUT'])
def update_intermediate4(project_id):
    """更新 intermediate4 数据"""
    project = Project.query.get_or_404(project_id)
    
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400
    
    # 获取文件路径
    file_path = project.intermediate_path4
    if not file_path or not os.path.exists(file_path):
        return jsonify({"code": 404, "msg": "intermediate4 文件不存在"}), 404
    
    # 读取现有数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"读取文件失败: {str(e)}"}), 500
    
    # 更新数据
    # 直接从 data 中获取字段，赋值给 existing_data['data']
    for key in data:
        existing_data['data'][key] = data[key]
    
    # 保存更新后的数据
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存文件失败: {str(e)}"}), 500
    
    return jsonify({
        "code": 200,
        "msg": "intermediate4 更新成功",
        "data": {
            "file_path": file_path
        }
    })
