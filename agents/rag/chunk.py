# 导入必要的库，用于文件操作、数据处理和标记语言处理
import tiktoken
import os
import json
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter, CharacterTextSplitter
# from get_abstract import get_abstract

# 定义输入、输出和保存路径，以及处理块大小和重叠参数
# 建议将这些路径作为参数传递或从配置文件中读取

chunk_size = 1000
chunk_overlap = 0
headers_to_split_on = [
    ("#", "Header "),
    ("##", "Header "),
    ("###", "Header "),
]

def process_markdown_files(input_path, output_path, headers_to_split_on):
    """
    处理Markdown文件，根据标题分割内容，并转换为JSON格式保存。
    
    :param input_path: Markdown文件的输入目录
    :param output_path: 生成的JSON文件的输出目录
    :param headers_to_split_on: 用于分割Markdown内容的标题级别
    """
    # 遍历输入目录中的所有文件
    for root, dirs, _ in os.walk(input_path):
        for dir in dirs:
            if dir.isdigit():
                continue
            for root1, _, files1 in os.walk(os.path.join(root, dir)):
                for file in files1:
                    # 忽略非Markdown文件
                    file_path = os.path.join(root1, file)
                    if not file.endswith(".md"):
                        continue
                    try:
                        # 读取Markdown文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            markdown_document = f.read()
                        # 使用Markdown标题分割器分割内容
                        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
                        md_header_splits = markdown_splitter.split_text(markdown_document)

                        # 组合分割后的数据到一个字典中
                        combined_dict = {}
                        for split_text in md_header_splits:
                            metadata = split_text.metadata.get('Header ', "Header")
                            page_content = re.sub(r'\n|image|Image|png|Png', '', split_text.page_content)
                            if "reference" in metadata.lower():
                                continue
                            combined_dict[metadata] = page_content

                        # 将字典转换为JSON格式，并保存到输出目录
                        info_json = json.dumps(combined_dict, sort_keys=False, indent=4, separators=(',', ': '))
                        if not os.path.exists(os.path.join(output_path,dir)):
                            os.makedirs(os.path.join(output_path,dir),exist_ok=True)
                        output_file_path = os.path.join(output_path,dir, file[:-3] + ".json")
                        with open(output_file_path, 'w', encoding='utf-8') as wfile:
                            wfile.write(info_json)
                    except IOError as e:
                        print(f"Error opening file {file_path}: {e}")

def process_chunked_files(chunk_path, save_path, text_splitter):
    """
    处理已分割的JSON文件，对超过规定大小的内容进行进一步分割。
    
    :param chunk_path: 输入的分割文件目录
    :param save_path: 输出的处理后文件目录
    :param text_splitter: 用于分割文本的工具
    """
    # 遍历输入目录中的所有文件
    for root, dirs, files in os.walk(chunk_path):
        for file in files:
            # 忽略非JSON文件
            file_path = os.path.join(root, file)
            if not file_path.endswith(".json"):
                continue
            try:
                # 读取JSON文件内容
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                abstract = get_abstract(file[:-5])
                temp_dict = abstract.copy()
                temp_dict.update(data)
                new_dict = {}
                # 对每个条目进行处理，根据长度进行分割
                for key, value in temp_dict.items():
                    if "reference" in key.lower():
                        continue


                    # if len(tiktoken.get_encoding("cl100k_base").encode(value)) > 1000:
                    #     texts = text_splitter.create_documents([value])
                    #     if len(texts) > 1:
                    #         for i in range(len(texts)):
                    #             ipdb.set_trace()
                    #             new_dict[key + str(i)] = texts[i]
                    #     else: new_dict[key] = value
                    # else:
                    new_dict[key] = value
                # 将处理后的数据保存到输出目录
                output_file_path = os.path.join(save_path, file)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(new_dict, f, ensure_ascii=False, indent=4)
            except IOError as e:
                print(f"Error opening file {file_path}: {e}")

if __name__ == "__main__":
    # 初始化字符级分割器
    input_path = "/root/medical/makedata2/data/mk_100"
    output_path = "/root/medical/makedata2/data/json_100"
    save_path = "/root/medical/makedata2/data/mk_100_2"

    process_markdown_files(input_path, output_path, headers_to_split_on)
    
    # 使用tiktoken编码器初始化分割器，用于进一步处理分块文件
    enc = tiktoken.get_encoding("cl100k_base")

    # text_splitter = RecursiveCharacterTextSplitter(
    #     # Set a really small chunk size, just to show.
    #     chunk_size = 1000,
    #     chunk_overlap  = 200,
    #     length_function = len,
    # )
    # process_chunked_files(output_path, save_path, text_splitter)
                
                