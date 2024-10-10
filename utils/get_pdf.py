import os
import json





def get_pmid_of_need_pdf(path="/Users/cqs/Documents/研究生学习/代码/LLM-Medical-Agent/data/answer",save_path = "/Users/cqs/Documents/研究生学习/代码/LLM-Medical-Agent/data/need_pdf.json"):
    pdfs = []
    for root,_,files in os.walk(path):
        for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if data["state"]["need_to_fetch_conent"] == False:
                        name_pmid = {"name":data["base_info"]["drug_name"],"pmid":data["base_info"]["abstract_url"]}
                        pdfs.append(name_pmid)
        with open(save_path, "w") as f:
            json.dump(pdfs, f)
    

