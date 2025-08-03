#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医学专业扩展模块
处理脊柱、椎间盘、肋骨等医学专业术语的缩写扩展
重构自原始代码的spine_extend, disk_extend, expand_rib_abbreviations等函数
"""

import re
from typing import Optional
from ..config.regex_patterns import get_pattern
from ..utils.text_utils import safe_regex_replace

class MedicalExpander:
    """医学术语扩展处理器"""
    
    def __init__(self):
        """初始化医学扩展器"""
        self._spine_limits = {
            '颈': 7, 'c': 7, 'C': 7,
            '胸': 12, 't': 12, 'T': 12,
            '腰': 5, 'l': 5, 'L': 5,
            '骶': 5, 's': 5, 'S': 5,
            '尾': 3
        }
    
    def expand_all(self, text: str) -> str:
        """应用所有医学扩展
        
        Args:
            text: 待处理文本
            
        Returns:
            扩展后的文本
        """
        if not text:
            return ''
        
        # 1. 椎体顿号扩展
        text = self.expand_spine_dot(text)
        
        # 2. 椎体范围扩展
        text = self.expand_spine_range(text)
        
        # 3. 椎间盘范围扩展
        text = self.expand_disk_range(text)
        
        # 4. 肋骨缩写扩展
        text = self.expand_rib_abbreviations(text)
        
        return text
    
    def expand_spine_dot(self, text: str) -> str:
        """扩展椎体+顿号形式
        
        例如: "L1、2椎体" -> "L1椎体、L2椎体"
        """
        if not text:
            return ''
        
        # 使用预编译的正则表达式
        try:
            # 处理各种椎体顿号格式
            patterns_and_replacements = [
                ('SPINE_DOT_1', r"\1\4\2、\4\3"),
                ('SPINE_DOT_3', r"\1\6\2\3、\6\4\5"),
            ]
            
            for pattern_name, replacement in patterns_and_replacements:
                pattern = get_pattern(pattern_name)
                text = pattern.sub(replacement, text)
            
            # 迭代处理复杂情况
            max_iterations = 10
            for _ in range(max_iterations):
                original_text = text
                
                patterns_and_replacements = [
                    ('SPINE_DOT_2', r"\1\3\2、\3\4"),
                    ('SPINE_DOT_4', r"\1\4\2\3、\4\5\6"),
                    ('SPINE_DOT_5', r"\1\2\3、\1\4"),
                    ('SPINE_DOT_6', r"\1\2、\3"),
                ]
                
                for pattern_name, replacement in patterns_and_replacements:
                    pattern = get_pattern(pattern_name)
                    text = pattern.sub(replacement, text)
                
                # 如果没有变化，退出循环
                if text == original_text:
                    break
                    
        except Exception as e:
            print(f"椎体顿号扩展失败: {e}")
        
        return text
    
    def expand_spine_range(self, text: str) -> str:
        """扩展椎体范围形式
        
        例如: "L1-3椎体" -> "L1椎体、L2椎体、L3椎体"
        """
        if not text:
            return ''
        
        try:
            pattern = get_pattern('SPINE_RANGE')
            matches = pattern.findall(text)
            
            if not matches:
                return text
            
            for match in matches:
                spine_type1, start_num, spine_type2, end_num, suffix = match
                
                try:
                    start = int(start_num)
                    end = int(end_num)
                    
                    # 确定结束椎体的最大编号
                    if spine_type1 == spine_type2 or spine_type2 == '':
                        last_vertebra = end
                    else:
                        last_vertebra = self._get_spine_limit(spine_type1)
                    
                    # 生成扩展文本
                    expanded_parts = []
                    
                    # 第一段椎体
                    for i in range(start, min(last_vertebra + 1, end + 1)):
                        expanded_parts.append(f"{spine_type1}{i}椎体")
                    
                    # 第二段椎体（如果有）
                    if spine_type1 != spine_type2 and spine_type2:
                        for i in range(1, end + 1):
                            expanded_parts.append(f"{spine_type2}{i}椎体")
                    
                    # 替换原文
                    old_text = f"{spine_type1}{start_num}-{spine_type2}{end_num}{suffix}"
                    new_text = "、".join(expanded_parts)
                    text = text.replace(old_text, new_text)
                    
                except (ValueError, TypeError):
                    # 如果数字转换失败，跳过这个匹配
                    continue
                    
        except Exception as e:
            print(f"椎体范围扩展失败: {e}")
        
        return text
    
    def expand_disk_range(self, text: str) -> str:
        """扩展椎间盘范围形式
        
        例如: "L1/2-3/4" -> "L1/2、L2/3、L3/4"
        """
        if not text:
            return ''
        
        try:
            pattern = get_pattern('DISK_RANGE')
            matches = pattern.findall(text)
            
            if not matches:
                return text
            
            for match in matches:
                spine_type1, start_num, _, _, spine_type2, end_num, _, _ = match
                
                try:
                    start = int(start_num)
                    end = int(end_num)
                    
                    # 确定结束位置
                    if spine_type1 == spine_type2 or spine_type2 == '':
                        last_disk = end
                    else:
                        last_disk = self._get_spine_limit(spine_type1)
                    
                    # 生成椎间盘序列
                    expanded_parts = []
                    
                    # 第一段椎间盘
                    for i in range(start, min(last_disk + 1, end + 1)):
                        expanded_parts.append(f"{spine_type1}{i}/{i+1}")
                    
                    # 第二段椎间盘（如果有）
                    if spine_type1 != spine_type2 and spine_type2:
                        for i in range(1, end + 1):
                            expanded_parts.append(f"{spine_type2}{i}/{i+1}")
                    
                    # 处理特殊的椎间盘连接
                    expanded_text = "、".join(expanded_parts)
                    expanded_text = re.sub(r"[颈|c|C]7/8", "颈7/胸1", expanded_text, flags=re.I)
                    expanded_text = re.sub(r"[胸|t|T]12/13", "胸12/腰1", expanded_text, flags=re.I)
                    expanded_text = re.sub(r"[腰|l|L]5/6", "腰5/骶1", expanded_text, flags=re.I)
                    
                    # 构建原始匹配文本
                    old_text = "".join(match)
                    text = text.replace(old_text, expanded_text)
                    
                except (ValueError, TypeError):
                    continue
                    
        except Exception as e:
            print(f"椎间盘范围扩展失败: {e}")
        
        return text
    
    def expand_rib_abbreviations(self, text: str) -> str:
        """扩展肋骨缩写形式
        
        例如: "右第5、6前肋骨折" -> "右第5前肋骨折，右第6前肋骨折"
        """
        if not text or "肋" not in text:
            return text
        
        try:
            pattern = get_pattern('RIB_ABBREVIATION')
            
            def replace_match(match):
                prefix = match.group(1) or ""
                marker = match.group(2)  # "第"
                num_part = match.group(3)
                range_end = match.group(4)  # None if not a range
                infix = match.group(5) or ""
                rib_word = match.group(6) or "肋骨"
                suffix = match.group(7) or ""
                
                numbers_to_expand = []
                
                if range_end:
                    # 范围格式：第1-4肋
                    try:
                        start_num = int(num_part)
                        end_num = int(range_end)
                        if start_num <= end_num <= 12:  # 肋骨最多12对
                            numbers_to_expand = list(range(start_num, end_num + 1))
                        else:
                            return match.group(0)
                    except ValueError:
                        return match.group(0)
                else:
                    # 列表格式：第5、6肋
                    try:
                        numbers_to_expand = [
                            int(n) for n in re.split(r'[、，]', num_part) 
                            if n.strip().isdigit() and 1 <= int(n) <= 12
                        ]
                    except ValueError:
                        return match.group(0)
                
                if not numbers_to_expand:
                    return match.group(0)
                
                # 生成扩展结果
                expanded_parts = []
                for num in numbers_to_expand:
                    expanded_parts.append(f"{prefix}{marker}{num}{infix}{rib_word}{suffix}")
                
                return "，".join(expanded_parts)
            
            text = pattern.sub(replace_match, text)
            
        except Exception as e:
            print(f"肋骨缩写扩展失败: {e}")
        
        return text
    
    def _get_spine_limit(self, spine_type: str) -> int:
        """获取椎体类型的最大编号"""
        return self._spine_limits.get(spine_type.lower(), 5)
    
    def normalize_spine_identifiers(self, text: str) -> str:
        """标准化椎体标识符
        
        将C1, T1, L1, S1等标准化为中文形式
        """
        if not text:
            return ''
        
        try:
            # 使用预编译的正则表达式
            spine_patterns = [
                ('CERVICAL', r'\1颈\2'),
                ('THORACIC', r'\1胸\2'),
                ('THORACIC_VERTEBRA', r'\1胸\2'),
                ('SACRAL', r'\1骶\2'),
                ('THORACIC_SPECIFIC', r'\1胸\2'),
            ]
            
            for pattern_name, replacement in spine_patterns:
                pattern = get_pattern(pattern_name)
                text = pattern.sub(replacement, text)
                
        except Exception as e:
            print(f"椎体标识符标准化失败: {e}")
        
        return text
    
    def get_expansion_stats(self, original_text: str, expanded_text: str) -> dict:
        """获取扩展统计信息"""
        return {
            'original_length': len(original_text),
            'expanded_length': len(expanded_text),
            'expansion_ratio': len(expanded_text) / len(original_text) if original_text else 0,
            'spine_mentions': len(re.findall(r'[颈胸腰骶尾]\d+', expanded_text)),
            'rib_mentions': len(re.findall(r'第\d+.*?肋', expanded_text)),
            'disk_mentions': len(re.findall(r'\d+/\d+', expanded_text))
        }

# 便捷函数
def expand_medical_terms(text: str) -> str:
    """便捷函数：扩展医学术语"""
    expander = MedicalExpander()
    return expander.expand_all(text)
