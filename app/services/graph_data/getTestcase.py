from app.models import Project
import json
import os
from .getDeletedTestcases import get_deleted_testcases


def get_testcase_nodes(project_id, rule_id=None, rule_change_type=None):
    """
    获取项目的测试用例节点
    
    Args:
        project_id: 项目ID
        rule_id: 指定规则ID（可选）
        
    Returns:
        dict: 测试用例节点字典 {测试用例ID: 节点对象}
    """
    nodes = {}
    
    # 获取项目信息
    project = Project.query.get(project_id)
    if not project:
        return nodes
    
    # 获取删除的测试用例
    deleted_testcases = get_deleted_testcases(project_id)
    
    # 获取旧测试用例文件内容
    old_testcases = {}
    old_test_case_path = project.old_test_case_path
    
    # 尝试读取 old_test_case_path
    old_testcase_list = []
    if old_test_case_path and os.path.exists(old_test_case_path):
        try:
            with open(old_test_case_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 尝试解析标准JSON
            try:
                old_data = json.loads(content)
                
                # 检查文件格式
                if "testcases" in old_data:
                    old_testcase_list = old_data["testcases"]
                elif "data" in old_data and "testcases" in old_data["data"]:
                    old_testcase_list = old_data["data"]["testcases"]
                elif "old_testcases" in old_data:
                    # 处理 old_testcases 字段
                    old_testcase_list = old_data["old_testcases"]
                elif isinstance(old_data, list):
                    # 处理嵌套数组格式：[[{...}], [{...}]]
                    for case_list in old_data:
                        if isinstance(case_list, list):
                            old_testcase_list.extend(case_list)
                else:
                    old_testcase_list = []
                    
            except json.JSONDecodeError:
                # 处理非标准JSON格式："old_testcases": [[...]]
                if content.strip().startswith('"old_testcases":'):
                    # 提取数组部分
                    array_str = content.strip().split(':', 1)[1].strip()
                    old_data = json.loads(array_str)
                    if isinstance(old_data, list):
                        # 处理嵌套数组格式：[[{...}], [{...}]]
                        for case_list in old_data:
                            if isinstance(case_list, list):
                                old_testcase_list.extend(case_list)
                    else:
                        old_testcase_list = []
                else:
                    old_testcase_list = []
                    
        except Exception as e:
            print(f"读取 old_test_case_path 文件失败: {str(e)}")
    else:
        print(f"旧测试用例文件不存在: {old_test_case_path}")
    
    # 如果没有找到测试用例，尝试读取 oldTestcase.json（大小写不同）
    if not old_testcase_list:
        alternative_path = os.path.join(os.path.dirname(old_test_case_path), "oldTestcase.json") if old_test_case_path else None
        if alternative_path and os.path.exists(alternative_path):
            try:
                with open(alternative_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 处理非标准JSON格式："old_testcases": [[...]]
                if content.strip().startswith('"old_testcases":'):
                    # 提取数组部分
                    array_str = content.strip().split(':', 1)[1].strip()
                    old_data = json.loads(array_str)
                    if isinstance(old_data, list):
                        # 处理嵌套数组格式：[[{...}], [{...}]]
                        for case_list in old_data:
                            if isinstance(case_list, list):
                                old_testcase_list.extend(case_list)
                    else:
                        old_testcase_list = []
                else:
                    old_testcase_list = []
                    
            except Exception as e:
                print(f"读取 oldTestcase.json 文件失败: {str(e)}")
    
    # 构建旧测试用例字典
    for testcase in old_testcase_list:
        testcase_id = testcase.get("testid") or testcase.get("id")
        if testcase_id:
            old_testcases[testcase_id] = testcase
    
    # 获取 result_path 文件路径
    result_path = project.result_path
    if result_path and os.path.exists(result_path):
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # result_path 格式: {"code": 200, "data": {"testcases": [[...]]}}
            testcases = data.get("data", {}).get("testcases", [])
            for case_list in testcases:
                for case in case_list:
                    scenario_id = case.get("rule")  # 场景ID
                    test_id = case.get("testid")  # 测试用例ID
                    if not scenario_id or not test_id:
                        continue
                    if rule_id:
                        # 精确匹配：要么完全相等，要么以 rule_id + "." 开头（确保是子节点）
                        if scenario_id != rule_id and not scenario_id.startswith(f"{rule_id}."):
                            continue
                    
                    # 确定测试用例的变更类型
                    # result_path 里的节点 change_type 不可能是 delete
                    if test_id in old_testcases and test_id not in deleted_testcases:
                        change_type = "unchanged"
                    else:
                        change_type = "add"
                    
                    # 使用 id + "_new_testcase" 作为唯一标识
                    unique_key = f"{test_id}_new_testcase"
                    nodes[unique_key] = {
                        "id": test_id,
                        "label": test_id,
                        "text": test_id,
                        "type": "new_testcase",
                        "change_type": change_type,
                        "testcase": case  # 添加完整的测试用例数据
                    }
                    
        except Exception as e:
            print(f"读取 result_path 文件失败: {str(e)}")
    
    # 从 intermediate_path6 的 to_delete_testcases 里添加所有相关的节点
    # change_type 是 delete，节点信息从 old_test_case_path 读取
    # 如果规则是 unchanged，跳过处理删除的测试用例
    if rule_change_type != "unchanged":
        for testcase_id in deleted_testcases:
            # 获取场景ID（从测试用例ID提取前5位）
            try:
                parts = testcase_id.split("_")[0].split(".")
                if len(parts) >= 5:
                    scenario_id = ".".join(parts[:5])
                    if rule_id and not scenario_id.startswith(rule_id):
                        continue
                    
                    # 使用 id + "_old_testcase" 作为唯一标识
                    unique_key = f"{testcase_id}_old_testcase"
                    
                    # 从旧测试用例中获取完整的测试用例数据
                    testcase_data = old_testcases.get(testcase_id, {})
                    
                    nodes[unique_key] = {
                        "id": testcase_id,
                        "label": testcase_id,
                        "text": testcase_id,
                        "type": "old_testcase",
                        "change_type": "delete",
                        "testcase": testcase_data  # 添加完整的测试用例数据
                    }
            except Exception as e:
                print(f"处理删除测试用例 {testcase_id} 失败: {str(e)}")
    
    return nodes
