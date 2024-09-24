import requests
import json
from bs4 import BeautifulSoup
import html2text
import json
import os
from utils.log import CustomLogger
from utils.get_abstract_exist import get_abstract_exist
from datetime import datetime
from agents.study import Study
import ipdb
from llmlingua import PromptCompressor
# 示例研究数据
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# 创建日志文件名
log_filename = f"log_{current_time}.log"
logger = CustomLogger("/LLM-Medical-Agent/log/"+log_filename)
compressor = PromptCompressor(
model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
use_llmlingua2=True
)

with open("/LLM-Medical-Agent/data/pmid_with_name.jsonl","r",encoding="utf-8") as f:
    """
    pmid_with_name.jsonl:
    {"英文通用名": ["Tobramycin", "dexamethasone"], "pmid": "12122630"}
    ...
    """
    for line in f:
        json_obj = json.loads(line.strip())
        name = ""
        for i in range(len(json_obj["英文通用名"])):
            name =name + json_obj["英文通用名"][i]+"_"
        name = name[:-1] 
        pmid = json_obj["pmid"]
        save_path = os.path.join("/LLM-Medical-Agent/data/answer_100(4)",name,pmid + ".json") 
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if data["question_list"]["process_pediatrics_incontent"] == False:
                    continue
        study_data = Study(pmid,name,compressor) 

        # 尝试获取摘要
        abstract = get_abstract_exist(name,pmid)
        if study_data.fetch_abstract(abstract):
            # 流程控制
            result = study_data.process_pediatrics_inabstract()
            logger.log_info(f"{name}_{pmid} process_pediatrics_inabstract: {result}")
            study_data.data["question_list"]["process_pediatrics_inabstract"] = True
            if result["short_answer"].lower() == "included":
                study_data.data["includes_pediatrics"] = True
                result = study_data.process_effectiveness()
                logger.log_info(f"{name}_{pmid} process_effectiveness: {result}")
                study_data.data["question_list"]["process_effectiveness"] = True
                if result["short_answer"].lower() == "yes":
                    study_data.data["proves_effective"] = True
                    # continue to ask question remain
                    study_data.ask_remain_question()
                    
            elif result["short_answer"].lower() == "age_not_mentioned":
                result = study_data.process_pediatrics_incontent()   
                logger.log_info(f"{name}_{pmid} process_pediatrics_incontent: {result}")
                study_data.data["question_list"]["process_pediatrics_incontent"] = True
                if result["short_answer"] == "yes": 
                    study_data.data["includes_pediatrics"] = True
                    result = study_data.process_population_effectiveness()
                    logger.log_info(f"{name}_{pmid} process_population_effectiveness: {result}")
                    study_data.data["question_list"]["process_population_effectiveness"] = True
                    if result["short_answer"] =="yes":
                        study_data.data["proves_effective"] = True
                        # continue to ask question remain
                        study_data.ask_remain_question()

            #save the answer to json
            details = study_data.gather_details()
            print(details)
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path),exist_ok=True)
            study_data.save_to_json(save_path)  # 保存到JSON文件
        else:
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path),exist_ok=True)
            study_data.save_to_json(save_path)  # 保存到JSON文件
            print("Failed to fetch abstract.")