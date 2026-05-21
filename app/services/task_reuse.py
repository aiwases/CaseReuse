import requests
import json
import os


# def task1(document_type, text_path, project_folder):
def task1(document_type, project_folder):
    log_lines = ["[任务1] 开始处理输入文件"]
    status = 'success'

    try:
        # if not text_path:
        #     raise ValueError("输入内容为空")

        # 按接口文档组装请求：
        # fileType=0 表示 PDF URL，fileType=1 表示文本内容。
        # if isinstance(text_path, str) and text_path.startswith(("http://", "https://")):
        #     payload = {
        #         "fileType": "0",
        #         "fileData": text_path
        #     }
        #     log_lines.append("[任务1] 检测到URL输入，按PDF URL模式提交")
        # elif os.path.isfile(text_path):
        #     _, ext = os.path.splitext(text_path)
        #     ext = ext.lower()
        #     if ext == ".pdf":
        #         raise ValueError("当前接口文档仅支持PDF URL或文本内容，本地PDF文件请先转换为可访问URL后重试")

        #     with open(text_path, "r", encoding="utf-8") as f:
        #         document_text = f.read().strip()

        #     if not document_text:
        #         raise ValueError(f"输入文本文件为空：{text_path}")

        #     payload = {
        #         "fileType": "1",
        #         "fileData": document_text
        #     }
        #     log_lines.append(f"[任务1] 检测到本地文本文件输入，按文本模式提交: {text_path}")
        # else:
        #     payload = {
        #         "fileType": "1",
        #         "fileData": str(text_path)
        #     }
        #     log_lines.append("[任务1] 未识别为URL/本地文件，按文本内容模式提交")
        if document_type=="old":
            payload={
            "fileType": "0",
            "fileData": "https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020210331716400647184.pdf"
            }
        else:
            # 新文档
            payload={
            "fileType": "0",
            "fileData": "https://docs.static.szse.cn/www/lawrules/rule/stock/W020230217564423808793.pdf"
            }

        # 发送POST请求
        url = "http://219.228.60.68:9092/requirement_generation"

        log_lines.append(f"[任务1] 正在请求接口: {url}")
        print("请求", url, "已发送1")
        print(document_type)
        print(payload)
        response = requests.post(url, json=payload, timeout=(30,3000))
        print("请求", url, "已发送2")

        # 检查响应
        if response.status_code != 200:
            log_lines.append(f"[任务1] 接口返回状态码异常: {response.status_code}")
            log_lines.append(f"[任务1] 响应体: {response.text}")
            status = 'failed'
            raise RuntimeError(f"接口返回错误状态码 {response.status_code}")

        resp_json = response.json()
        status_code = resp_json.get("code")
        data_field = resp_json.get("data")
        msg = resp_json.get("msg")

        # 接口内部错误
        if status_code != 200 or not data_field:
            log_lines.append(f"[任务1] 接口内部返回异常: status_code={status_code}")
            log_lines.append(f"[任务1] msg={msg}")
            log_lines.append(f"[任务1] data={data_field}")
            raise ValueError("接口返回内容异常或为空")

        # 保存输出JSON文件（按 old/new 分流，避免互相覆盖）
        output_filename = "1_out_new.json" if document_type == "new" else "1_out.json"
        intermediate_path1 = os.path.join(project_folder, output_filename)
        with open(intermediate_path1, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)

        log_lines.append(f"[任务1] 已生成中间文件: {intermediate_path1}")

        return intermediate_path1, log_lines, status

    except Exception as e:
        log_lines.append(f"[任务1] 发生错误: {str(e)}")
        status = 'failed'
        return None, log_lines, status

