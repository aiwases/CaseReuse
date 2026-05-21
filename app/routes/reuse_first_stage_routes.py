import json
import re
from flask import Blueprint, jsonify
from app.models import Project
import os

reuse_first_stage_bp = Blueprint('reuse_first_stage', __name__, url_prefix='/reuse')


def parse_and_transform_requirements(requirement):
    """
    将单个 requirement 对象解析成结构化格式：
    {
        "id": "3.1.5.1",
        "rule": "3.1.5.1",
        "sourceId": "3.1.5",
        "text": "...",
        "blocks": [
            {
                "name": "rule 1",
                "if": [{"field": ..., "value": ...}],
                "then": [{"field": ..., "value": ...}]
            }
        ]
    }
    """
    rule_id = requirement.get("rule", "")
    source_id = requirement.get("sourceId", "")
    text = requirement.get("text", "")
    
    if_cond_text = ""
    then_cond_text = ""
    
    # 解析文本中的 if/then 条件
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("if "):
            if_cond_text = line[3:].strip()
        elif line.startswith("then "):
            then_cond_text = line[5:].strip()
    
    # 拆分 if 条件
    if_list = []
    if if_cond_text:
        for cond in re.split(r'\s+and\s+', if_cond_text):
            if " is " in cond:
                field, value = cond.split(" is ", 1)
                if_list.append({"field": field.strip(), "value": value.strip()})
    
    # 拆分 then 条件
    then_list = []
    if then_cond_text:
        for cond in re.split(r'\s+and\s+', then_cond_text):
            if " is " in cond:
                field, value = cond.split(" is ", 1)
                then_list.append({"field": field.strip(), "value": value.strip()})
    
    # 生成 block
    blocks_list = []
    if if_list or then_list:
        blocks_list.append({"name": "rule 1", "if": if_list, "then": then_list})
    
    return {
        "id": rule_id,
        "rule": rule_id,
        "sourceId": source_id,
        "text": text,
        "blocks": blocks_list
    }

@reuse_first_stage_bp.route('/<int:project_id>/intermediate1', methods=['GET'])
def get_project_intermediate1(project_id):
    """
{
  "market_variety": {
    "market": "深圳证券交易所",
    "variety": "证券"
  },
  "requirements": [
    {
      "rule": "3.1.5.1",
      "source_id": "3.1.5",
      "blocks": [
        {
          "name": "rule 1",
          "if": [
            {"field": "操作对象", "value": "本所"},
            {"field": "操作", "value": "上市交易"},
            {"field": "交易品种", "value": "债券"}
          ],
          "then": [
            {"field": "交易类型", "value": "当日回转交易"}
          ]
        }
      ]
    }
  ],
  "rules": [...],
  "sco": [...]
}
    """
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path1

    # 2. 校验路径
    if not file_path:
        return jsonify({"error": "独立需求生成结果文件（旧文档）为空"}), 400

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

    # 转换 requirements
    transformed_requirements = []
    for req in data["data"].get("requirements", []):
        transformed = parse_and_transform_requirements(req)
        transformed_requirements.append(transformed)
    
    data["data"]["requirements"] = transformed_requirements

    return jsonify(data["data"])

@reuse_first_stage_bp.route('/<int:project_id>/intermediate2', methods=['GET'])
def get_project_intermediate2(project_id):
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path2

    # 2. 校验路径
    if not file_path:
        return jsonify({"error": "独立需求生成结果文件（新文档）为空"}), 400

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

    # 转换 requirements
    transformed_requirements = []
    for req in data["data"].get("requirements", []):
        transformed = parse_and_transform_requirements(req)
        transformed_requirements.append(transformed)
    
    data["data"]["requirements"] = transformed_requirements

    return jsonify(data["data"])


