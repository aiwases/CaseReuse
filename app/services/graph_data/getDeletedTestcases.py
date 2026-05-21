from app.models import Project
import json
import os


def get_deleted_testcases(project_id):
    """
    获取项目中删除的测试用例ID集合
    
    Args:
        project_id: 项目ID
        
    Returns:
        set: 删除的测试用例ID集合
    """
    deleted_testcases = set()
    
    # 获取项目信息
    project = Project.query.get(project_id)
    if not project:
        return deleted_testcases
    
    # 获取 intermediate_path6 文件路径
    intermediate_path6 = project.intermediate_path6
    if not intermediate_path6 or not os.path.exists(intermediate_path6):
        return deleted_testcases
    
    try:
        # 读取 intermediate_path6 文件内容
        with open(intermediate_path6, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析JSON
        try:
            data = json.loads(content)
            
            # 检查 data 是否是字典类型
            if isinstance(data, dict):
                # 提取删除的测试用例ID列表
                to_delete_testcases = data.get("data", {}).get("to_delete_testcases", [])
                
                # 将删除的测试用例ID添加到集合中
                deleted_testcases.update(to_delete_testcases)
            else:
                print(f"intermediate_path6 文件格式错误: data 不是字典类型")
                
        except json.JSONDecodeError as e:
            print(f"解析 intermediate_path6 文件失败: {str(e)}")
                
    except Exception as e:
        print(f"获取删除的测试用例失败: {str(e)}")
    
    return deleted_testcases
