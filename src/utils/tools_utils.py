import yaml
from pathlib import Path

def insert_node_yaml(file: Path, node: dict):
    with open(file, "r") as infile:
        data = yaml.safe_load(infile)

    data["workflow"]["graph"]["nodes"].append(node)

    with open(file, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)


def insert_edge_yaml(file: Path, edge: dict):
    with open(file, "r") as infile:
        data = yaml.safe_load(infile)

    data["workflow"]["graph"]["edges"].append(edge)

    with open(file, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)