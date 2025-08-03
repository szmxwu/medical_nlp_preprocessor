#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
规则加载器
负责加载和管理Excel中的替换规则，支持版本管理和设备类型分类
支持多文件结构和单文件结构的自动检测和兼容
"""

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ReplacementRule:
    """替换规则数据类"""
    original: str          # 原始值
    replacement: str       # 替换值
    is_regex: bool        # 是否为正则表达式
    version: str          # 版本（报告/标题/申请单）
    modality: str         # 设备类型（通用/CT/MR等）
    
    def __post_init__(self):
        """后处理：处理空值"""
        if pd.isna(self.replacement):
            self.replacement = ""
        if pd.isna(self.original):
            raise ValueError("原始值不能为空")

class RuleLoader:
    """规则加载器类 - 支持多文件和单文件结构"""
    
    def __init__(self, rules_path: Optional[str] = None):
        """初始化规则加载器
        
        Args:
            rules_path: 规则路径，可以是目录（多文件模式）或文件（单文件模式）
        """
        self.rules_path = rules_path or self._get_default_rules_path()
        self._cached_rules = {}
        self._excel_data = {}
        self._use_multi_files = self._detect_file_structure()
        
        print(f"规则加载器初始化: {'多文件模式' if self._use_multi_files else '单文件模式'}")
        print(f"规则路径: {self.rules_path}")
    
    def _get_default_rules_path(self) -> str:
        """获取默认规则路径"""
        # 优先使用多文件结构的rules目录
        rules_dir = 'medical_nlp_preprocessor/data/rules'
        single_file_new = 'medical_nlp_preprocessor/data/replace_v1.0.xlsx'
        single_file_old = 'user_input_files/replace.xlsx'
        
        if os.path.exists(rules_dir) and os.path.isdir(rules_dir):
            return rules_dir
        elif os.path.exists(single_file_new):
            return single_file_new
        elif os.path.exists(single_file_old):
            return single_file_old
        else:
            raise FileNotFoundError("找不到替换规则文件或目录")
    
    def _detect_file_structure(self) -> bool:
        """检测是否使用多文件结构"""
        return os.path.isdir(self.rules_path)
    
    def _get_file_mapping(self) -> Dict[str, str]:
        """获取版本到文件名的映射
        从外部文件加载，避免硬编码
        """
        # 检查是否已经加载过映射
        if hasattr(self, '_file_mapping'):
            return self._file_mapping

        # 映射文件路径
        mapping_file = os.path.join('medical_nlp_preprocessor', 'data', 'rules', 'version_mapping.json')

        try:
            # 读取映射文件
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
                self._file_mapping = mapping_data.get('version_to_file', {
                    '报告': 'report_replace_v1.xlsx',
                    '标题': 'title_replace_v1.xlsx',
                    '申请单': 'application_replace_v1.xlsx'
                })
                return self._file_mapping
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载版本映射文件失败: {e}")
            # 返回默认映射作为备用
            self._file_mapping = {
                '报告': 'report_replace_v1.xlsx',
                '标题': 'title_replace_v1.xlsx',
                '申请单': 'application_replace_v1.xlsx'
            }
            return self._file_mapping

    def _load_valid_params(self) -> Dict:
        """加载有效的参数信息
        从外部文件加载有效的version和modality参数组合
        """
        # 检查是否已经加载过有效参数
        if hasattr(self, '_valid_params'):
            return self._valid_params

        # 有效参数文件路径
        params_file = os.path.join('medical_nlp_preprocessor', 'data', 'rules', 'valid_params.json')

        try:
            # 读取有效参数文件
            with open(params_file, 'r', encoding='utf-8') as f:
                self._valid_params = json.load(f)
                return self._valid_params
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载有效参数文件失败: {e}")
            # 返回默认参数作为备用
            self._valid_params = {
                'valid_versions': ['报告', '标题', '申请单'],
                'valid_modalities': ['通用', 'CT', 'MR', 'DR', '病理', '超声'],
                'version_modality_mapping': {
                    '报告': ['通用', 'CT', 'MR', 'DR', '病理', '超声'],
                    '标题': ['通用', 'CT', 'MR', 'DR'],
                    '申请单': ['通用', 'CT', 'MR']
                }
            }
            return self._valid_params

    def validate_params(self, version: str, modality: str) -> None:
        """验证version和modality参数是否有效

        Args:
            version: 版本名称
            modality: 设备类型

        Raises:
            ValueError: 当参数无效时抛出异常
        """
        valid_params = self._load_valid_params()
        valid_versions = valid_params.get('valid_versions', [])
        valid_modalities = valid_params.get('valid_modalities', [])
        version_modality_mapping = valid_params.get('version_modality_mapping', {})

        # 验证版本
        if version not in valid_versions:
            raise ValueError(f"无效的版本: '{version}'。有效的版本有: {', '.join(valid_versions)}")

        # 验证设备类型
        if modality not in valid_modalities:
            raise ValueError(f"无效的设备类型: '{modality}'。有效的设备类型有: {', '.join(valid_modalities)}")

        # 验证版本和设备类型的组合
        if version in version_modality_mapping and modality not in version_modality_mapping[version]:
            valid_combinations = version_modality_mapping[version]
            raise ValueError(f"版本 '{version}' 不支持设备类型 '{modality}'。有效的组合有: {', '.join(valid_combinations)}")
    
    def _load_multi_file_data(self, version: str):
        """加载多文件结构的数据"""
        if version in self._excel_data:
            return
        
        file_mapping = self._get_file_mapping()
        
        if version not in file_mapping:
            raise ValueError(f"不支持的版本: {version}")
        
        file_path = os.path.join(self.rules_path, file_mapping[version])
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"规则文件不存在: {file_path}")
        
        try:
            self._excel_data[version] = pd.ExcelFile(file_path)
            print(f"加载规则文件: {file_path}")
            print(f"工作表数量: {len(self._excel_data[version].sheet_names)}")
        except Exception as e:
            raise RuntimeError(f"加载Excel文件失败: {e}")
    
    def _load_single_file_data(self):
        """加载单文件结构的数据"""
        if 'single_file' in self._excel_data:
            return
        
        if not os.path.exists(self.rules_path):
            raise FileNotFoundError(f"规则文件不存在: {self.rules_path}")
        
        try:
            self._excel_data['single_file'] = pd.ExcelFile(self.rules_path)
            print(f"加载规则文件: {self.rules_path}")
            print(f"工作表数量: {len(self._excel_data['single_file'].sheet_names)}")
        except Exception as e:
            raise RuntimeError(f"加载Excel文件失败: {e}")
    
    def get_available_versions(self) -> List[str]:
        """获取可用的版本列表"""
        if self._use_multi_files:
            # 多文件模式：从文件名获取版本
            file_mapping = self._get_file_mapping()
            return list(file_mapping.keys())
        else:
            # 单文件模式：从工作表名获取版本
            self._load_single_file_data()
            versions = set()
            
            for sheet_name in self._excel_data['single_file'].sheet_names:
                if '_' in sheet_name:
                    version = sheet_name.split('_')[0]
                    versions.add(version)
            
            return sorted(list(versions))
    
    def get_available_modalities(self) -> List[str]:
        """获取可用的设备类型列表"""
        if self._use_multi_files:
            # 多文件模式：从任一文件的工作表名获取设备类型
            file_mapping = self._get_file_mapping()
            first_version = list(file_mapping.keys())[0]
            self._load_multi_file_data(first_version)
            
            return sorted(self._excel_data[first_version].sheet_names)
        else:
            # 单文件模式：从工作表名获取设备类型
            self._load_single_file_data()
            modalities = set()
            
            for sheet_name in self._excel_data['single_file'].sheet_names:
                if '_' in sheet_name:
                    modality = sheet_name.split('_', 1)[1]
                    modalities.add(modality)
            
            return sorted(list(modalities))
    
    def load_rules(self, version: str, modality: str = '通用', include_general: bool = True) -> List[ReplacementRule]:
        """加载指定版本和设备类型的替换规则
        
        Args:
            version: 版本名称（报告/标题/申请单）
            modality: 设备类型（通用/CT/MR/DR/病理/超声）
            include_general: 是否包含通用规则
            
        Returns:
            替换规则列表
        """
        # 验证参数有效性
        self.validate_params(version, modality)
        
        cache_key = f"{version}_{modality}_{include_general}"
        
        if cache_key in self._cached_rules:
            return self._cached_rules[cache_key]
        
        if self._use_multi_files:
            rules = self._load_rules_multi_file(version, modality, include_general)
        else:
            rules = self._load_rules_single_file(version, modality, include_general)
        
        # 去重：如果有相同的原始值，保留后加载的规则
        rules = self._deduplicate_rules(rules)
        
        self._cached_rules[cache_key] = rules
        return rules
    
    def _load_rules_multi_file(self, version: str, modality: str, include_general: bool) -> List[ReplacementRule]:
        """多文件模式：加载规则"""
        # 加载对应版本的Excel文件
        self._load_multi_file_data(version)
        excel_file = self._excel_data[version]
        
        rules = []
        
        # 总是先加载通用规则（如果存在且需要包含通用规则）
        if include_general and '通用' in excel_file.sheet_names:
            general_rules = self._load_rules_from_sheet(excel_file, '通用', version, '通用')
            rules.extend(general_rules)
            print(f"从 通用 加载 {len(general_rules)} 条规则")
        
        # 然后加载特定设备类型的规则（如果不是通用设备类型）
        if modality != '通用' and modality in excel_file.sheet_names:
            specific_rules = self._load_rules_from_sheet(excel_file, modality, version, modality)
            rules.extend(specific_rules)
            print(f"从 {modality} 加载 {len(specific_rules)} 条规则")
        
        return rules
    
    def _load_rules_single_file(self, version: str, modality: str, include_general: bool) -> List[ReplacementRule]:
        """单文件模式：加载规则"""
        self._load_single_file_data()
        excel_file = self._excel_data['single_file']
        
        rules = []
        
        # 总是先加载通用规则（如果存在且需要包含通用规则）
        if include_general:
            general_sheet_name = f"{version}_通用"
            if general_sheet_name in excel_file.sheet_names:
                general_rules = self._load_rules_from_sheet(excel_file, general_sheet_name, version, '通用')
                rules.extend(general_rules)
                print(f"从 通用 加载 {len(general_rules)} 条规则")
            else:
                # 如果找不到通用工作表，尝试从旧格式加载
                legacy_rules = self._load_legacy_rules(excel_file, version)
                rules.extend(legacy_rules)
                if legacy_rules:
                    print(f"从旧格式加载 {len(legacy_rules)} 条通用规则")
        
        # 然后加载特定设备类型的规则（如果不是通用设备类型）
        if modality != '通用':
            specific_sheet_name = f"{version}_{modality}"
            if specific_sheet_name in excel_file.sheet_names:
                specific_rules = self._load_rules_from_sheet(excel_file, specific_sheet_name, version, modality)
                rules.extend(specific_rules)
                print(f"从 {modality} 加载 {len(specific_rules)} 条规则")
        
        return rules
    
    def _load_rules_from_sheet(self, excel_file, sheet_name: str, version: str, modality: str) -> List[ReplacementRule]:
        """从指定工作表加载规则"""
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            rules = []
            
            for _, row in df.iterrows():
                if pd.isna(row.get('原始值')):
                    continue
                
                # 处理替换值：确保NaN值被转换为空字符串
                replacement_value = row.get('替换值', '')
                if pd.isna(replacement_value):
                    replacement_value = ''
                else:
                    replacement_value = str(replacement_value)
                
                # 处理新格式（包含IsRegex列）
                if 'IsRegex' in df.columns:
                    is_regex = bool(row.get('IsRegex', False))
                    rule_version = row.get('Version', version)
                    rule_modality = row.get('Modality', modality)
                else:
                    # 旧格式：根据工作表名称判断是否为正则
                    is_regex = '条件' in sheet_name
                    rule_version = version
                    rule_modality = modality
                
                rule = ReplacementRule(
                    original=str(row['原始值']),
                    replacement=replacement_value,
                    is_regex=is_regex,
                    version=rule_version,
                    modality=rule_modality
                )
                rules.append(rule)
            
            print(f"从 {sheet_name} 加载 {len(rules)} 条规则")
            return rules
            
        except Exception as e:
            print(f"加载工作表 {sheet_name} 失败: {e}")
            return []
    
    def _load_legacy_rules(self, excel_file, version: str) -> List[ReplacementRule]:
        """加载旧格式的规则（向后兼容）"""
        legacy_mapping = {
            '报告': ['报告', '报告条件'],
            '标题': ['标题', '标题条件'],
            '申请单': ['申请单']
        }
        
        if version not in legacy_mapping:
            return []
        
        rules = []
        for sheet_name in legacy_mapping[version]:
            if sheet_name in excel_file.sheet_names:
                sheet_rules = self._load_rules_from_sheet(excel_file, sheet_name, version, '通用')
                rules.extend(sheet_rules)
        
        return rules
    
    def _deduplicate_rules(self, rules: List[ReplacementRule]) -> List[ReplacementRule]:
        """去重规则：相同原始值保留最后一个"""
        seen = {}
        for rule in rules:
            seen[rule.original] = rule
        return list(seen.values())
    
    def get_rule_statistics(self) -> Dict[str, int]:
        """获取规则统计信息"""
        stats = {}
        
        if self._use_multi_files:
            # 多文件模式：统计每个文件的工作表
            file_mapping = self._get_file_mapping()
            for version, filename in file_mapping.items():
                try:
                    self._load_multi_file_data(version)
                    excel_file = self._excel_data[version]
                    
                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = pd.read_excel(excel_file, sheet_name=sheet_name)
                            stats[f"{version}_{sheet_name}"] = len(df.dropna(subset=['原始值']))
                        except Exception:
                            stats[f"{version}_{sheet_name}"] = 0
                except Exception:
                    stats[version] = 0
        else:
            # 单文件模式：统计所有工作表
            self._load_single_file_data()
            excel_file = self._excel_data['single_file']
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    stats[sheet_name] = len(df.dropna(subset=['原始值']))
                except Exception:
                    stats[sheet_name] = 0
        
        return stats
    
    def reload_rules(self):
        """重新加载规则（清除缓存）"""
        self._cached_rules.clear()
        self._excel_data.clear()
        print("规则缓存已清除，将重新加载")

# 全局规则加载器实例
_rule_loader = None

@lru_cache(maxsize=1)
def get_rule_loader() -> RuleLoader:
    """获取全局规则加载器实例（单例模式）"""
    global _rule_loader
    if _rule_loader is None:
        _rule_loader = RuleLoader()
    return _rule_loader

# 便捷函数
def load_replacement_rules(version: str, modality: str = '通用', include_general: bool = True) -> List[ReplacementRule]:
    """便捷函数：加载替换规则"""
    return get_rule_loader().load_rules(version, modality, include_general)
