import json
from flask import Blueprint, jsonify, request
from app.models import Project
from app.services.graph_data.getChange import get_change_rules
from app.services.graph_data.getRule import get_rule_nodes_with_change_type
from app.services.graph_data.getScenarios import get_scenario_nodes
from app.services.graph_data.getTestcase import get_testcase_nodes
import os

reuse_graph_bp = Blueprint('reuse_graph', __name__, url_prefix='/reuse')


@reuse_graph_bp.route('/<int:project_id>/trace-rule', methods=['POST'])
def trace_rule(project_id):
    """
    追踪复用过程中规则在多个中间文件中的衍生关系
    
    前端传 JSON：
    {
        "rule_id": "3.1.5",  // 可选，指定特定规则ID
        "paths": [
            "intermediate_path1",   // 旧文档结果
            "intermediate_path2",   // 新文档结果
            "intermediate_path3",   // 旧文档测试场景合成结果
            "new_test_scenarios_path" // 新文档测试场景合成结果
        ]
    }
    
    返回 ECharts graph 格式：
    {
        "project_id": 74,
        "rule_id": "3.1.5",
        "graph": {
            "nodes": [...],
            "links": [...]
        }
    }
    """
    project = Project.query.get_or_404(project_id)
    payload = request.get_json(silent=True) or {}
    rule_id = payload.get("rule_id")

    paths = ["intermediate_path1", "intermediate_path2", "new_test_scenarios_path", "intermediate_path3", "result_path"]

    nodes = {}
    links = []

    # 获取添加和删除的规则
    change_rules = get_change_rules(project_id)
    add_rules = change_rules.get("add_rules", [])
    delete_rules = change_rules.get("delete_rules", [])

    # 获取规则节点（包含 change_type）
    rule_nodes = get_rule_nodes_with_change_type(project_id, rule_id, add_rules, delete_rules)
    nodes.update(rule_nodes)

    # 获取规则节点的 change_type
    rule_change_type = None
    for node_key, node in rule_nodes.items():
        if rule_id and node.get("id") == rule_id:
            rule_change_type = node.get("change_type")
            break
    
    # 获取场景节点（包含需求节点）
    # 场景和需求节点从 intermediate_path3 和 new_test_scenarios_path 获取
    scenario_nodes, scenario_edges = get_scenario_nodes(project_id, rule_id, rule_change_type)
    nodes.update(scenario_nodes)
    links.extend(scenario_edges)
    
    # 为需求节点构建到规则节点的链接
    for node_key, node in nodes.items():
        if "_requirement" in node_key:
            req_id = node.get("id")
            if req_id:
                # 从需求ID的前3位提取规则ID（如 "3.1.5.1" -> "3.1.5"）
                parts = req_id.split(".")
                if len(parts) >= 4:
                    # 取前3位作为规则ID
                    rule_id_part = ".".join(parts[:3])
                    
                    # 查找对应的规则节点
                    rule_type = "old_rule" if node.get("type") == "old_requirement" else "new_rule"
                    rule_key = f"{rule_id_part}_{rule_type}"
                    
                    # 如果对应的规则类型不存在，尝试另一种规则类型
                    if rule_key not in nodes:
                        other_rule_type = "old_rule" if rule_type == "new_rule" else "new_rule"
                        other_rule_key = f"{rule_id_part}_{other_rule_type}"
                        if other_rule_key in nodes:
                            rule_key = other_rule_key
                    
                    # 创建规则到需求的连接
                    if rule_key in nodes:
                        # 检查规则节点的 change_type
                        rule_node = nodes.get(rule_key)
                        rule_change_type = rule_node.get("change_type")
                        
                        # 如果规则是 unchanged，只处理 new 类型的需求
                        if rule_change_type == "unchanged" and "_old_requirement" in node_key:
                            continue
                        
                        links.append({"source": rule_key, "target": node_key})
    
    # 为场景节点构建到需求节点的链接
    for scenario_key, scenario_node in scenario_nodes.items():
        # 确保场景节点的类型是场景类型
        if "_scenario" not in scenario_key:
            continue
        
        # 场景ID与需求ID相同
        scenario_id = scenario_node.get("id")
        if scenario_id:
            # 提取场景的规则ID（前3位）
            parts = scenario_id.split(".")
            if len(parts) >= 3:
                rule_id_from_scenario = ".".join(parts[:3])
                
                # 检查规则节点是否存在
                rule_key = f"{rule_id_from_scenario}_new_rule"
                if rule_key not in nodes:
                    rule_key = f"{rule_id_from_scenario}_old_rule"
                
                # 检查规则节点的 change_type
                rule_node = nodes.get(rule_key)
                rule_change_type = rule_node.get("change_type") if rule_node else None
                
                # 如果规则是 unchanged，只处理 new 类型的场景节点
                if rule_change_type == "unchanged" and "_old_scenario" in scenario_key:
                    continue
                
                # 查找对应的旧需求节点
                old_req_key = f"{scenario_id}_old_requirement"
                if old_req_key in nodes:
                    # 如果规则是 unchanged，跳过 old 类型的需求
                    if rule_change_type == "unchanged" and "_old_requirement" in old_req_key:
                        continue
                    # 创建需求到场景的连接
                    links.append({"source": old_req_key, "target": scenario_key})
                
                # 查找对应的新需求节点
                new_req_key = f"{scenario_id}_new_requirement"
                if new_req_key in nodes:
                    # 创建需求到场景的连接
                    links.append({"source": new_req_key, "target": scenario_key})

    # 获取测试用例节点
    testcase_nodes = get_testcase_nodes(project_id, rule_id, rule_change_type)
    nodes.update(testcase_nodes)
    
    # 为测试用例节点构建到场景节点的链接
    for testcase_key, testcase_node in testcase_nodes.items():
        testcase_id = testcase_node["id"]
        testcase_type = testcase_node.get("type", "new_testcase")
        
        # 处理测试用例ID，去掉下划线后缀
        pure_id = testcase_id.split("_")[0]
        parts = pure_id.split(".")
        
        if len(parts) >= 5:  # 测试用例节点（7位ID）
            scenario_id = ".".join(parts[:5])
            
            # 提取测试用例的规则ID（前3位）
            rule_id_from_testcase = ".".join(parts[:3])
            
            # 检查规则节点是否存在
            rule_key = f"{rule_id_from_testcase}_new_rule"
            if rule_key not in nodes:
                rule_key = f"{rule_id_from_testcase}_old_rule"
            
            # 检查规则节点的 change_type
            rule_node = nodes.get(rule_key)
            rule_change_type = rule_node.get("change_type") if rule_node else None
            
            # 如果规则是 unchanged，只处理 new 类型的测试用例
            if rule_change_type == "unchanged" and testcase_type == "old_testcase":
                continue
            
            # 先尝试根据测试用例类型确定对应的场景类型
            scenario_type = "old_scenario" if testcase_type == "old_testcase" else "new_scenario"
            parent_key = f"{scenario_id}_{scenario_type}"
            
            # 如果对应的场景类型不存在，根据测试用例类型创建对应的场景节点
            if parent_key not in nodes:
                # 不尝试另一种场景类型，只创建同类型的场景节点
                # 这样可以避免 old_testcase 连接到 new_scenario 的情况
                scenario_type = "new_scenario" if testcase_type == "new_testcase" else "old_scenario"
                parent_key = f"{scenario_id}_{scenario_type}"
                
                if parent_key not in nodes:
                    # 从 new_test_scenarios_path 或 intermediate_path3 中搜索场景信息
                    scenario_text = scenario_id
                    # 确定要搜索的文件路径
                    file_path = None
                    if testcase_type == "new_testcase":
                        file_path = getattr(project, "new_test_scenarios_path", None)
                    else:
                        file_path = getattr(project, "intermediate_path3", None)
                    
                    # 搜索场景信息
                    if file_path and os.path.isfile(file_path):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            # 从 data.scenarios 或 data.data.scenarios 读取
                            scenarios = data.get("scenarios", [])
                            if not scenarios:
                                scenarios = data.get("data", {}).get("scenarios", [])
                            # 查找与场景ID匹配的需求
                            for scenario in scenarios:
                                req_id = scenario.get("rule") or scenario.get("id")
                                if req_id == scenario_id:
                                    # 收集所有相关需求的ID
                                    related_requirements = [req_id]
                                    # 添加 before 中的需求
                                    if "before" in scenario and scenario.get("before"):
                                        before_req_id = scenario.get("before")
                                        if isinstance(before_req_id, list):
                                            related_requirements.extend(before_req_id)
                                        else:
                                            related_requirements.append(before_req_id)
                                    # 添加 after 中的需求
                                    if "after" in scenario and scenario.get("after"):
                                        after_req_id = scenario.get("after")
                                        if isinstance(after_req_id, list):
                                            related_requirements.extend(after_req_id)
                                        else:
                                            related_requirements.append(after_req_id)
                                    scenario_text = ", ".join(related_requirements)
                                    break
                        except Exception as e:
                            print(f"读取场景文件失败: {str(e)}")
                    
                    # 创建场景节点
                    # 获取测试用例的 change_type
                    testcase_change_type = testcase_node.get("change_type", "add")
                    
                    nodes[parent_key] = {
                        "id": scenario_id, 
                        "label": scenario_id, 
                        "text": scenario_text, 
                        "type": scenario_type,
                        "change_type": testcase_change_type
                    }
                    
                    # 查找对应的需求节点
                    req_type = "new_requirement" if testcase_type == "new_testcase" else "old_requirement"
                    req_key = f"{scenario_id}_{req_type}"
                    
                    # 如果需求节点不存在，创建一个
                    if req_key not in nodes:
                        nodes[req_key] = {
                            "id": scenario_id, 
                            "label": scenario_id, 
                            "text": scenario_text, 
                            "type": req_type,
                            "change_type": testcase_change_type
                        }
                    
                    # 创建需求到场景的连接
                    links.append({"source": req_key, "target": parent_key})
                    
                    # 创建需求到规则的连接
                    # 从需求ID的前3位提取规则ID（如 "3.1.5.1" -> "3.1.5"）
                    parts = scenario_id.split(".")
                    if len(parts) >= 4:
                        # 取前3位作为规则ID
                        rule_id_part = ".".join(parts[:3])
                        
                        # 查找对应的规则节点
                        rule_type = "old_rule" if req_type == "old_requirement" else "new_rule"
                        rule_key = f"{rule_id_part}_{rule_type}"
                        
                        # 如果对应的规则类型不存在，尝试另一种规则类型
                        if rule_key not in nodes:
                            other_rule_type = "old_rule" if rule_type == "new_rule" else "new_rule"
                            other_rule_key = f"{rule_id_part}_{other_rule_type}"
                            if other_rule_key in nodes:
                                rule_key = other_rule_key
                        
                        # 创建规则到需求的连接
                        if rule_key in nodes:
                            links.append({"source": rule_key, "target": req_key})
            
            links.append({"source": parent_key, "target": testcase_key})

    # 确保起始规则在 nodes 中
    if rule_id:
        # 检查是否已有对应的旧规则或新规则
        old_rule_key = f"{rule_id}_old_rule"
        new_rule_key = f"{rule_id}_new_rule"
        
        # 如果已有旧规则或新规则，直接使用
        if old_rule_key in nodes or new_rule_key in nodes:
            pass
        else:
            # 确定规则的变更类型和类型
            if rule_id in add_rules:
                change_type = "add"
                rule_type = "new_rule"
                rule_key = new_rule_key
            elif rule_id in delete_rules:
                change_type = "delete"
                rule_type = "old_rule"
                rule_key = old_rule_key
            else:
                change_type = "unchanged"
                rule_type = "rule"
                rule_key = rule_id
            
            # 创建规则节点
            nodes[rule_key] = {
                "id": rule_id, 
                "label": rule_id, 
                "text": rule_id,
                "type": rule_type,
                "change_type": change_type
            }

    # 检查并合并相同的节点（unchanged+id一致）
    # 创建一个字典，用于存储每个 id 对应的最佳节点
    merged_nodes = {}
    # 存储需要删除的节点 key
    nodes_to_remove = []
    # 存储节点 key 到合并后节点 key 的映射
    node_key_mapping = {}
    
    # 第一次遍历：收集每个节点
    # 对于同一 type 的节点，使用 id 作为唯一标识（合并相同 id 的节点）
    # 对于不同 type 的节点，使用 type 作为区分
    for node_key, node in nodes.items():
        node_id = node.get("id")
        node_type = node.get("type")
        change_type = node.get("change_type")
        
        if node_id and node_type:
            # 对于同一 type 的节点，使用 id 作为唯一标识
            unique_id = f"{node_type}_{node_id}"
            
            # 优先保留 unchanged 类型的节点
            if unique_id not in merged_nodes or change_type == "unchanged":
                merged_nodes[unique_id] = node_key
    
    # 第二次遍历：标记需要删除的节点
    for node_key, node in nodes.items():
        node_id = node.get("id")
        node_type = node.get("type")
        
        if node_id and node_type:
            # 对于同一 type 的节点，使用 id 作为唯一标识
            unique_id = f"{node_type}_{node_id}"
            
            if node_key != merged_nodes.get(unique_id):
                nodes_to_remove.append(node_key)
                # 建立映射关系
                node_key_mapping[node_key] = merged_nodes[unique_id]
    
    # 删除需要删除的节点
    for node_key in nodes_to_remove:
        del nodes[node_key]
    
    # 更新链接，确保它们指向合并后的节点，并且只创建相邻层级之间的连接
    updated_links = []
    for link in links:
        source = link.get("source")
        target = link.get("target")
        
        # 更新 source
        if source in node_key_mapping:
            source = node_key_mapping[source]
        
        # 更新 target
        if target in node_key_mapping:
            target = node_key_mapping[target]
        
        # 确保 source 和 target 都存在
        if source in nodes and target in nodes:
            # 检查是否是相邻层级之间的连接
            source_node = nodes[source]
            target_node = nodes[target]
            source_type = source_node.get("type")
            target_type = target_node.get("type")
            
            # 只允许以下类型的连接：
            # 1. 规则到需求（rule -> requirement）
            # 2. 需求到场景（requirement -> scenario）
            # 3. 场景到测试用例（scenario -> testcase）
            is_valid_connection = False
            
            # 规则到需求
            if ("rule" in source_type and "requirement" in target_type):
                is_valid_connection = True
            # 需求到场景
            elif ("requirement" in source_type and "scenario" in target_type):
                is_valid_connection = True
            # 场景到测试用例
            elif ("scenario" in source_type and "testcase" in target_type):
                is_valid_connection = True
            
            if is_valid_connection:
                updated_links.append({"source": source, "target": target})
    
    # 找出没有连接到规则节点的需求节点
    connected_requirements = set()
    for link in updated_links:
        source = link.get("source")
        target = link.get("target")
        
        source_node = nodes.get(source)
        target_node = nodes.get(target)
        
        # 规则到需求的连接
        if source_node and "rule" in source_node.get("type", "") and target_node and "requirement" in target_node.get("type", ""):
            connected_requirements.add(target)
    
    # 找出所有需求节点
    all_requirements = set()
    for node_key, node in nodes.items():
        if "requirement" in node.get("type", ""):
            all_requirements.add(node_key)
    
    # 找出没有连接到规则节点的需求节点
    unconnected_requirements = all_requirements - connected_requirements
    
    # 处理未连接的需求节点，连接到其 sourceId 对应的规则节点
    if unconnected_requirements:
        # 首先创建"其他规则"节点，作为备用
        other_rule_key = "other_rule"
        if other_rule_key not in nodes:
            nodes[other_rule_key] = {
                "id": "other",
                "label": "其他规则",
                "text": "其他规则",
                "type": "old_rule",
                "change_type": "unchanged"
            }
        
        # 为每个未连接的需求节点找到对应的规则节点
        for req_key in unconnected_requirements:
            req_node = nodes.get(req_key)
            if req_node:
                # 从需求节点中获取 sourceId（规则ID）
                source_id = req_node.get("sourceId") or req_node.get("source_id")
                
                # 如果有 sourceId，尝试找到对应的规则节点
                if source_id:
                    # 尝试查找新旧规则节点
                    old_rule_key = f"{source_id}_old_rule"
                    new_rule_key = f"{source_id}_new_rule"
                    
                    if old_rule_key in nodes:
                        # 连接到旧规则节点
                        updated_links.append({
                            "source": old_rule_key,
                            "target": req_key
                        })
                    elif new_rule_key in nodes:
                        # 连接到新规则节点
                        updated_links.append({
                            "source": new_rule_key,
                            "target": req_key
                        })
                    else:
                        # 如果没有找到对应的规则节点，连接到"其他规则"节点
                        updated_links.append({
                            "source": other_rule_key,
                            "target": req_key
                        })
                else:
                    # 如果没有 sourceId，连接到"其他规则"节点
                    updated_links.append({
                        "source": other_rule_key,
                        "target": req_key
                    })
    
    # 保存结果到项目文件夹
    result = {
        "project_id": project.id,
        "rule_id": rule_id,
        "graph": {
            "nodes": list(nodes.values()),
            "links": updated_links
        }
    }
    
    # 获取项目文件夹路径（从第一个存在的文件路径中提取）
    project_folder = None
    for path_attr in paths:
        file_path = getattr(project, path_attr, None)
        if file_path and os.path.isfile(file_path):
            project_folder = os.path.dirname(file_path)
            break
    
    # 如果找不到文件路径，使用默认路径
    if not project_folder:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        project_folder = os.path.join(project_root, "projects", f"project_{project_id}")
    
    # 保存结果到 JSON 文件
    output_file = os.path.join(project_folder, f"trace_rule_{rule_id.replace('.', '_') if rule_id else 'all'}.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save result: {str(e)}")

    return jsonify(result)


