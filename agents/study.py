import requests
import json
from models.gpt import *
from bs4 import BeautifulSoup
import html2text
import json
import os
import tiktoken
import logging

from utils.find_relative_chunk import find_relative_chunk
enc = tiktoken.get_encoding("cl100k_base")
class Study:

    def __init__(self, abstract_url,drug_name,compressor):
        self.abstract_url = abstract_url
        self.drug_name = drug_name
        self.compressor = compressor
        self.data = {
            "abstract": "",
            "includes_pediatrics": False,
            "proves_effective": False,
            "patient_age": "",
            "disease_icd10": "",
            "drug_route": "",
            "question_list": {}
        }
        self.data["question_list"]["process_pediatrics_inabstract"] = False
        self.data["question_list"]["process_effectiveness"] = False
        self.data["question_list"]["process_pediatrics_incontent"] = False
        self.data["question_list"]["process_population_effectiveness"] = False
        self.data["question_list"]["remain_problem"] = False



    def fetch_abstract(self):
        url = 'https://pubmed.ncbi.nlm.nih.gov/' + self.abstract_url + "/" 
        try:
            response = requests.get(url)
            if response.status_code == 200:
            # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser') 
                abstract_div = soup.find('div', class_='abstract-content selected', id='eng-abstract')
                if abstract_div is not None:
                    html_abstract = abstract_div.get_text()
                else:
                    logging.error(f"drug name:{self.drug_name}'s paper{self.abstract_url} not have abstract")
                    return False
                markdown = html2text.html2text(html_abstract)  
                self.data["abstract"] = markdown
                logging.info(f"Abstract: {markdown} have been fetched.")
                return True
        except requests.RequestException as e:
            logging.error(f"Error fetching abstract: {e}")
            return False



    def process_pediatrics_inabstract(self):
        json_object = {"reason":"","short_answer":""}
        prompt = "##INSTRUCTION:Based on the abstract , is this study exploring the effectiveness of the drug in the pediatric population?your answer must is in [yes,no,age_not_mentioned]\n##ABSTRACT:{abstract}\n##model generated chain of thought explanation.\nTherefore, the json format answer is json:{json}"
        prompt = prompt.format(abstract=self.data["abstract"],json=json_object)
        prompt_dict = {}
        prompt_dict["prompt"] = prompt
        result = gpt_request_from_relative_chunk(prompt_dict)
        try:
            json_object = json.loads(result)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return None

        return json_object

    def process_effectiveness(self):
        json_object = {"reason":"","short_answer":""}
        prompt = "##INSTRUCTION:Based on the abstract, does this study demonstrate that the drug{drug_name} is effective in the pediatric population?your answer must is in [yes,no]\n##ABSTRACT:{abstract}\n##model generated chain of thought explanation.\nTherefore, the json format answer is json:{json}"
        prompt = prompt.format(abstract=self.data["abstract"],json=json_object,drug_name="vd")
        prompt_dict = {}
        prompt_dict["prompt"] = prompt
        result = gpt_request_from_relative_chunk(prompt_dict)
        try:
            json_object = json.loads(result)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return None

        return json_object

 

    def process_pediatrics_incontent(self):
        json_object = {"reason":"","short_answer":""}
        question = "did the pediatric population be included in this study?"
        relative_chunk = find_relative_chunk( "/root/medical/makedata/chunk_with_target_grug/albumin/11002872.json",question)
        content = []
        all_token = 0
        for key, value in relative_chunk.items():
            content.append(value)
            all_token =  all_token + len(enc.encode(value) )
        contents = '\n'.join(content)
        if all_token >5000:
            print("all_token lenght:" + str(all_token))
            contents = self.compressor.compress_prompt_llmlingua2(
                contents,
                rate=0.6,
                target_token = 5000,
                chunk_end_tokens=['.', '\n'],
                return_word_label=True,
                drop_consecutive=True
            )
        prompt = "##INSTRUCTION:According to the relative information, did the pediatric population be included in this study?your answer must is in [yes,no]\n##Relative information:{relative_chunk}\n##model generated chain of thought explanation.\nTherefore, the json format answer is json:{json}"
        prompt = prompt.format(relative_chunk= contents,json=json_object)
        prompt_dict = {}
        prompt_dict["prompt"] = prompt
        result = gpt_request_from_relative_chunk(prompt_dict)
        try:
            json_object = json.loads(result)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return None
        return json_object

    def process_population_effectiveness(self):
        json_object = {"reason":"","short_answer":""}
        prompt = "##INSTRUCTION:Based on the abstract, does this study demonstrate that the drug{drug_name} is effective in the population?your answer must is in [yes,no]\n##ABSTRACT:{abstract}\n##model generated chain of thought explanation.\nTherefore, the json format answer is json:{json}"
        prompt = prompt.format(drug_name = self.drug_name,abstract=self.data["abstract"],json=json_object)
        prompt_dict = {}
        prompt_dict["prompt"] = prompt
        result = gpt_request_from_relative_chunk(prompt_dict)
        try:
            json_object = json.loads(result)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return None
        return json_object

    def ask_remain_question(self):
        self.data["question_list"]["remain_problem"] = True





    def gather_details(self):
        return self.data

    def save_to_json(self, filename):
        directory_path = os.path.dirname(filename)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path,exists_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=4)
