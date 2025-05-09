from langchain_core.output_parsers import JsonOutputParser
import re
import json


def extract_json(content, response_format):
    parser = JsonOutputParser(pydantic_object=response_format)
    response = None

    try:
        if isinstance(content, str) and "```" in content:
            print("================ Resposta é uma string com JSON ================")
            pattern = r"```(?:json)?\s*({.*?})\s*```"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                raw_json_str = match.group(1)
                parsed = parser.parse(raw_json_str)
                response = response_format(**parsed)

        elif isinstance(content, str):
            print("================ Resposta é uma string ================")
            json_start = content.find('{')
            if json_start != -1:
                raw_json_str = content[json_start:]
                parsed = json.loads(raw_json_str)
                response = response_format(**parsed)

        else:
            print("================ Resposta não é uma string ou JSON válido ================")
            print(content)
            
        return response

    except Exception as e:
        print("Erro ao parsear JSON:", e)
        print("Resposta bruta:", content)
