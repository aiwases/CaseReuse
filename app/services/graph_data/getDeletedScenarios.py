from app.models import Project
import json
import os


def get_deleted_scenarios(project_id):
    """
    获取项目中删除的场景
    
    Args:
        project_id: 项目ID
        
    Returns:
        set: 删除的场景ID集合
    """
    deleted_scenarios = set()
    
    # 获取项目信息
    project = Project.query.get(project_id)
    if not project:
        return deleted_scenarios
    
    # 获取 intermediate_path6 文件路径
    intermediate_path6 = project.intermediate_path6
    if not intermediate_path6 or not os.path.exists(intermediate_path6):
        return deleted_scenarios
    
    try:
        # 读取文件内容
        with open(intermediate_path6, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析JSON
        try:
            data = json.loads(content)
            
            # 检查 data 是否是字典类型
            if isinstance(data, dict):
                # 提取删除的关联场景
                to_delete_scenarios = data.get("data", {}).get("to_delete_scenarios", [])
                # to_delete_scenarios 是字符串列表，每个元素直接是场景ID
                for scenario_id in to_delete_scenarios:
                    if scenario_id:
                        deleted_scenarios.add(scenario_id)
            else:
                print(f"intermediate_path6 文件格式错误: data 不是字典类型")
                
        except json.JSONDecodeError as e:
            print(f"解析 intermediate_path6 文件失败: {str(e)}")
        
    except Exception as e:
        print(f"读取 intermediate_path6 文件失败: {str(e)}")
    
    return deleted_scenarios
