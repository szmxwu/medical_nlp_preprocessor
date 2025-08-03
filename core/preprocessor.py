#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医学NLP文本预处理核心类
实现"先分句，后逐句纠正"的处理流程，整合所有预处理功能
"""

from typing import Optional, Dict, Any, List
from functools import lru_cache
import time
import re

from .text_replacer import TextReplacer
from ..config.config_manager import get_config_manager, get_config, get_config_pattern
from ..config.regex_patterns import get_regex_manager
from ..extensions.medical_expander import MedicalExpander
from ..utils.text_utils import timing_decorator

class Preprocessor:
    """医学文本预处理器核心类"""
    
    def __init__(self, version: str = '报告', modality: str = '通用', enable_cache: bool = True):
        """初始化预处理器
        
        Args:
            version: 规则版本（报告/标题/申请单）
            modality: 设备类型（通用/CT/MR/DR/病理/超声）
            enable_cache: 是否启用缓存
        """
        self.version = version
        self.modality = modality
        self.enable_cache = enable_cache
        
        # 初始化组件
        self.config_manager = get_config_manager()
        self.regex_manager = get_regex_manager()
        self.text_replacer = TextReplacer(version=version, modality=modality)
        self.medical_expander = MedicalExpander()
        
        # 加载配置
        self._load_patterns()
        
        print(f"医学文本预处理器初始化完成: {version} - {modality}")
    
    def _load_patterns(self):
        """加载预编译的正则表达式模式"""
        self.sentence_pattern = get_config('sentence', 'sentence_pattern', '[?？。；;\n\r]')
        self.stop_pattern = get_config('sentence', 'stop_pattern', '[?？。；;,，\n\r伴并]')
        
        # 获取编译后的模式
        self.sentence_regex = get_config_pattern('SENTENCE_PATTERN')
        self.spine_words_regex = get_config_pattern('SPINE_WORDS')
    
    @timing_decorator
    def process(self, text: str) -> List[Dict[str, str]]:
        """主处理方法：完整的预处理流水线
        
        Args:
            text: 待处理的原始医学文本
            
        Returns:
            包含分句结果的列表，每个元素为字典
            格式: [{"original": 原始句子1, "preprocessed": 处理后的句子1}, ...]
        """
        if not text or not isinstance(text, str):
            return []
        
        # 使用LRU缓存处理（如果启用）
        if self.enable_cache:
            return self._process_with_cache(text,  self.version, self.modality)
        else:
            # 不使用缓存的直接处理
            return self._process_without_cache(text)
    
    def _process_without_cache(self, text: str) -> List[Dict[str, str]]:
        """不使用缓存的处理方法"""
        # Step 1: 分句并清洗
        sentences = self._split_and_clean_sentences(text)
        
        # Step 2: 逐句处理
        results = []
        for original_sentence in sentences:
            # 基础文本替换
            processed_sentence = self.text_replacer.apply_replacements(original_sentence)
            
            # 医学专业扩展
            processed_sentence = self.medical_expander.expand_all(processed_sentence)
            
            # 特殊处理：脊柱相关句子
            if self._contains_spine_content(processed_sentence):
                processed_sentence = self._apply_spine_processing(processed_sentence)
            
            # 条件性替换
            processed_sentence = self._apply_conditional_replacements(processed_sentence)
            
            # 最终清理
            processed_sentence = processed_sentence.strip()
            
            # 只保留有意义的结果
            if self._is_meaningful_sentence(processed_sentence):
                results.append({
                    "original": original_sentence,
                    "preprocessed": processed_sentence
                })
        
        return results
    
    def _split_and_clean_sentences(self, text: str) -> List[str]:
        """分句并清洗文本"""
        if not text or not isinstance(text, str):
            return []
        
        # 使用正则表达式分句
        sentences = re.split(self.sentence_pattern, text)
        
        # 清洗和过滤句子
        cleaned_sentences = []
        for sentence in sentences:
            # 去除前后空白
            sentence = sentence.strip()
            
            # 检查是否为有意义的句子
            if self._is_meaningful_sentence(sentence):
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _is_meaningful_sentence(self, sentence: str) -> bool:
        """判断句子是否有意义"""
        if not sentence:
            return False
        
        # 去除所有空白字符（包括全角和半角）
        cleaned = re.sub(r'[\s\u3000\u00A0]+', '', sentence)
        
        # 如果清洗后为空，则无意义
        if not cleaned:
            return False
        
        # 如果只包含标点符号，则无意义
        punctuation_chars = '。，、；：！？（）【】""''『』〈〉《》「」[](){}.,:;!?\\-_=+*/\\|<>~`@#$%^&'
        punctuation_pattern = '^[' + re.escape(punctuation_chars) + ']*$'
        if re.match(punctuation_pattern, cleaned):
            return False
        
        # 如果只包含数字和标点，且长度很短，可能无意义
        if len(cleaned) <= 2 and re.match(r'^[\d\.,\-+]+$', cleaned):
            return False
        
        # 如果只包含控制字符，则无意义
        control_chars_pattern = r'^[\x00-\x1f\x7f-\x9f]*$'
        if re.match(control_chars_pattern, cleaned):
            return False
        
        return True
    
    def _apply_conditional_replacements(self, sentence: str) -> str:
        """应用条件性替换规则"""

        condition_replacer = TextReplacer(version=self.version, modality=self.modality) 
        
        # 应用条件性替换规则
        return condition_replacer._apply_regex_replacements(sentence)
    

    
    def _contains_spine_content(self, text: str) -> bool:
        """检查是否包含脊柱相关内容"""
        if self.spine_words_regex:
            return bool(self.spine_words_regex.search(text))
        
        # 备用检查
        spine_keywords = ['椎', '横突', '棘', '脊', '黄韧带', '肋', '颈', '骶', '尾骨', '腰大肌']
        return any(keyword in text for keyword in spine_keywords)
    
    def _apply_spine_processing(self, text: str) -> str:
        """应用脊柱特殊处理"""
        # 获取脊柱相关的预编译正则表达式
        spine_patterns = [
            ('CERVICAL', r'\1颈\2'),
            ('THORACIC', r'\1胸\2'),
            ('THORACIC_VERTEBRA', r'\1胸\2'),
            ('SACRAL', r'\1骶\2'),
            ('THORACIC_SPECIFIC', r'\1胸\2'),
        ]
        
        for pattern_name, replacement in spine_patterns:
            try:
                pattern = self.regex_manager.get_pattern(pattern_name)
                text = pattern.sub(replacement, text)
            except KeyError:
                # 如果模式不存在，跳过
                continue
        
        return text
    
    @lru_cache(maxsize=1000)
    def _process_with_cache(self, text: str,  version: str, modality: str) -> List[Dict[str, str]]:
        """带缓存的处理方法 - 使用LRU缓存提升重复文本处理性能"""
        # 注意：由于LRU缓存要求参数可哈希，这里直接处理而不使用中间缓存方法
        
        # Step 1: 分句并清洗
        sentences = self._split_and_clean_sentences(text)
        
        # Step 2: 逐句处理
        results = []
        for original_sentence in sentences:
            # 基础文本替换
            processed_sentence = self.text_replacer.apply_replacements(original_sentence)
            
            # 医学专业扩展
            processed_sentence = self.medical_expander.expand_all(processed_sentence)
            
            # 特殊处理：脊柱相关句子
            if self._contains_spine_content(processed_sentence):
                processed_sentence = self._apply_spine_processing(processed_sentence)
            
            # 条件性替换
            processed_sentence = self._apply_conditional_replacements(processed_sentence)
            
            # 最终清理
            processed_sentence = processed_sentence.strip()
            
            # 只保留有意义的结果
            if self._is_meaningful_sentence(processed_sentence):
                results.append({
                    "original": original_sentence,
                    "preprocessed": processed_sentence
                })
        
        return results
    
    def get_info(self) -> Dict[str, Any]:
        """获取预处理器信息"""
        return {
            'version': self.version,
            'modality': self.modality,
            'enable_cache': self.enable_cache,
            'text_replacer_info': self.text_replacer.get_rule_info(),
            'config_version': self.config_manager.get_version_info(),
            'available_patterns': len(self.regex_manager.get_all_patterns())
        }
    
    def reload_config(self):
        """重新加载配置和规则"""
        print("重新加载配置...")
        
        # 重新加载各个组件
        self.config_manager = get_config_manager()
        self.text_replacer.reload_rules()
        self.medical_expander = MedicalExpander()
        
        # 重新加载模式
        self._load_patterns()
        
        # 清除所有缓存
        self.clear_cache()
        
        print("配置重新加载完成")
    
    def validate_input(self, text: str) -> bool:
        """验证输入文本"""
        if not isinstance(text, str):
            return False
        
        if len(text.strip()) == 0:
            return False
        
        # 可以添加更多验证规则
        return True
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        cache_info = None
        if self.enable_cache and hasattr(self, '_process_with_cache'):
            cache_info = self._process_with_cache.cache_info()
        
        return {
            'cache_info': cache_info,
            'cache_enabled': self.enable_cache,
            'replacer_stats': self.text_replacer.get_rule_info(),
            'config_stats': self.config_manager.get_version_info()
        }
    
    def clear_cache(self):
        """清除缓存"""
        if hasattr(self, '_process_with_cache'):
            self._process_with_cache.cache_clear()
            print("缓存已清除")
        else:
            print("无缓存需要清除")
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """获取缓存信息"""
        if self.enable_cache and hasattr(self, '_process_with_cache'):
            cache_info = self._process_with_cache.cache_info()
            return {
                'hits': cache_info.hits,
                'misses': cache_info.misses,
                'maxsize': cache_info.maxsize,
                'currsize': cache_info.currsize,
                'hit_rate': cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0
            }
        return None

# 便捷函数
def create_preprocessor(version: str = '报告', modality: str = '通用', enable_cache: bool = True) -> Preprocessor:
    """创建预处理器实例"""
    return Preprocessor(version=version, modality=modality, enable_cache=enable_cache)

# 全局默认预处理器
_default_preprocessor = None

def get_default_preprocessor() -> Preprocessor:
    """获取默认预处理器实例"""
    global _default_preprocessor
    if _default_preprocessor is None:
        _default_preprocessor = create_preprocessor()
    return _default_preprocessor

def preprocess_text(text: str, version: str = '报告', modality: str = '通用') -> List[Dict[str, str]]:
    """便捷函数：预处理文本
    
    Args:
        text: 待处理的原始医学文本
        version: 规则版本（报告/标题/申请单）
        modality: 设备类型（通用/CT/MR/DR/病理/超声）
        
    Returns:
        包含分句结果的列表，每个元素为字典
        格式: [{"original": 原始句子1, "preprocessed": 处理后的句子1}, ...]
    """
    if version == '报告' and modality == '通用':
        # 使用默认预处理器
        return get_default_preprocessor().process(text)
    else:
        # 创建专用预处理器
        preprocessor = create_preprocessor(version=version, modality=modality)
        return preprocessor.process(text)
