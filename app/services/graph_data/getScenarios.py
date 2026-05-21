from app.models import Project
import json
import os


def get_scenario_nodes(project_id, rule_id=None, rule_change_type=None):
    """
    获取项目的场景节点和需求节点，以及场景之间的边

    从 intermediate_path3 和 new_test_scenarios_path 中读取场景和需求。
    只有包含 before/after 任一属性的需求是场景，场景ID与需求ID相同。
    场景节点需要与自身需求相连，也需要与 before/after 中的需求相连。
    所有需求节点都被保留，旧文档中属于删除场景的需求节点打上 delete 的 change_type。

    Args:
        project_id: 项目ID
        rule_id: 指定规则ID（可选）

    Returns:
        tuple: (节点字典 {节点ID_类型: 节点对象}, 边列表 [边对象])
    """
    nodes = {}
    edges = []

    # 获取项目信息
    project = Project.query.get(project_id)
    if not project:
        return nodes, edges

    # 获取删除的场景
    deleted_scenarios = set()

    # 获取 intermediate_path6 文件路径
    intermediate_path6 = project.intermediate_path6
    if intermediate_path6 and os.path.exists(intermediate_path6):
        try:
            # 读取文件内容
            with open(intermediate_path6, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取删除的关联场景
            to_delete_scenarios = data.get("data", {}).get("to_delete_scenarios", [])
            # to_delete_scenarios 是字符串列表，每个元素直接是场景ID
            for scenario_id in to_delete_scenarios:
                if scenario_id:
                    deleted_scenarios.add(scenario_id)

        except Exception as e:
            print(f"读取 intermediate_path6 文件失败: {str(e)}")

    # 先读取旧文档场景，用于新文档场景的变更类型判断
    old_scenarios = set()
    old_requirements = set()

    # 读取 intermediate_path3（旧文档场景）
    if rule_change_type != "unchanged":
        intermediate_path3 = getattr(project, "intermediate_path3", None)
        if intermediate_path3 and os.path.isfile(intermediate_path3):
            try:
                with open(intermediate_path3, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 从 data.scenarios 或 data.data.scenarios 读取
                scenarios = data.get("scenarios", [])
                if not scenarios:
                    scenarios = data.get("data", {}).get("scenarios", [])

                for scenario in scenarios:
                    # 处理直接的需求对象（2_out.json 格式）
                    req_id = scenario.get("rule") or scenario.get("id")
                    if not req_id:
                        continue
                    if rule_id:
                        # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                        if req_id != rule_id and not req_id.startswith(f"{rule_id}."):
                            continue
                    old_requirements.add(req_id)

                    # 检查是否有 before/after 属性（即使为空字符串也认为有）
                    if "before" in scenario or "after" in scenario:
                        old_scenarios.add(req_id)

                    # 处理 before 中的需求
                    if "before" in scenario and scenario.get("before"):
                        before_req_id = scenario.get("before")
                        if isinstance(before_req_id, list):
                            for before_id in before_req_id:
                                if rule_id:
                                    if before_id != rule_id and not before_id.startswith(f"{rule_id}."):
                                        continue
                                old_requirements.add(before_id)
                        else:
                            if rule_id:
                                if before_req_id != rule_id and not before_req_id.startswith(f"{rule_id}."):
                                    continue
                            old_requirements.add(before_req_id)

                    # 处理 after 中的需求
                    if "after" in scenario and scenario.get("after"):
                        after_req_id = scenario.get("after")
                        if isinstance(after_req_id, list):
                            for after_id in after_req_id:
                                if rule_id:
                                    if after_id != rule_id and not after_id.startswith(f"{rule_id}."):
                                        continue
                                old_requirements.add(after_id)
                        else:
                            if rule_id:
                                if after_req_id != rule_id and not after_req_id.startswith(f"{rule_id}."):
                                    continue
                            old_requirements.add(after_req_id)

            except Exception as e:
                print(f"读取 intermediate_path3 文件失败: {str(e)}")

    # 读取 intermediate_path3（旧文档场景）并创建节点
    if rule_change_type != "unchanged":
        intermediate_path3 = getattr(project, "intermediate_path3", None)
        if intermediate_path3 and os.path.isfile(intermediate_path3):
            try:
                with open(intermediate_path3, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 从 data.scenarios 或 data.data.scenarios 读取
                scenarios = data.get("scenarios", [])
                if not scenarios:
                    scenarios = data.get("data", {}).get("scenarios", [])


                for scenario in scenarios:
                    # 处理直接的需求对象（2_out.json 格式）
                    req_id = scenario.get("rule") or scenario.get("id")
                    if not req_id:
                        continue
                    if rule_id:
                        # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                        if req_id != rule_id and not req_id.startswith(f"{rule_id}."):
                            continue

                    # 检查需求是否在删除列表中
                    if req_id in deleted_scenarios:
                        req_change_type = "delete"
                    else:
                        req_change_type = "unchanged"

                    # 创建需求节点
                    req_node_type = "old_requirement"
                    req_key = f"{req_id}_{req_node_type}"

                    nodes[req_key] = {
                        "id": req_id,
                        "label": req_id,
                        "text": scenario.get("text", req_id),
                        "type": req_node_type,
                        "change_type": req_change_type,
                        "sourceId": scenario.get("sourceId")
                    }

                    # 检查是否有 before/after 属性（即使为空字符串也认为有）
                    has_before_after = "before" in scenario or "after" in scenario
                    if has_before_after:
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
                        
                        # 创建场景节点（场景ID与需求ID相同）
                        scenario_node_type = "old_scenario"
                        scenario_key = f"{req_id}_{scenario_node_type}"

                        # 场景节点的 change_type 与需求节点相同，text 是所有需求的ID
                        nodes[scenario_key] = {
                            "id": req_id,
                            "label": req_id,
                            "text": ", ".join(related_requirements),
                            "type": scenario_node_type,
                            "change_type": req_change_type
                        }

                        # 创建需求到场景的连接
                        edges.append({
                            "source": req_key,
                            "target": scenario_key
                        })

                        # 处理 before/after 连接
                        if "before" in scenario and scenario.get("before"):
                            # 创建从 before 需求到当前场景的边
                            before_req_id = scenario.get("before")
                            if isinstance(before_req_id, list):
                                # 如果 before 是数组
                                for before_id in before_req_id:
                                    before_req_key = f"{before_id}_old_requirement"
                                    # 如果节点不存在，创建一个
                                    if before_req_key not in nodes:
                                        nodes[before_req_key] = {
                                            "id": before_id,
                                            "label": before_id,
                                            "text": before_id,
                                            "type": "old_requirement",
                                            "change_type": "unchanged"
                                        }
                                    # 创建边 - 需求到场景
                                    if scenario_key in nodes:
                                        edges.append({
                                            "source": before_req_key,
                                            "target": scenario_key
                                        })
                            else:
                                # 如果 before 是单个值
                                before_req_key = f"{before_req_id}_old_requirement"
                                # 如果节点不存在，创建一个
                                if before_req_key not in nodes:
                                    nodes[before_req_key] = {
                                        "id": before_req_id,
                                        "label": before_req_id,
                                        "text": before_req_id,
                                        "type": "old_requirement",
                                        "change_type": "unchanged"
                                    }
                                # 创建边 - 需求到场景
                                if scenario_key in nodes:
                                    edges.append({
                                        "source": before_req_key,
                                        "target": scenario_key
                                    })
                        if "after" in scenario and scenario.get("after"):
                            # 创建从 after 需求到当前场景的边
                            after_req_id = scenario.get("after")
                            if isinstance(after_req_id, list):
                                # 如果 after 是数组
                                for after_id in after_req_id:
                                    after_req_key = f"{after_id}_old_requirement"
                                    # 如果节点不存在，创建一个
                                    if after_req_key not in nodes:
                                        nodes[after_req_key] = {
                                            "id": after_id,
                                            "label": after_id,
                                            "text": after_id,
                                            "type": "old_requirement",
                                            "change_type": "unchanged"
                                        }
                                    # 创建边 - 需求到场景
                                    if scenario_key in nodes:
                                        edges.append({
                                            "source": after_req_key,
                                            "target": scenario_key
                                        })
                            else:
                                # 如果 after 是单个值
                                after_req_key = f"{after_req_id}_old_requirement"
                                # 如果节点不存在，创建一个
                                if after_req_key not in nodes:
                                    nodes[after_req_key] = {
                                        "id": after_req_id,
                                        "label": after_req_id,
                                        "text": after_req_id,
                                        "type": "old_requirement",
                                        "change_type": "unchanged"
                                    }
                                # 创建边 - 需求到场景
                                if scenario_key in nodes:
                                    edges.append({
                                        "source": after_req_key,
                                        "target": scenario_key
                                    })

            except Exception as e:
                print(f"读取 intermediate_path3 文件失败: {str(e)}")

    # 读取 new_test_scenarios_path（新文档场景）
    new_test_scenarios_path = getattr(project, "new_test_scenarios_path", None)
    if new_test_scenarios_path and os.path.isfile(new_test_scenarios_path):
        try:
            with open(new_test_scenarios_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 从 data.scenarios 或 data.data.scenarios 读取
            scenarios = data.get("scenarios", [])
            if not scenarios:
                scenarios = data.get("data", {}).get("scenarios", [])


            for scenario in scenarios:
                # 处理直接的需求对象（2_out.json 格式）
                req_id = scenario.get("rule") or scenario.get("id")
                if not req_id:
                    continue
                if rule_id:
                    # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                    if req_id != rule_id and not req_id.startswith(f"{rule_id}."):
                        continue

                # 确定需求的变更类型
                if req_id in old_requirements and req_id not in deleted_scenarios:
                    req_change_type = "unchanged"
                else:
                    req_change_type = "add"

                # 即使是 unchanged，也创建新需求节点（因为场景需要连接到它）
                # 创建需求节点
                req_node_type = "new_requirement"
                req_key = f"{req_id}_{req_node_type}"

                nodes[req_key] = {
                    "id": req_id,
                    "label": req_id,
                    "text": scenario.get("text", req_id),
                    "type": req_node_type,
                    "change_type": req_change_type,
                    "sourceId": scenario.get("sourceId")
                }

                # 检查是否有 before/after 属性（即使为空字符串也认为有）
                has_before_after = "before" in scenario or "after" in scenario
                if has_before_after:
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
                    
                    # 创建场景节点（场景ID与需求ID相同）
                    scenario_node_type = "new_scenario"
                    scenario_key = f"{req_id}_{scenario_node_type}"

                    # 场景节点的 change_type 与需求节点相同，text 是所有需求的ID
                    nodes[scenario_key] = {
                        "id": req_id,
                        "label": req_id,
                        "text": ", ".join(related_requirements),
                        "type": scenario_node_type,
                        "change_type": req_change_type
                    }

                    # 创建需求到场景的连接
                    edges.append({
                        "source": req_key,
                        "target": scenario_key
                    })

                    # 处理 before/after 连接
                    if "before" in scenario and scenario.get("before"):
                        # 创建从 before 需求到当前场景的边
                        before_req_id = scenario.get("before")
                        if isinstance(before_req_id, list):
                            # 如果 before 是数组
                            for before_id in before_req_id:
                                # 只连接到同类型的需求节点
                                before_req_key = f"{before_id}_new_requirement"
                                # 如果节点不存在，创建一个
                                if before_req_key not in nodes:
                                    nodes[before_req_key] = {
                                        "id": before_id,
                                        "label": before_id,
                                        "text": before_id,
                                        "type": "new_requirement",
                                        "change_type": "add"
                                    }
                                # 创建边 - 需求到场景
                                if scenario_key in nodes:
                                    edges.append({
                                        "source": before_req_key,
                                        "target": scenario_key
                                    })
                        else:
                            # 如果 before 是单个值
                            before_req_key = f"{before_req_id}_new_requirement"
                            # 如果节点不存在，创建一个
                            if before_req_key not in nodes:
                                nodes[before_req_key] = {
                                    "id": before_req_id,
                                    "label": before_req_id,
                                    "text": before_req_id,
                                    "type": "new_requirement",
                                    "change_type": "add"
                                }
                            # 创建边 - 需求到场景
                            if scenario_key in nodes:
                                edges.append({
                                    "source": before_req_key,
                                    "target": scenario_key
                                })
                    if "after" in scenario and scenario.get("after"):
                        # 创建从 after 需求到当前场景的边
                        after_req_id = scenario.get("after")
                        if isinstance(after_req_id, list):
                            # 如果 after 是数组
                            for after_id in after_req_id:
                                # 只连接到同类型的需求节点
                                after_req_key = f"{after_id}_new_requirement"
                                # 如果节点不存在，创建一个
                                if after_req_key not in nodes:
                                    nodes[after_req_key] = {
                                        "id": after_id,
                                        "label": after_id,
                                        "text": after_id,
                                        "type": "new_requirement",
                                        "change_type": "add"
                                    }
                                # 创建边 - 需求到场景
                                if scenario_key in nodes:
                                    edges.append({
                                        "source": after_req_key,
                                        "target": scenario_key
                                    })
                        else:
                            # 如果 after 是单个值
                            after_req_key = f"{after_req_id}_new_requirement"
                            # 如果节点不存在，创建一个
                            if after_req_key not in nodes:
                                nodes[after_req_key] = {
                                    "id": after_req_id,
                                    "label": after_req_id,
                                    "text": after_req_id,
                                    "type": "new_requirement",
                                    "change_type": "add"
                                }
                            # 创建边 - 需求到场景
                            if scenario_key in nodes:
                                edges.append({
                                    "source": after_req_key,
                                    "target": scenario_key
                                })

        except Exception as e:
            print(f"读取 new_test_scenarios_path 文件失败: {str(e)}")

    return nodes, edges
