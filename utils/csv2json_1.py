import pandas as pd
import json
# import ipdb
# ipdb.set_trace()
# 读取 Excel 文件的第二个表格
file_path = '/LLM-Medical-Agent/data/output_modified.xlsx'  # 替换为你的 Excel 文件路径
sheet_name = 1  # 表示读取第二个工作表（从 0 开始计数）

# 使用 pandas 读取 Excel 文件的第二个工作表
df = pd.read_excel(file_path, sheet_name=sheet_name)

# 创建或打开 jsonl 文件
jsonl_file_path = '/LLM-Medical-Agent/data/output.jsonl'  # 替换为你想要保存的 jsonl 文件路径

# 将每一行数据转换为 JSON 格式，并写入 jsonl 文件
with open(jsonl_file_path, 'w', encoding='utf-8') as jsonl_file:
    for index, row in df.iterrows():
        json_record = row.to_dict()  # 将一行数据转换为字典
        jsonl_file.write(json.dumps(json_record, ensure_ascii=False) + '\n')  # 写入 JSONL 文件

print(f"数据已成功保存到 {jsonl_file_path}")