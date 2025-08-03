#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本替换引擎
统一的替换引擎，支持正则和普通文本替换，数据驱动
"""

import re
from typing import List, Dict, Optional
from functools import lru_cache
from ..data.rule_loader import ReplacementRule, load_replacement_rules
from ..config.regex_patterns import get_pattern, compile_pattern

class TextReplacer:
    """统一文本替换引擎"""
    
    def __init__(self, version: str = '报告', modality: str = '通用'):
        """初始化替换引擎
        
        Args:
            version: 规则版本（报告/标题/申请单）
            modality: 设备类型（通用/CT/MR/DR/病理/超声）
        """
        self.version = version
        self.modality = modality
        self._rules = []
        self._compiled_regex_rules = {}
        self._text_rules = {}
        
        self.load_rules()
    
    def load_rules(self):
        """加载并预处理替换规则"""
        print(f"加载替换规则: {self.version} - {self.modality}")
        
        # 加载规则，先加载通用规则，再加载特定设备规则
        self._rules = load_replacement_rules(
            version=self.version,
            modality=self.modality,
            include_general=True
        )
        
        # 分类处理规则
        self._compile_rules()
        
        print(f"已加载 {len(self._rules)} 条规则")
        print(f"正则规则: {len(self._compiled_regex_rules)}")
        print(f"文本规则: {len(self._text_rules)}")
    
    def _compile_rules(self):
        """编译和分类规则"""
        self._compiled_regex_rules.clear()
        self._text_rules.clear()
        
        for rule in self._rules:
            if rule.is_regex:
                # 正则替换规则
                try:
                    compiled_pattern = compile_pattern(rule.original)
                    self._compiled_regex_rules[rule.original] = {
                        'pattern': compiled_pattern,
                        'replacement': rule.replacement,
                        'rule': rule
                    }
                except re.error as e:
                    print(f"正则表达式编译失败: {rule.original} - {e}")
            else:
                # 普通文本替换规则
                # 转换为大写以支持不区分大小写的替换
                key = rule.original.upper()
                self._text_rules[key] = {
                    'original': rule.original,
                    'replacement': rule.replacement,
                    'rule': rule
                }
    
    def apply_replacements(self, text: str) -> str:
        """应用所有替换规则
        
        Args:
            text: 待处理文本
      
            
        Returns:
            处理后的文本
        """
        if not text or not isinstance(text, str):
            return ''
        
        # 1. 基础预处理
        text = self._basic_preprocessing(text)
        
        # 2. 应用文本替换规则
        text = self._apply_text_replacements(text)
        
        # 3. 应用正则替换规则
        text = self._apply_regex_replacements(text)
        
        return text
    
    def _basic_preprocessing(self, text: str) -> str:
        """基础预处理"""
        # 移除序号前缀
        text = re.sub(r"^[\n\t\r]+\d[\.|、]", "", text)
        
        # 统一空白字符
        text = re.sub(r"[ \xa0\x7f\u3000]", "", text)
        
        # 处理括号后的换行
        text = re.sub(r"(）|\)) ", r"\1\n", text)
        
        # 移除带序号的句子开头
        text = re.sub(r"\b(\d+[.、])(?!\d)([\u4e00-\u9fffa-zA-Z][\u4e00-\u9fffa-zA-Z，。；]*)\b", 
                     r"\2", text, flags=re.X | re.IGNORECASE)
        
        return text
    
    def _apply_text_replacements(self, text: str) -> str:
        """应用普通文本替换"""
        for rule_data in self._text_rules.values():
            original = rule_data['original']
            replacement = rule_data['replacement']
            
            # 不区分大小写的替换
            text = text.upper().replace(original.upper(), replacement)
        
        return text
    
    def _apply_regex_replacements(self, text: str) -> str:
        """应用正则替换"""
        for rule_data in self._compiled_regex_rules.values():
            pattern = rule_data['pattern']
            replacement = rule_data['replacement']
            
            try:
                text = pattern.sub(replacement, text)
            except Exception as e:
                print(f"正则替换失败: {rule_data['rule'].original} - {e}")
        
        return text
    
    def process_sentences(self, text: str, sentence_pattern: str) -> str:
        """分句处理：先分句，后逐句处理
        
        Args:
            text: 待处理文本
            sentence_pattern: 分句正则表达式
            
        Returns:
            处理后的文本
        """
        # 分句
        sentence_ends = [match.start() for match in re.finditer(sentence_pattern, text)]
        
        if not sentence_ends:
            sentence_ends = [len(text)]
        
        if sentence_ends[0] != 0:
            sentence_ends = [0] + sentence_ends
        
        if sentence_ends[-1] != len(text):
            sentence_ends.append(len(text))
        
        # 逐句处理
        processed_sentences = []
        for i in range(len(sentence_ends) - 1):
            sentence = text[sentence_ends[i]:sentence_ends[i + 1]]
            
            if sentence:
                # 对每个句子应用特殊处理
                processed_sentence = self._process_single_sentence(sentence)
                processed_sentences.append(processed_sentence)
        
        return "\n".join(processed_sentences)
    
    def _process_single_sentence(self, sentence: str) -> str:
        """处理单个句子的特殊规则"""
        # 应用脊柱相关的特殊处理
        if self._contains_spine_keywords(sentence):
            sentence = self._apply_spine_specific_rules(sentence)
        
        # 应用点号分隔符处理
        dot_pattern = get_pattern('DOT_SEPARATOR')
        sentence = dot_pattern.sub(r"\1。\2", sentence)
        
        return sentence
    
    def _contains_spine_keywords(self, text: str) -> bool:
        """检查文本是否包含脊柱关键词"""
        spine_keywords = ['椎', '横突', '棘', '脊', '黄韧带', '肋', '颈', '骶', '尾骨', '腰大肌']
        return any(keyword in text for keyword in spine_keywords)
    
    def _apply_spine_specific_rules(self, text: str) -> str:
        """应用脊柱特定的替换规则"""
        # 应用椎体标识的正则替换
        patterns_and_replacements = [
            ('CERVICAL', r'\1颈\2'),
            ('THORACIC', r'\1胸\2'), 
            ('THORACIC_VERTEBRA', r'\1胸\2'),
            ('SACRAL', r'\1骶\2'),
            ('THORACIC_SPECIFIC', r'\1胸\2'),
        ]
        
        for pattern_name, replacement in patterns_and_replacements:
            try:
                pattern = get_pattern(pattern_name)
                text = pattern.sub(replacement, text)
            except KeyError:
                # 如果模式不存在，跳过
                continue
        
        return text
    
    def reload_rules(self):
        """重新加载规则"""
        self.load_rules()
    
    def get_rule_info(self) -> Dict:
        """获取规则信息（用于调试）"""
        return {
            'version': self.version,
            'modality': self.modality,
            'total_rules': len(self._rules),
            'text_rules': len(self._text_rules),
            'regex_rules': len(self._compiled_regex_rules),
            'rule_breakdown': {
                'regex': [rule.original for rule in self._rules if rule.is_regex][:5],  # 只显示前5个
                'text': [rule.original for rule in self._rules if not rule.is_regex][:5]  # 只显示前5个
            }
        }

# 便捷函数
def create_replacer(version: str = '报告', modality: str = '通用') -> TextReplacer:
    """创建文本替换器"""
    return TextReplacer(version=version, modality=modality)
