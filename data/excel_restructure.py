#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Excel数据结构重构工具
重新组织replace.xlsx文件，添加IsRegex列和modality列，支持版本管理
"""

import pandas as pd
import numpy as np
import os

def restructure_replace_excel():
    """重构replace.xlsx文件结构"""
    
    # 读取原始Excel文件
    original_path = 'user_input_files/replace.xlsx'
    xl_file = pd.ExcelFile(original_path)
    
    # 新的Excel文件结构
    new_data = {}
    
    # 1. 处理"报告"工作表 - 合并报告和报告条件
    print("处理报告数据...")
    
    # 读取原始"报告"数据
    report_data = pd.read_excel(original_path, sheet_name='报告')
    report_data['IsRegex'] = False  # 普通文本替换
    report_data['Version'] = '报告'
    
    # 读取原始"报告条件"数据（正则替换）
    report_condition_data = pd.read_excel(original_path, sheet_name='报告条件')
    report_condition_data['IsRegex'] = True  # 正则替换
    report_condition_data['Version'] = '报告'
    
    # 合并报告数据
    combined_report = pd.concat([report_data, report_condition_data], ignore_index=True)
    
    # 为不同设备类型创建数据
    modalities = ['通用', 'CT', 'MR', 'DR', '病理', '超声']
    
    for modality in modalities:
        modality_data = combined_report.copy()
        modality_data['Modality'] = modality
        
        if modality == '通用':
            # 通用包含所有现有规则
            new_data[f'报告_{modality}'] = modality_data
        else:
            # 其他模态暂时为空，后续可手工添加专用规则
            empty_data = pd.DataFrame(columns=['原始值', '替换值', 'IsRegex', 'Version', 'Modality'])
            empty_data['Modality'] = modality
            empty_data['Version'] = '报告'
            new_data[f'报告_{modality}'] = empty_data
    
    # 2. 处理"标题"工作表
    print("处理标题数据...")
    
    # 读取原始"标题"数据
    title_data = pd.read_excel(original_path, sheet_name='标题')
    title_data['IsRegex'] = False
    title_data['Version'] = '标题'
    
    # 读取原始"标题条件"数据
    title_condition_data = pd.read_excel(original_path, sheet_name='标题条件')
    title_condition_data['IsRegex'] = True
    title_condition_data['Version'] = '标题'
    
    # 合并标题数据
    combined_title = pd.concat([title_data, title_condition_data], ignore_index=True)
    
    for modality in modalities:
        modality_data = combined_title.copy()
        modality_data['Modality'] = modality
        
        if modality == '通用':
            new_data[f'标题_{modality}'] = modality_data
        else:
            empty_data = pd.DataFrame(columns=['原始值', '替换值', 'IsRegex', 'Version', 'Modality'])
            empty_data['Modality'] = modality
            empty_data['Version'] = '标题'
            new_data[f'标题_{modality}'] = empty_data
    
    # 3. 处理"申请单"工作表
    print("处理申请单数据...")
    
    apply_data = pd.read_excel(original_path, sheet_name='申请单')
    apply_data['IsRegex'] = False
    apply_data['Version'] = '申请单'
    
    for modality in modalities:
        modality_data = apply_data.copy()
        modality_data['Modality'] = modality
        
        if modality == '通用':
            new_data[f'申请单_{modality}'] = modality_data
        else:
            empty_data = pd.DataFrame(columns=['原始值', '替换值', 'IsRegex', 'Version', 'Modality'])
            empty_data['Modality'] = modality
            empty_data['Version'] = '申请单'
            new_data[f'申请单_{modality}'] = empty_data
    
    return new_data

def save_restructured_excel(new_data, output_path):
    """保存重构后的Excel文件"""
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, data in new_data.items():
            if not data.empty:
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"创建工作表: {sheet_name} ({len(data)} 条规则)")
            else:
                # 创建空的模板
                empty_df = pd.DataFrame(columns=['原始值', '替换值', 'IsRegex', 'Version', 'Modality'])
                empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"创建空工作表: {sheet_name}")

def create_version_info():
    """创建版本信息文档"""
    
    version_info = {
        'version': '1.0.0',
        'date': '2025-08-03',
        'description': '重构版本 - 支持IsRegex和Modality分类',
        'changes': [
            '添加IsRegex列区分普通文本替换和正则替换',
            '添加Modality列支持设备类型分类',
            '添加Version列支持版本管理',
            '合并"报告"和"报告条件"到统一工作表',
            '合并"标题"和"标题条件"到统一工作表',
            '为CT、MR、DR、病理、超声创建专用工作表'
        ],
        'modalities': ['通用', 'CT', 'MR', 'DR', '病理', '超声'],
        'versions': ['报告', '标题', '申请单']
    }
    
    return version_info

def main():
    """主函数"""
    print("开始重构Excel数据结构...")
    
    # 创建输出目录
    os.makedirs('medical_nlp_preprocessor/data', exist_ok=True)
    
    # 重构数据
    new_data = restructure_replace_excel()
    
    # 保存新的Excel文件
    output_path = 'medical_nlp_preprocessor/data/replace_v1.0.xlsx'
    save_restructured_excel(new_data, output_path)
    
    # 创建版本信息
    version_info = create_version_info()
    
    # 保存版本信息到JSON
    import json
    with open('medical_nlp_preprocessor/data/version_info.json', 'w', encoding='utf-8') as f:
        json.dump(version_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n重构完成!")
    print(f"新Excel文件: {output_path}")
    print(f"版本信息: medical_nlp_preprocessor/data/version_info.json")
    print(f"总工作表数: {len(new_data)}")

if __name__ == "__main__":
    main()
