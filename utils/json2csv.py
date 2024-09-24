import os
import json
import pandas as pd

# 定义 JSON 文件所在的目录
directory = "/LLM-Medical-Agent/data/answer_100(4)"

# 初始化一个空的列表来存储数据
data = []

# 遍历目录中的所有文件
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".json"):
            # 从文件路径中提取目标药品和 PMID
            drug = os.path.basename(root)
            pmid = file.split('.')[0]

            file_path = os.path.join(root, file)
            with open(file_path, 'r') as json_file:
                # 读取 JSON 文件
                json_data = json.load(json_file)
                json_data['drug'] = drug
                json_data['pmid'] = pmid
                
                # 处理 question_list，将其键值对转换为单独的列
                for key, value in json_data.get("question_list", {}).items():
                    json_data[key] = value
                # 添加目标药品和 PMID 到 JSON 数据中
                if "question_list" in json_data:
                    del json_data["question_list"]
                if "patient_age" in json_data:
                    del json_data["patient_age"]
                if "drug_route" in json_data:
                    del json_data["drug_route"]
                if "disease_icd10" in json_data:
                    del json_data["disease_icd10"]
                desired_order = ['drug', 'pmid', 'abstract', 'includes_pediatrics', 'proves_effective','process_pediatrics_inabstract', 'process_effectiveness','process_pediatrics_incontent','process_population_effectiveness','remain_problem']
                json_data = {key: json_data[key] for key in desired_order if key in json_data}
                # 将 JSON 数据添加到列表中
                data.append(json_data)
            
# 将数据转换为 DataFrame
df = pd.DataFrame(data)

# 将 DataFrame 保存为 CSV 文件
csv_file_path = "/LLM-Medical-Agent/data/output6.csv"
df.to_csv(csv_file_path, index=False)

print(f"CSV 文件已保存到 {csv_file_path}")