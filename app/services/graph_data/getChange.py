from app.models import Project
import json
import os

def get_change_rules(project_id):
    """
    根据项目ID获取添加和删除的规则
    
    Args:
        project_id: 项目ID
        
    Returns:
        dict: {
            "add_rules": ["规则ID1", "规则ID2"],
            "delete_rules": ["规则ID3", "规则ID4"]
        }
    """
    # 获取项目信息
    project = Project.query.get(project_id)
    if not project:
        return {"add_rules": [], "delete_rules": []}
    
    # 获取 intermediate_path5 文件路径
    intermediate_path5 = project.intermediate_path5
    if not intermediate_path5 or not os.path.exists(intermediate_path5):
        return {"add_rules": [], "delete_rules": []}
    
    try:
        # 读取文件内容
        with open(intermediate_path5, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取添加和删除的规则ID
        add_rules = []
        delete_rules = []
        
        # 获取添加的规则
        to_add_rules = data.get("data", {}).get("to_add_rules", [])
        for rule in to_add_rules:
            add_rules.append(rule.get("id", ""))
        
        # 获取删除的规则
        to_delete_rules = data.get("data", {}).get("to_delete_rules", [])
        for rule in to_delete_rules:
            delete_rules.append(rule.get("id", ""))
        
        return {
            "add_rules": add_rules,
            "delete_rules": delete_rules
        }
        
    except Exception as e:
        print(f"读取 intermediate_path5 文件失败: {str(e)}")
        return {"add_rules": [], "delete_rules": []}
