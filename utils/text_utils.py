#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本处理工具模块
提供通用的文本处理工具函数
"""

import time
import re
from functools import wraps
from typing import List, Pattern, Optional

def timing_decorator(func):
    """性能计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        # 可选择性地打印时间，用于调试
        # print(f"Time spent on {func.__name__}: {end_time - start_time:.3f}s")
        return result
    return wrapper

def clean_whitespace(text: str) -> str:
    """清理多余的空白字符"""
    if not text:
        return ''
    
    # 替换各种空白字符为标准空格
    text = re.sub(r"[ \xa0\x7f\u3000]+", " ", text)
    
    # 移除行首行尾空白
    text = re.sub(r"^\s+|\s+$", "", text, flags=re.MULTILINE)
    
    return text

def normalize_punctuation(text: str) -> str:
    """标准化标点符号"""
    if not text:
        return ''
    
    # 中文标点标准化
    punctuation_map = {
        '，': ',',
        '。': '.',
        '；': ';',
        '：': ':',
        '！': '!',
        '？': '?',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '（': '(',
        '）': ')',
        '【': '[',
        '】': ']',
        '《': '<',
        '》': '>',
    }
    
    for chinese, english in punctuation_map.items():
        text = text.replace(chinese, english)
    
    return text

def remove_numbered_prefix(text: str) -> str:
    """移除序号前缀（如：1. 2、等）"""
    if not text:
        return ''
    
    # 移除行首的序号
    text = re.sub(r"^[\n\t\r]*\d+[.、]\s*", "", text, flags=re.MULTILINE)
    
    return text

def split_sentences(text: str, pattern: str = r'[.。!！?？;；\n\r]') -> List[str]:
    """分句处理"""
    if not text:
        return []
    
    sentences = re.split(pattern, text)
    
    # 清理空句子和只包含空白的句子
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences

def is_valid_medical_text(text: str) -> bool:
    """验证是否为有效的医学文本"""
    if not text or not isinstance(text, str):
        return False
    
    # 基本长度检查
    if len(text.strip()) < 2:
        return False
    
    # 检查是否包含过多特殊字符
    special_char_ratio = len(re.findall(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', text)) / len(text)
    if special_char_ratio > 0.5:
        return False
    
    return True

def extract_numbers(text: str) -> List[str]:
    """提取文本中的数字"""
    if not text:
        return []
    
    # 匹配各种数字格式
    number_pattern = r'\d+(?:\.\d+)?'
    numbers = re.findall(number_pattern, text)
    
    return numbers

def extract_measurements(text: str) -> List[str]:
    """提取测量值"""
    if not text:
        return []
    
    # 匹配测量值（数字+单位）
    measurement_pattern = r'\d+(?:\.\d+)?(?:mm|cm|m|毫米|厘米|米|ml|毫升)'
    measurements = re.findall(measurement_pattern, text, re.IGNORECASE)
    
    return measurements

def contains_keywords(text: str, keywords: List[str], case_sensitive: bool = False) -> bool:
    """检查文本是否包含指定关键词"""
    if not text or not keywords:
        return False
    
    if not case_sensitive:
        text = text.lower()
        keywords = [kw.lower() for kw in keywords]
    
    return any(keyword in text for keyword in keywords)

def highlight_keywords(text: str, keywords: List[str], 
                      start_tag: str = '<mark>', end_tag: str = '</mark>') -> str:
    """高亮显示关键词（用于调试和可视化）"""
    if not text or not keywords:
        return text
    
    highlighted_text = text
    for keyword in keywords:
        if keyword in highlighted_text:
            highlighted_text = highlighted_text.replace(
                keyword, f"{start_tag}{keyword}{end_tag}"
            )
    
    return highlighted_text

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """截断文本到指定长度"""
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def count_chinese_chars(text: str) -> int:
    """统计中文字符数量"""
    if not text:
        return 0
    
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
    return len(chinese_chars)

def validate_regex_pattern(pattern: str) -> bool:
    """验证正则表达式是否有效"""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

def safe_regex_replace(text: str, pattern: str, replacement: str, flags: int = 0) -> str:
    """安全的正则替换，处理异常情况"""
    if not text:
        return ''
    
    try:
        return re.sub(pattern, replacement, text, flags=flags)
    except re.error as e:
        print(f"正则替换失败: {pattern} -> {replacement}, 错误: {e}")
        return text
    except Exception as e:
        print(f"替换过程中发生未知错误: {e}")
        return text

class TextStatistics:
    """文本统计工具类"""
    
    @staticmethod
    def get_basic_stats(text: str) -> dict:
        """获取基本文本统计"""
        if not text:
            return {
                'total_chars': 0,
                'chinese_chars': 0,
                'english_chars': 0,
                'digits': 0,
                'spaces': 0,
                'punctuation': 0,
                'lines': 0
            }
        
        return {
            'total_chars': len(text),
            'chinese_chars': len(re.findall(r'[\u4e00-\u9fa5]', text)),
            'english_chars': len(re.findall(r'[a-zA-Z]', text)),
            'digits': len(re.findall(r'\d', text)),
            'spaces': len(re.findall(r'\s', text)),
            'punctuation': len(re.findall(r'[^\w\s]', text)),
            'lines': len(text.splitlines())
        }
    
    @staticmethod
    def get_word_frequency(text: str, top_n: int = 10) -> List[tuple]:
        """获取词频统计（简单版本，按字符计算）"""
        if not text:
            return []
        
        # 简单的字符频率统计
        char_count = {}
        for char in text:
            if char.isalnum():  # 只统计字母和数字
                char_count[char] = char_count.get(char, 0) + 1
        
        # 按频率排序
        sorted_chars = sorted(char_count.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_chars[:top_n]

# 常用的正则表达式模式
COMMON_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'1[3-9]\d{9}',
    'id_card': r'\d{17}[\dXx]',
    'measurement': r'\d+(?:\.\d+)?(?:mm|cm|m|毫米|厘米|米)',
    'percentage': r'\d+(?:\.\d+)?%',
    'date': r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?',
    'time': r'\d{1,2}:\d{2}(?::\d{2})?',
}

def get_pattern(pattern_name: str) -> Optional[Pattern]:
    """获取常用正则表达式模式"""
    pattern_str = COMMON_PATTERNS.get(pattern_name)
    if pattern_str:
        return re.compile(pattern_str)
    return None
