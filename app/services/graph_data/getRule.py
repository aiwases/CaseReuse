from app.models import Project
import json
import os


def get_rule_nodes_with_change_type(project_id, rule_id=None, add_rules=None, delete_rules=None):
    """
    获取项目的规则节点（包含 change_type）
    
    Args:
        project_id: 项目ID
        rule_id: 指定规则ID（可选）
        add_rules: 添加的规则列表（可选）
        delete_rules: 删除的规则列表（可选）
        
    Returns:
        dict: 规则节点字典 {规则ID: 节点对象}
    """
    from app.services.graph_data.getChange import get_change_rules
    
    # 如果没有提供变更规则，自动获取
    if add_rules is None or delete_rules is None:
        change_rules = get_change_rules(project_id)
        add_rules = change_rules.get("add_rules", [])
        delete_rules = change_rules.get("delete_rules", [])
    
    nodes = {}
    
    # 获取项目信息
    project = Project.query.get(project_id)
    if not project:
        return nodes
    
    # 先读取旧文档规则，用于新文档规则的变更类型判断
    old_rules = set()
    
    # 读取 intermediate_path1（旧文档规则）
    intermediate_path1 = getattr(project, "intermediate_path1", None)
    if intermediate_path1 and os.path.isfile(intermediate_path1):
        try:
            with open(intermediate_path1, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            rules = data.get("data", {}).get("rules", [])
            if rules:
                for rule in rules:
                    nid = rule.get("rule") or rule.get("id")
                    if not nid:
                        continue
                    if rule_id:
                        # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                        if nid != rule_id and not nid.startswith(f"{rule_id}."):
                            continue
                    old_rules.add(nid)
                    
        except Exception as e:
            print(f"读取 intermediate_path1 文件失败: {str(e)}")
    
    # 读取 intermediate_path1（旧文档规则）并创建节点
    if intermediate_path1 and os.path.isfile(intermediate_path1):
        try:
            with open(intermediate_path1, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            rules = data.get("data", {}).get("rules", [])
            if rules:
                for rule in rules:
                    nid = rule.get("rule") or rule.get("id")
                    if not nid:
                        continue
                    if rule_id:
                        # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                        if nid != rule_id and not nid.startswith(f"{rule_id}."):
                            continue
                    
                    rule_type = "old_rule"
                    
                    # 确定规则的变更类型
                    # 旧文档里的都是删除的或者不变的
                    if nid in delete_rules:
                        change_type = "delete"
                    else:
                        # 如果规则是 unchanged，只保留新文档的节点，不保留旧文档的节点
                        continue
                    
                    # 使用 id + type 作为唯一标识，确保新旧文档规则不被覆盖
                    unique_key = f"{nid}_{rule_type}"
                    
                    nodes[unique_key] = {
                        "id": nid,
                        "label": nid,
                        "text": rule.get("text", nid),
                        "type": rule_type,
                        "change_type": change_type
                    }
                    
        except Exception as e:
            print(f"读取 intermediate_path1 文件失败: {str(e)}")
    
    # 读取 intermediate_path2（新文档规则）
    intermediate_path2 = getattr(project, "intermediate_path2", None)
    if intermediate_path2 and os.path.isfile(intermediate_path2):
        try:
            with open(intermediate_path2, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            rules = data.get("data", {}).get("rules", [])
            if rules:
                for rule in rules:
                    nid = rule.get("rule") or rule.get("id")
                    if not nid:
                        continue
                    if rule_id:
                        # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                        if nid != rule_id and not nid.startswith(f"{rule_id}."):
                            continue
                    
                    rule_type = "new_rule"
                    
                    # 确定规则的变更类型
                    # 新文档里的都是新增的或者不变的
                    if nid in add_rules:
                        change_type = "add"
                    else:
                        change_type = "unchanged"
                    
                    # 如果是 unchanged，优先使用新文档的节点，不保留旧文档的节点
                    if change_type == "unchanged":
                        # 检查是否存在旧文档的节点，如果存在则删除
                        old_unique_key = f"{nid}_old_rule"
                        if old_unique_key in nodes:
                            del nodes[old_unique_key]
                    
                    # 使用 id + type 作为唯一标识，确保新旧文档规则不被覆盖
                    unique_key = f"{nid}_{rule_type}"
                    
                    nodes[unique_key] = {
                        "id": nid,
                        "label": nid,
                        "text": rule.get("text", nid),
                        "type": rule_type,
                        "change_type": change_type
                    }
                    
        except Exception as e:
            print(f"读取 intermediate_path2 文件失败: {str(e)}")
    
    return nodes