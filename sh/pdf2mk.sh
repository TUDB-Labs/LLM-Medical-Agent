#!/bin/bash

# 定义输入和输出的基础路径
input_base_dir="/root/medical/makedata2/data/pdfs_100"
output_base_dir="/root/medical/makedata2/data/mk_100"

# 遍历 input_base_dir 下的所有子目录
for dir in "$input_base_dir"/*/; do
    # 获取当前子目录的名称
    dir_name=$(basename "$dir")
    
    # 构建完整的输入和输出路径
    input_folder="$dir"
    output_folder="$output_base_dir/$dir_name"
    
    # 执行 marker 命令
    marker "$input_folder" "$output_folder" --workers 5
done