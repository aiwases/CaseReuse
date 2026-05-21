import json
import os


def split_path(path: str):
    """拆分 4.2.6.2,4.2.5.2,... 为多级链"""
    return [p.strip() for p in path.split(',') if p.strip()]


def load_intermediate6(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"intermediate6 file not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_rule_graph_from_project(project):
    """
    project: Project ORM 对象
    """
    data = load_intermediate6(project.intermediate_path6)

    nodes = {}
    edges = set()

    def add_node(node_id, node_type, label=None, raw=None):
        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label": label or node_id,
                "raw": raw
            }

    def add_edge(src, tgt):
        edges.add((src, tgt))

    for item in data:
        rule_id = item["rule"]

        # 规则节点
        add_node(
            node_id=rule_id,
            node_type="rule",
            label=item.get("focus", rule_id),
            raw={
                "rule": rule_id,
                "focus": item.get("focus"),
                "sourceId": item.get("sourceId"),
                "text": item.get("text")
            }
        )

        # before → rule
        for b in item.get("before", []):
            add_node(b, "before")
            add_edge(b, rule_id)

        # rule → after（多级）
        for after_path in item.get("after", []):
            parts = split_path(after_path)
            prev = rule_id
            for p in parts:
                add_node(p, "after")
                add_edge(prev, p)
                prev = p

    return {
        "nodes": list(nodes.values()),
        "edges": [
            {"source": s, "target": t}
            for s, t in edges
        ]
    }
