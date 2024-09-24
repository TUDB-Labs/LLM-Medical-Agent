import os
import json
def get_abstract_exist(name,pmid):
    path = os.path.join("/LLM-Medical-Agent/data/answer_100/",name,pmid + ".json") 
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        abstract = data["abstract"]
        return abstract
    return None