@reuse_first_stage_bp.route('/<int:project_id>/intermediate3', methods=['GET'])
def get_project_intermediate3(project_id):
    """
    {
        "scenarios": [
            {
                "id": "S1",
                "requirements": [
                    {
                        "id": "第二节.1.1",
                        "text": "",
                        "blocks": [
                            {
                                "name": "rule 第二节.1.1",
                                "if": [{"field": "交易市场", "value": "深圳证券交易所"},
                                       {"field": "交易方向", "value": "买入"}],
                                "then": [{"field": "操作", "value": "成功"}]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)

    file_path = project.intermediate_path3

    # 2. 校验路径
    if not file_path:
        return jsonify({"error": "测试场景合成结果文件（旧文档）为空"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # 3. 读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({
            "error": "failed to read json file",
            "detail": str(e)
        }), 500

    # 转换 scenarios
    transformed_requirements = []
    for scenario in data["data"].get("scenarios", []):
        transformed = parse_and_transform_requirements(scenario)
        transformed_requirements.append(transformed)
    
    frontend_data = {
        "scenarios": transformed_requirements
    }

    # # 获取项目文件夹路径
    # project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # project_folder = os.path.join(project_root, "projects", f"project_{project_id}")
    
    # # 确保项目文件夹存在
    # os.makedirs(project_folder, exist_ok=True)
    
    # # 保存转换后的结果到 JSON 文件
    # output_file = os.path.join(project_folder, "3_out_transformed.json")
    # try:
    #     with open(output_file, 'w', encoding='utf-8') as f:
    #         json.dump(frontend_data, f, ensure_ascii=False, indent=2)
    # except Exception as e:
    #     return jsonify({
    #         "error": "failed to write json file",
    #         "detail": str(e)
    #     }), 500

    # 返回给前端
    return jsonify(frontend_data)


@reuse_first_stage_bp.route('/<int:project_id>/new_test_scenarios', methods=['GET'])
def get_project_new_test_scenarios(project_id):
    """
    {
        "scenarios": [
            {
                "id": "S1",
                "requirements": [
                    {
                        "id": "第二节.1.1",
                        "text": "",
                        "blocks": [
                            {
                                "name": "rule 第二节.1.1",
                                "if": [{"field": "交易市场", "value": "深圳证券交易所"},
                                       {"field": "交易方向", "value": "买入"}],
                                "then": [{"field": "操作", "value": "成功"}]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    # 1. 查询项目
    project = Project.query.get_or_404(project_id)

    file_path = project.new_test_scenarios_path

    # 2. 校验路径
    if not file_path:
        return jsonify({"error": "测试场景合成结果文件（新文档）为空"}), 400

    if not os.path.isabs(file_path):
        return jsonify({"error": "path is not absolute"}), 400

    if not os.path.isfile(file_path):
        return jsonify({"error": "file not found", "path": file_path}), 404

    # 3. 读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({
            "error": "failed to read json file",
            "detail": str(e)
        }), 500

    # 转换 scenarios
    transformed_requirements = []
    for scenario in data["data"].get("scenarios", []):
        transformed = parse_and_transform_requirements(scenario)
        transformed_requirements.append(transformed)
    
    frontend_data = {
        "scenarios": transformed_requirements
    }

    # 返回给前端
    return jsonify(frontend_data)


def relation_to_nodes_links(relation_dict):
    """
    将 relation 字典转换为 nodes + links 结构（不带 category）

    relation_dict 格式示例：
    {
        "3.1.5": ["3.1.5.9.1_2", "3.3.13.5.2_1"],
        "3.2.6": ["3.2.6.1.2.1_1", "第二节.1.2_1"]
    }
    """
    nodes = {}
    links = []

    # 遍历 relation 字典
    for parent, children in relation_dict.items():
        # 添加父节点
        if parent not in nodes:
            nodes[parent] = {"id": parent, "name": parent}
        # 遍历子节点
        for child in children:
            if child not in nodes:
                nodes[child] = {"id": child, "name": child}
            links.append({"source": parent, "target": child})

    # 输出结构
    return {
        "nodes": list(nodes.values()),
        "links": links
    }

@reuse_first_stage_bp.route('/<int:project_id>/intermediate4', methods=['GET'])
def get_project_intermediate4(project_id):
    """{
  "nodes": [
    { "id": "3.1.5", "name": "3.1.5" },
    { "id": "3.1.5.9.1_2", "name": "3.1.5.9.1_2" },
    { "id": "3.3.13.5.2_1", "name": "3.3.13.5.2_1" },
    { "id": "3.1.5.2.2_1", "name": "3.1.5.2.2_1" },
    { "id": "3.2.6", "name": "3.2.6" },
    { "id": "3.2.6.1.2.1_1", "name": "3.2.6.1.2.1_1" },
    { "id": "第二节.1.2_1", "name": "第二节.1.2_1" }
  ],
  "links": [
    { "source": "3.1.5", "target": "3.1.5.9.1_2" },
    { "source": "3.1.5", "target": "3.3.13.5.2_1" },
    { "source": "3.1.5", "target": "3.1.5.2.2_1" },
    { "source": "3.2.6", "target": "3.2.6.1.2.1_1" },
    { "source": "3.2.6", "target": "第二节.1.2_1" }
  ]
}"""
    project = Project.query.get_or_404(project_id)
    file_path = project.intermediate_path4

    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "场景-测试用例对齐结果文件无效或不存在"}), 400

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    re = relation_to_nodes_links(raw["data"]["relation"])

    return jsonify(re)
