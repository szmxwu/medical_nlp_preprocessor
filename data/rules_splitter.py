#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
规则文件拆分工具
将单一的replace_v1.0.xlsx文件按应用场景拆分成多个独立文件
"""

import pandas as pd
import os
from pathlib import Path

def analyze_current_structure():
    """分析当前文件结构"""
    excel_path = 'medical_nlp_preprocessor/data/replace_v1.0.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"文件不存在: {excel_path}")
        return None
    
    xl_file = pd.ExcelFile(excel_path)
    sheet_names = xl_file.sheet_names
    
    print("=== 当前Excel文件结构分析 ===")
    print(f"工作表数量: {len(sheet_names)}")
    print("工作表列表:")
    
    # 按应用场景分组
    scenarios = {'报告': [], '标题': [], '申请单': []}
    
    for sheet_name in sheet_names:
        print(f"  - {sheet_name}")
        
        # 确定应用场景
        for scenario in scenarios.keys():
            if sheet_name.startswith(scenario):
                scenarios[scenario].append(sheet_name)
                break
    
    print("\n=== 按应用场景分组 ===")
    for scenario, sheets in scenarios.items():
        print(f"{scenario}: {len(sheets)} 个工作表")
        for sheet in sheets:
            print(f"  - {sheet}")
    
    return scenarios, xl_file

def split_excel_by_scenario():
    """按应用场景拆分Excel文件"""
    
    scenarios, xl_file = analyze_current_structure()
    if not scenarios:
        return
    
    rules_dir = Path('medical_nlp_preprocessor/data/rules')
    rules_dir.mkdir(exist_ok=True)
    
    print("\n=== 开始拆分文件 ===")
    
    # 文件名映射
    file_mapping = {
        '报告': 'report_replace_v1.xlsx',
        '标题': 'title_replace_v1.xlsx', 
        '申请单': 'application_replace_v1.xlsx'
    }
    
    for scenario, sheets in scenarios.items():
        if not sheets:
            print(f"⚠ {scenario} 场景无工作表，跳过")
            continue
            
        output_file = rules_dir / file_mapping[scenario]
        print(f"\n创建文件: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name in sheets:
                try:
                    # 读取原工作表
                    df = pd.read_excel(xl_file, sheet_name=sheet_name)
                    
                    # 提取设备类型（去掉场景前缀）
                    modality = sheet_name.replace(f'{scenario}_', '')
                    
                    # 写入新文件，工作表名为设备类型
                    df.to_excel(writer, sheet_name=modality, index=False)
                    print(f"  ✓ {sheet_name} -> {modality} ({len(df)} 条规则)")
                    
                except Exception as e:
                    print(f"  ✗ 处理 {sheet_name} 失败: {e}")
        
        print(f"✓ {scenario} 文件创建完成: {output_file}")
    
    return file_mapping

def create_new_version_info():
    """创建新版本信息"""
    
    version_info = {
        'version': '1.1.0',
        'date': '2025-08-03',
        'description': '多文件版本 - 按应用场景拆分规则文件',
        'changes': [
            '将单一Excel文件拆分为多个场景专用文件',
            '支持独立的版本管理和维护',
            '保持原有功能完全兼容',
            '优化文件组织结构和加载逻辑'
        ],
        'file_structure': {
            'report_replace_v1.xlsx': '报告场景规则文件',
            'title_replace_v1.xlsx': '标题场景规则文件', 
            'application_replace_v1.xlsx': '申请单场景规则文件'
        },
        'modalities': ['通用', 'CT', 'MR', 'DR', '病理', '超声'],
        'scenarios': ['报告', '标题', '申请单'],
        'rules_directory': 'rules/'
    }
    
    return version_info

def main():
    """主函数"""
    print("开始规则文件拆分...")
    
    # 拆分文件
    file_mapping = split_excel_by_scenario()
    
    if file_mapping:
        # 创建新版本信息
        version_info = create_new_version_info()
        
        # 保存版本信息
        import json
        version_path = 'medical_nlp_preprocessor/data/version_info_v1.1.json'
        with open(version_path, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 新版本信息已保存: {version_path}")
        print(f"✓ 规则文件拆分完成！")
        print(f"✓ 生成文件:")
        
        rules_dir = Path('medical_nlp_preprocessor/data/rules')
        for file_name in file_mapping.values():
            file_path = rules_dir / file_name
            if file_path.exists():
                print(f"  - {file_path}")
    
    else:
        print("✗ 拆分失败")

if __name__ == "__main__":
    main()