def task2(intermediate_path1, project_folder, document_type):
    log_lines = ["[任务2] 开始场景生成"]
    status = 'success'

    try:
        if not os.path.exists(intermediate_path1):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path1}")
        with open(intermediate_path1, "r", encoding="utf-8") as f:
            preprocess_json = json.load(f)
        preprocess_data = preprocess_json.get("data", {})
        requirements_list = preprocess_data.get("requirements", [])
        if not isinstance(requirements_list, list) or not requirements_list:
            raise ValueError("输入文件中 requirements 为空或格式错误")
        normalized_requirements = []
        requirements_text = ""
        for req in requirements_list:
            rule_id = req.get("rule", "")
            source_id = req.get("sourceId", "")
            text = req.get("text", "")
            normalized_requirements.append({
                "rule": rule_id,
                "sourceId": source_id,
                "text": text
            })
            requirements_text += f"rule {rule_id}\nsourceId {source_id}\n{text}\n\n"
        sco = preprocess_data.get("sco", [])
        market_variety = preprocess_data.get("market_variety", {})
        if not isinstance(sco, list):
            raise ValueError("输入文件中 sco 格式错误，应为数组")
        if not isinstance(market_variety, dict):
            raise ValueError("输入文件中 market_variety 格式错误，应为对象")
        payload = {
            "requirements": normalized_requirements,
            "sco": sco,
            "market_variety": market_variety
        }
        fallback_payload = {
            "requirements": requirements_text,
            "sco": sco,
            "market_variety": market_variety
        }
        request_payload_filename = "2_request_payload_new.json" if document_type == "new" else "2_request_payload.json"
        request_payload_path = os.path.join(project_folder, request_payload_filename)
        with open(request_payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        url = "http://219.228.60.68:9092/scenario_generation"
        log_lines.append(f"[任务2] 正在请求接口: {url}")
        print("请求", url, "已发送")
        response = requests.post(url, json=payload, timeout=(30,3000))
        if response.status_code != 200:
            log_lines.append(f"[任务2] 数组模式状态码异常: {response.status_code}，尝试字符串模式回退")
            response = requests.post(url, json=fallback_payload, timeout=(30,600))
            if response.status_code != 200:
                log_lines.append(f"[任务2] 接口返回状态码异常: {response.status_code}")
                log_lines.append(f"[任务2] 响应体: {response.text}")
                status = 'failed'
                raise RuntimeError(f"接口返回错误状态码 {response.status_code}")
        resp_json = response.json()
        status_code = resp_json.get("code")
        data_field = resp_json.get("data")
        msg = resp_json.get("msg")
        if status_code != 200 or not data_field:
            log_lines.append(f"[任务2] 数组模式返回异常: status_code={status_code}, msg={msg}，尝试字符串模式回退")
            response = requests.post(url, json=fallback_payload, timeout=(30,600))
            if response.status_code != 200:
                log_lines.append(f"[任务2] 字符串模式状态码异常: {response.status_code}")
                log_lines.append(f"[任务2] 响应体: {response.text}")
                status = 'failed'
                raise RuntimeError(f"接口返回错误状态码 {response.status_code}")
            resp_json = response.json()
            status_code = resp_json.get("code")
            data_field = resp_json.get("data")
            msg = resp_json.get("msg")
            if status_code != 200 or not data_field:
                log_lines.append(f"[任务2] 接口内部返回异常: status_code={status_code}")
                log_lines.append(f"[任务2] msg={msg}")
                log_lines.append(f"[任务2] data={data_field}")
                raise ValueError("接口返回内容异常或为空")
        output_filename = "2_out_new.json" if document_type == "new" else "2_out.json"
        intermediate_path3 = os.path.join(project_folder, output_filename)
        with open(intermediate_path3, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)
        log_lines.append(f"[任务2] 已生成中间文件: {intermediate_path3}")
        return intermediate_path3, log_lines, status

    except Exception as e:
        log_lines.append(f"[任务2] 发生错误: {str(e)}")
        status = 'failed'
        return None, log_lines, status

def task3(intermediate_path2, project_folder, old_test_case_path):
    log_lines = ["[任务3] 开始测试用例对齐"]
    status = 'success'

    try:
        # 检查输入文件
        if not os.path.exists(intermediate_path2):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path2}")

        # 读取 intermediate_path2 内容
        with open(intermediate_path2, "r", encoding="utf-8") as f:
            rule_filter_json = json.load(f)
        rule_filter_data = rule_filter_json.get("data", {})

        # 直接读取 scenarios（接口要求为数组）
        scenarios = rule_filter_data.get("scenarios", [])
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("scenarios 为空或格式错误，无法进行测试用例对齐")

        # 读取 old_test_case_path 文件内容
        if not old_test_case_path or not os.path.exists(old_test_case_path):
            raise FileNotFoundError(f"找不到测试用例文件：{old_test_case_path}")

        with open(old_test_case_path, "r", encoding="utf-8") as f:
            testcases_data = json.load(f)

        # 获取并规范化 testcases（接口要求为数组）
        # testcases_data = testcases_data.get("data", {})
        testcases = testcases_data
        if not isinstance(testcases, list) or not testcases:
            raise ValueError("testcases 为空或格式错误，无法进行测试用例对齐")

        # 构建请求数据
        payload = {
            "scenarios": scenarios,
            "testcases": testcases
        }

        # 保存请求体到本地，便于接口调试与问题复现
        request_payload_path = os.path.join(project_folder, "3_request_payload.json")
        with open(request_payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        log_lines.append(f"[任务3] 已保存请求体: {request_payload_path}")

        # 发送POST请求
        url = "http://219.228.60.68:9092/testcase_align"
        log_lines.append(f"[任务3] 正在请求接口: {url}")
        print("请求", url, "已发送")
        response = requests.post(url, json=payload, timeout=(30,3000))
        print("请求", url, "已响应")

        # 检查响应
        if response.status_code != 200:
            log_lines.append(f"[任务3] 接口返回状态码异常: {response.status_code}")
            log_lines.append(f"[任务3] 响应体: {response.text}")
            status = 'failed'
            raise RuntimeError(f"接口返回错误状态码 {response.status_code}")

        resp_json = response.json()
        status_code = resp_json.get("code")
        data_field = resp_json.get("data")
        msg = resp_json.get("msg")
        relation = data_field.get("relation", {}) if isinstance(data_field, dict) else {}

        # 接口内部错误
        if status_code != 200 or not isinstance(data_field, dict) or not isinstance(relation, dict):
            log_lines.append(f"[任务3] 接口内部返回异常: status_code={status_code}")
            log_lines.append(f"[任务3] msg={msg}")
            log_lines.append(f"[任务3] data={data_field}")
            raise ValueError("接口返回内容异常或为空")

        # 保存输出JSON文件
        intermediate_path4 = os.path.join(project_folder, "3_out.json")
        with open(intermediate_path4, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)

        log_lines.append(f"[任务3] 已生成中间文件: {intermediate_path4}")

        return intermediate_path4, log_lines, status

    except Exception as e:
        log_lines.append(f"[任务3] 发生错误: {str(e)}")
        status = 'failed'
        return None, log_lines, status

def task4(intermediate_path1, intermediate_path2, intermediate_path3, new_test_scenarios_path, project_folder):
    log_lines = ["[任务4] 开始变更规则识别"]
    status = 'success'

    try:
        # 检查输入文件
        if not os.path.exists(intermediate_path1):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path1}")
        if not os.path.exists(intermediate_path2):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path2}")
        if not os.path.exists(intermediate_path3):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path3}")
        if not new_test_scenarios_path or not os.path.exists(new_test_scenarios_path):
            raise FileNotFoundError(f"找不到新测试场景文件：{new_test_scenarios_path}")

        # 读取 intermediate_path1 内容（旧规则文本）
        with open(intermediate_path1, "r", encoding="utf-8") as f:
            preprocess_json = json.load(f)
        preprocess_data = preprocess_json.get("data", {})
        # old_texts = [req.get("text", "") for req in preprocess_data.get("requirements", [])]
        old_texts = preprocess_data.get("rules")

        # 读取 intermediate_path2 内容（新规则文本）
        with open(intermediate_path2, "r", encoding="utf-8") as f:
            rule_filter_json = json.load(f)
        rule_filter_data = rule_filter_json.get("data", {})
        # new_texts = [req.get("text", "") for req in rule_filter_data.get("requirements", [])]
        new_texts = rule_filter_data.get("rules")

        # 读取 intermediate_path3 内容（旧场景，来源 task2 旧文档）
        with open(intermediate_path3, "r", encoding="utf-8") as f:
            old_scenarios_json = json.load(f)
        old_scenarios_data = old_scenarios_json.get("data", {})
        old_scenarios = old_scenarios_data.get("scenarios", [])
        if not isinstance(old_scenarios, list) or not old_scenarios:
            raise ValueError("旧场景数据为空或格式错误，无法进行变更规则识别")

        # 读取 new_test_scenarios_path 内容（新场景，来源 task2 新文档）
        with open(new_test_scenarios_path, "r", encoding="utf-8") as f:
            new_scenarios_json = json.load(f)
        new_scenarios_data = new_scenarios_json.get("data", {})
        new_scenarios = new_scenarios_data.get("scenarios", [])
        if not isinstance(new_scenarios, list) or not new_scenarios:
            raise ValueError("新场景数据为空或格式错误，无法进行变更规则识别")

        # 构建请求数据
        payload = {
            "old_texts": old_texts,
            "new_texts": new_texts,
            "old_scenarios": old_scenarios,
            "new_scenarios": new_scenarios
        }

        # 保存请求体到本地，便于接口调试与问题复现
        request_payload_path = os.path.join(project_folder, "4_request_payload.json")
        with open(request_payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        log_lines.append(f"[任务4] 已保存请求体: {request_payload_path}")

        # 发送POST请求
        url = "http://219.228.60.68:9092/change_identify"
        log_lines.append(f"[任务4] 正在请求接口: {url}")
        print("请求", url, "已发送")
        response = requests.post(url, json=payload, timeout=(30,3000))
        print("请求", url, "已响应")

        # 检查响应
        if response.status_code != 200:
            log_lines.append(f"[任务4] 接口返回状态码异常: {response.status_code}")
            log_lines.append(f"[任务4] 响应体: {response.text}")
            status = 'failed'
            raise RuntimeError(f"接口返回错误状态码 {response.status_code}")

        resp_json = response.json()
        status_code = resp_json.get("code")
        data_field = resp_json.get("data")
        msg = resp_json.get("msg")
        to_delete_rules = data_field.get("to_delete_rules", []) if isinstance(data_field, dict) else []
        to_add_rules = data_field.get("to_add_rules", []) if isinstance(data_field, dict) else []
        new_map = data_field.get("new_map", {}) if isinstance(data_field, dict) else {}

        # 接口内部错误
        if (
            status_code != 200
            or not isinstance(data_field, dict)
            or not isinstance(to_delete_rules, list)
            or not isinstance(to_add_rules, list)
            or not isinstance(new_map, dict)
        ):
            log_lines.append(f"[任务4] 接口内部返回异常: status_code={status_code}")
            log_lines.append(f"[任务4] msg={msg}")
            log_lines.append(f"[任务4] data={data_field}")
            raise ValueError("接口返回内容异常或为空")

        # 保存输出JSON文件
        intermediate_path5 = os.path.join(project_folder, "4_out.json")
        with open(intermediate_path5, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)

        log_lines.append(f"[任务4] 已生成中间文件: {intermediate_path5}")

        return intermediate_path5, log_lines, status

    except Exception as e:
        log_lines.append(f"[任务4] 发生错误: {str(e)}")
        status = 'failed'
        return None, log_lines, status

def task5(intermediate_path3, intermediate_path4, intermediate_path5, project_folder):
    log_lines = ["[任务5] 开始变更影响分析"]
    status = 'success'

    try:
        # 检查输入文件
        if not os.path.exists(intermediate_path3):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path3}")
        if not os.path.exists(intermediate_path4):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path4}")
        if not os.path.exists(intermediate_path5):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path5}")

        # 读取 intermediate_path3 内容（旧场景，来源 task2 旧文档）
        with open(intermediate_path3, "r", encoding="utf-8") as f:
            old_scenarios_json = json.load(f)
        old_scenarios_data = old_scenarios_json.get("data", {})
        old_scenarios = old_scenarios_data.get("scenarios", [])
        if not isinstance(old_scenarios, list) or not old_scenarios:
            raise ValueError("old_scenarios 为空或格式错误，无法进行变更影响分析")

        # 读取 intermediate_path5 内容（待删除规则）
        with open(intermediate_path5, "r", encoding="utf-8") as f:
            change_rule_json = json.load(f)
        change_rule_data = change_rule_json.get("data", {})
        to_delete_rules = change_rule_data.get("to_delete_rules", [])

        # 读取 intermediate_path4 内容（旧规则与测试用例的关联关系，来源 task3）
        with open(intermediate_path4, "r", encoding="utf-8") as f:
            old_relation_json = json.load(f)
        old_relation_data = old_relation_json.get("data", {})
        old_relation = old_relation_data.get("relation", {})
        if not isinstance(old_relation, dict):
            raise ValueError("old_relation 格式错误，应为对象")

        # 构建请求数据
        payload = {
            "old_scenarios": old_scenarios,
            "to_delete_rules": to_delete_rules,
            "old_relation": old_relation
        }

        # 保存请求体到本地，便于接口调试与问题复现
        request_payload_path = os.path.join(project_folder, "5_request_payload.json")
        with open(request_payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        log_lines.append(f"[任务5] 已保存请求体: {request_payload_path}")

        # 发送POST请求
        url = "http://219.228.60.68:9092/impact_analysis"
        log_lines.append(f"[任务5] 正在请求接口: {url}")
        print("请求", url, "已发送")
        response = requests.post(url, json=payload, timeout=(30,3000))
        print("请求", url, "已响应")

        # 检查响应
        if response.status_code != 200:
            log_lines.append(f"[任务5] 接口返回状态码异常: {response.status_code}")
            log_lines.append(f"[任务5] 响应体: {response.text}")
            status = 'failed'
            raise RuntimeError(f"接口返回错误状态码 {response.status_code}")

        resp_json = response.json()
        status_code = resp_json.get("code")
        data_field = resp_json.get("data")
        msg = resp_json.get("msg")
        to_delete_linked_scenario = data_field.get("to_delete_linked_scenario", []) if isinstance(data_field, dict) else []
        to_delete_testcases = data_field.get("to_delete_testcases", []) if isinstance(data_field, dict) else []

        # 接口内部错误
        if (
            status_code != 200
            or not isinstance(data_field, dict)
            or not isinstance(to_delete_linked_scenario, list)
            or not isinstance(to_delete_testcases, list)
        ):
            log_lines.append(f"[任务5] 接口内部返回异常: status_code={status_code}")
            log_lines.append(f"[任务5] msg={msg}")
            log_lines.append(f"[任务5] data={data_field}")
            raise ValueError("接口返回内容异常或为空")

        # 保存输出JSON文件
        intermediate_path6 = os.path.join(project_folder, "5_out.json")
        with open(intermediate_path6, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)

        log_lines.append(f"[任务5] 已生成中间文件: {intermediate_path6}")

        return intermediate_path6, log_lines, status

    except Exception as e:
        log_lines.append(f"[任务5] 发生错误: {str(e)}")
        status = 'failed'
        return None, log_lines, status

def task6(intermediate_path2, new_test_scenarios_path, intermediate_path4, intermediate_path5, old_test_case_path, project_folder):
    log_lines = ["[任务6] 开始测试用例更新"]
    status = 'success'

    try:
        # 检查输入文件
        if not os.path.exists(intermediate_path2):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path2}")
        if not os.path.exists(new_test_scenarios_path):
            raise FileNotFoundError(f"找不到输入文件：{new_test_scenarios_path}")
        if not os.path.exists(intermediate_path4):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path4}")
        if not os.path.exists(intermediate_path5):
            raise FileNotFoundError(f"找不到输入文件：{intermediate_path5}")
        if not old_test_case_path or not os.path.exists(old_test_case_path):
            raise FileNotFoundError(f"找不到旧测试用例文件：{old_test_case_path}")

        # 读取 intermediate_path2 内容（新规则文本、新sco、新market_variety）
        with open(intermediate_path2, "r", encoding="utf-8") as f:
            rule_filter_json = json.load(f)
        rule_filter_data = rule_filter_json.get("data", {})
        new_texts = rule_filter_data.get("rules")
        if not isinstance(new_texts, list):
            raise ValueError("new_texts 格式错误，应为数组")

        new_sco = rule_filter_data.get("sco", [])
        new_market_variety = rule_filter_data.get("market_variety", {})
        if not isinstance(new_sco, list):
            raise ValueError("new_sco 格式错误，应为数组")
        if not isinstance(new_market_variety, dict):
            raise ValueError("new_market_variety 格式错误，应为对象")
        
        # new_scenarios 按文档应为场景对象数组，优先从 task2 输出的 scenarios 读取
        with open(new_test_scenarios_path, "r", encoding="utf-8") as f:
            scenarios_filter_json = json.load(f)
        scenarios_filter_json_data = scenarios_filter_json.get("data", {})
        new_scenarios = scenarios_filter_json_data.get("scenarios")
        if not isinstance(new_scenarios, list) or not new_scenarios:
            raise ValueError("new_scenarios 为空或格式错误，无法进行测试用例更新")

        # 读取 intermediate_path4 内容（旧规则与测试用例的关联关系）
        with open(intermediate_path4, "r", encoding="utf-8") as f:
            testcase_alignment_json = json.load(f)
        testcase_alignment_data = testcase_alignment_json.get("data", {})
        old_relation = testcase_alignment_data.get("relation", {})
        if not isinstance(old_relation, dict):
            raise ValueError("old_relation 格式错误，应为对象")

        # 读取 intermediate_path4 内容（变更规则识别结果）
        with open(intermediate_path5, "r", encoding="utf-8") as f:
            change_rule_json = json.load(f)
        change_rule_data = change_rule_json.get("data", {})
        to_delete_rules = change_rule_data.get("to_delete_rules")
        to_add_rules = change_rule_data.get("to_add_rules")
        new_map = change_rule_data.get("new_map", {})
        if not isinstance(to_delete_rules, list):
            raise ValueError("to_delete_rules 格式错误，应为数组")
        if not isinstance(to_add_rules, list):
            raise ValueError("to_add_rules 格式错误，应为数组")
        if not isinstance(new_map, dict):
            raise ValueError("new_map 格式错误，应为对象")

        # 读取 old_test_case_path 内容（旧测试用例）
        with open(old_test_case_path, "r", encoding="utf-8") as f:
            old_testcases_data = json.load(f)
        old_testcases = old_testcases_data
        if not isinstance(old_testcases, list) or not old_testcases:
            raise ValueError("old_testcases 为空或格式错误，无法进行测试用例更新")

        # 构建请求数据
        payload = {
            "new_texts": new_texts,
            "new_scenarios": new_scenarios,
            "to_delete_rules": to_delete_rules,
            "to_add_rules": to_add_rules,
            "old_relation": old_relation,
            "old_testcases": old_testcases,
            "new_map": new_map,
            "new_sco": new_sco,
            "new_market_variety": new_market_variety
        }

        # 保存请求体到本地，便于接口调试与问题复现
        request_payload_path = os.path.join(project_folder, "6_request_payload.json")
        with open(request_payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        log_lines.append(f"[任务6] 已保存请求体: {request_payload_path}")

        # 发送POST请求
        url = "http://219.228.60.68:9092/testcase_update"
        log_lines.append(f"[任务6] 正在请求接口: {url}")
        print("请求", url, "已发送")
        response = requests.post(url, json=payload, timeout=(30,3000))
        print("请求", url, "已响应")


        # 检查响应
        if response.status_code != 200:
            log_lines.append(f"[任务6] 接口返回状态码异常: {response.status_code}")
            log_lines.append(f"[任务6] 响应体: {response.text}")
            status = 'failed'
            raise RuntimeError(f"接口返回错误状态码 {response.status_code}")

        resp_json = response.json()
        status_code = resp_json.get("code")
        data_field = resp_json.get("data")
        msg = resp_json.get("msg")
        testcases = data_field.get("testcases", []) if isinstance(data_field, dict) else []

        # 接口内部错误
        if status_code != 200 or not isinstance(data_field, dict) or not isinstance(testcases, list):
            log_lines.append(f"[任务6] 接口内部返回异常: status_code={status_code}")
            log_lines.append(f"[任务6] msg={msg}")
            log_lines.append(f"[任务6] data={data_field}")
            raise ValueError("接口返回内容异常或为空")

        # 保存输出JSON文件
        intermediate_path6 = os.path.join(project_folder, "6_out.json")
        with open(intermediate_path6, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)

        log_lines.append(f"[任务6] 已生成中间文件: {intermediate_path6}")

        return intermediate_path6, log_lines, status

    except Exception as e:
        log_lines.append(f"[任务6] 发生错误: {str(e)}")
        status = 'failed'
        return None, log_lines, status

# if __name__ == '__main__':
    # task1("","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test")
    # intermediate_path2, log_lines, status = task2("D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test/preprocess_file.json","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test")
    # intermediate_path3, log_lines, status = task3("D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test/rule_filter_file.json","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test")
    # intermediate_path4, log_lines, status = task4("D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test/preprocess_file.json","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test/rule_element_extraction_file.json","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test")
    # intermediate_path5, log_lines, status = task5("D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test/rule_assembly_file.json","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test")
    # intermediate_path6, log_lines, status = task6("D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test/r1_to_r2_file.json","D:/projects/pythonProjects/ECNUProject/zhengquan_flask_vue/app/projects_test")
    # print(intermediate_path6)

