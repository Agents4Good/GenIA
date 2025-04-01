import json
import os
from plantuml import PlantUML

def json_to_plantuml(data: str) -> str:
    """
    Converte um JSON de agentes e interações para um diagrama de sequência em PlantUML.
    """
    data = json.loads(data)

    plantuml_code = """
    @startuml

    ' Definição dos agentes
    """
    
    agents = {agent["agent"] for agent in data["agents"]}
    for agent in agents:
        plantuml_code += f"participant {agent}\n"
    
    plantuml_code += "\n' Definição das interações\n"
    
    for interaction in data["interactions"]:
        source = interaction["source"]
        target = interaction["targets"]
        description = interaction["description"]
        plantuml_code += f"{source} -> {target}: {description}\n"
    
    plantuml_code += "@enduml"
    
    return plantuml_code

def generate_diagram(plantuml_code, output_dir="GenIA/generated_files"):
    """Salva o código PlantUML em um arquivo e gera o diagrama"""
    puml_file = os.path.join(output_dir, "sequence_diagram.puml")

    with open(puml_file, "w", encoding="utf-8") as f:
        f.write(plantuml_code)

    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")

    plantuml_server.processes_file(puml_file)