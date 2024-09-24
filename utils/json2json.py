import json

# 定义读取jsonl文件的函数
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data

# 定义写入新的jsonl文件的函数
def write_jsonl(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        for entry in data:
            # ensure_ascii=False 避免 Unicode 转义，将中文等字符正常保存
            file.write(json.dumps(entry, ensure_ascii=False) + '\n')

# 定义处理json数据的函数，删除某些键并重命名键
def process_json_data(data, keys_to_remove, rename_mapping):
    processed_data = []
    for entry in data:
        # 删除指定的键
        for key in keys_to_remove:
            if key in entry:
                del entry[key]
        
        # 重命名键
        for old_key, new_key in rename_mapping.items():
            if old_key in entry:
                entry[new_key] = entry.pop(old_key)
        
        processed_data.append(entry)
    
    return processed_data

# 示例：读取原始jsonl文件，处理后写入新的jsonl文件
input_file = '/LLM-Medical-Agent/data/output.jsonl'
output_file = '/LLM-Medical-Agent/data/output1.jsonl'

# 要删除的键列表
keys_to_remove = ['Unnamed: 4', 'Unnamed: 5', 'Unnamed: 7','应该把level4的提出来…']

# 要重命名的键，格式为 {'旧键名': '新键名'}
rename_mapping = {
    'Unnamed: 0': '文献序号',
    'Unnamed: 1': '中文药品名',
    'Unnamed: 2': 'drug',
    'Unnamed: 3': 'pmid',
    'Unnamed: 6': 'url'
}

# 读取数据
json_data = read_jsonl(input_file)

# 处理数据：删除键值对并重命名键
processed_data = process_json_data(json_data, keys_to_remove, rename_mapping)

# 写入新的jsonl文件
write_jsonl(output_file, processed_data)

print(f"数据已成功处理并写入到 {output_file}")