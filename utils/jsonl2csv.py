import json
import csv

# 读取 jsonl 文件
input_file = '/LLM-Medical-Agent/data/output1.jsonl'
output_file = '/LLM-Medical-Agent/data/output3.csv'

# 打开 jsonl 文件和 csv 文件
with open(input_file, 'r', encoding='utf-8') as jsonl_file, open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
    # 读取 jsonl 的第一行，解析键（列名）
    first_line = json.loads(jsonl_file.readline())
    fieldnames = list(first_line.keys())
    
    # 创建 csv 写入器
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 写入第一行数据
    writer.writerow(first_line)
    
    # 继续读取后面的 jsonl 行，写入 csv
    for line in jsonl_file:
        json_obj = json.loads(line)
        writer.writerow(json_obj)