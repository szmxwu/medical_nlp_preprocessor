#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
正则表达式统一管理模块
所有正则表达式在此预编译，避免运行时重复编译，提升性能
"""

import re
from functools import lru_cache
from typing import Dict, Pattern

class RegexPatterns:
    """正则表达式管理类"""
    
    def __init__(self):
        """初始化并预编译所有正则表达式"""
        self._patterns = {}
        self._compile_all_patterns()
    
    def _compile_all_patterns(self):
        """预编译所有正则表达式"""
        
        # 脊柱和椎体相关正则表达式
        self._patterns.update({
            # 椎体扩展相关
            'SPINE_DOT_1': re.compile(r'([^颈胸腰骶尾])(\d{1,2})[、|,|，|及|和](\d{1,2})([颈|胸|腰|骶|尾])(?!.*段)', re.I),
            'SPINE_DOT_2': re.compile(r'([^颈胸腰骶尾/])(\d{1,2})[、|,|，|及|和]([颈|胸|腰|骶|尾])(\d{1,2})(?!.*段)', re.I),
            'SPINE_DOT_3': re.compile(r'([^颈胸腰骶尾])(\d{1,2})(/\d{1,2})[、|,|，|及|和](\d{1,2})(/\d{1,2})([颈|胸|腰|骶|尾])', re.I),
            'SPINE_DOT_4': re.compile(r'([^颈胸腰骶尾])(\d{1,2})(/\d{1,2})[、|,|，|及|和]([颈|胸|腰|骶|尾])(\d{1,2})(/\d{1,2})', re.I),
            'SPINE_DOT_5': re.compile(r'([腰|胸|颈|骶|尾|c|l|t|s])(\d{1,2})(/\d{1,2})?[、|,|，|及|和](\d{1,2})', re.I),
            'SPINE_DOT_6': re.compile(r'([腰|胸|颈|骶|尾|c|l|t|s]\d{1,2})(/\d{1,2})?[,|，]([腰|胸|颈|骶|尾|c|l|t|s]\d{1,2})', re.I),
            
            # 椎间盘相关
            'DISK_RANGE': re.compile(r"([胸|腰|颈|骶|c|t|l|s])(\d{1,2})/([胸|腰|颈|骶|c|t|l|s])?(\d{1,2})-([胸|腰|颈|骶|c|t|l|s])?(\d{1,2})/([胸|腰|颈|骶|c|t|l|s])?(\d{1,2})(?!.*段)", re.I),
            'SPINE_RANGE': re.compile(r"([胸|腰|颈|骶|c|t|l|s])(\d{1,2})-([胸|腰|颈|骶|c|t|l|s])?(\d{1,2})(椎体)?(?!.*段)", re.I),
            
            # 其他标识
            'CERVICAL': re.compile(r'(^|[^a-zA-Z])C([1-8])(?!.*段)', re.I),
            'THORACIC': re.compile(r'(^|[^a-zA-Z长短低高等脂水])T(\d{1,2})(?!.*[段_信号压黑为呈示a-zA-Z])', re.I),
            'THORACIC_VERTEBRA': re.compile(r'(^|[^a-zA-Z])T(\d{1,2})椎', re.I),
            'THORACIC_SPECIFIC': re.compile(r'(^|[^a-zA-Z])T([3-9]|10|11|12)(?!.*[MN])', re.I),
            'SACRAL': re.compile(r'(^|[^a-zA-Z])S([1-5])(?![段a-zA-Z0-9])', re.I),
            
            # 文本处理相关
            'DOT_SEPARATOR': re.compile(r"([a-zA-Z\u4e00-\u9fa5])\.([a-zA-Z\u4e00-\u9fa5])", re.I),
        })
        
        # 测量值提取相关正则表达式
        self._patterns.update({
            'MEASUREMENT': re.compile(r'(\d+(\.\d+)?(?:mm|cm|m|\*|×))(?![a-zA-Z])|(\d+(\.\d+)?(?:毫米|米))', re.I),
            'PERCENTAGE': re.compile(r'[\d\.]{1,}(?:%|％)'),
            'VOLUME': re.compile(r'(\d+(\.\d+)?(?:ml|毫升))(?![a-zA-Z])', re.I),
        })
        
        # 肋骨缩写扩展相关
        self._patterns.update({
            'RIB_ABBREVIATION': re.compile(
                r"(双侧|双|[左右]|)"   # Group 1: Optional Prefix (左/右/双侧)
                r"(第)"           # Group 2: Literal '第'
                r"([\d、，]+)"     # Group 3: Numbers (list '5、6' or start of range '1')
                r"(?:-(\d+))?"    # Group 4: Optional end of range ('4')
                r"([前后腋]?)"     # Group 5: Optional Infix (前/后/腋)
                r"(肋骨?)"         # Group 6: '肋骨' or '肋'
                r"([^，。、\s]+)"  # Group 7: Suffix - One or more non-separator/space chars
            )
        })
    
    def get_pattern(self, pattern_name: str) -> Pattern:
        """获取预编译的正则表达式
        
        Args:
            pattern_name: 正则表达式名称
            
        Returns:
            预编译的正则表达式对象
            
        Raises:
            KeyError: 如果模式名称不存在
        """
        if pattern_name not in self._patterns:
            raise KeyError(f"正则表达式模式 '{pattern_name}' 不存在")
        return self._patterns[pattern_name]
    
    def get_all_patterns(self) -> Dict[str, Pattern]:
        """获取所有预编译的正则表达式"""
        return self._patterns.copy()
    
    def compile_from_config(self, config_regex: str, flags: int = re.I) -> Pattern:
        """从配置文件中的字符串编译正则表达式
        
        Args:
            config_regex: 配置文件中的正则表达式字符串
            flags: 正则表达式标志
            
        Returns:
            编译后的正则表达式对象
        """
        return re.compile(config_regex, flags)

# 全局实例
_regex_manager = None

@lru_cache(maxsize=1)
def get_regex_manager() -> RegexPatterns:
    """获取全局正则表达式管理器实例（单例模式）"""
    global _regex_manager
    if _regex_manager is None:
        _regex_manager = RegexPatterns()
    return _regex_manager

# 便捷函数
def get_pattern(pattern_name: str) -> Pattern:
    """便捷函数：获取预编译的正则表达式"""
    return get_regex_manager().get_pattern(pattern_name)

def compile_pattern(regex_str: str, flags: int = re.I) -> Pattern:
    """便捷函数：编译正则表达式"""
    return get_regex_manager().compile_from_config(regex_str, flags)
