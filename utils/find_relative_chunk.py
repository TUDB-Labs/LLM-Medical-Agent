from models.gpt import *
from json import loads, dumps
import os
import json
import random
from transformers import AutoTokenizer
import logging
import spacy
from rank_bm25 import BM25Okapi
from concurrent.futures import ProcessPoolExecutor
logging.basicConfig(filename="relativechunk.log",  # 将日志保存到filename文件中 
                    level=logging.INFO) 

#only llm,return relative chunk
def find_relative_chunk(paper_name, question, prompt = "Given the question and the document below, does the document provide information that would be useful in answering the question? Please respond with either 'Yes' or 'No' only."):
    try:
        with open(paper_name, 'r', encoding='utf-8') as f:  
            relative_chunk = {}
            datas=loads(f.read())
            relative_state = gpt_request_demo(datas, question, prompt)
            for key, value in relative_state.items():
                if value.lower() == "yes":
                    relative_chunk[key] = datas[key]
            return relative_chunk
    except Exception as e:
        logging.info(e)
        return {}
        
#
def question2relative_chunk_1(paper_name, question_list, prompt = "Given the question and the document below, does the document provide information that would be useful in answering the question? Please respond with either 'Yes' or 'No' only."):
    pass


def find_most_relevant_key_bm25(query, json_file_path):
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # 假设JSON文件是一个字典，其中每个键对应一个文本值
    texts = {key: value for key, value in data.items()}
    # 创建BM25模型
    model = BM25Okapi(texts.values())
    # 计算每个键的BM25得分
    scores = model.get_scores(query)
    # 找出得分最高的键
    ipdb.set_trace()
    most_relevant_key = [key for key, score in zip(texts.keys(), scores) if score == max(scores)][0]
    return most_relevant_key




def extract_gpe_entities_from_json(file_path):
    """
    从给定的JSON文件中提取地理政治实体（GPE）实体。

    参数:
    file_path (str): JSON文件的路径。

    返回:
    list: 识别出的GPE实体列表。
    """
    # 初始化一个空列表来存储GPE实体
    gpe_entities = []

    # 尝试打开并读取JSON文件
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return gpe_entities
    except json.JSONDecodeError:
        print(f"文件不是有效的JSON格式: {file_path}")
        return gpe_entities
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return gpe_entities

    # 初始化一个字符串来存储所有文本
    all_text = ""

    # 遍历字典，提取所有文本
    for value in data.values():
        if isinstance(value, str):
            all_text += value

    # 使用SpaCy处理所有文本
    doc = nlp(all_text)

    # 查找并添加GPE实体
    for ent in doc.ents:
        if ent.label_ == "GPE":
            gpe_entities.append(ent.text)

    return gpe_entities
