#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医学NLP文本预处理模块
Medical NLP Text Preprocessor

重构后的医学文本预处理功能，提供模块化、高性能、易扩展的预处理能力

主要功能:
- 统一的文本替换引擎
- 医学专业术语扩展
- 配置和规则管理
- 高性能正则表达式处理

使用示例:
    from medical_nlp_preprocessor import preprocess_text, create_preprocessor
    
    # 简单使用
    results = preprocess_text("第一句话。第二句话。")
    for result in results:
        print(f"原始文本: {result['original']}")
        print(f"处理后文本: {result['preprocessed']}")
    
    # 高级使用
    preprocessor = create_preprocessor(version='报告', modality='CT')
    results = preprocessor.process("第一句话。第二句话。")
    for result in results:
        print(f"原始文本: {result['original']}")
        print(f"处理后文本: {result['preprocessed']}")
"""

__version__ = "1.0.0"
__author__ = "MiniMax Agent"
__description__ = "医学NLP文本预处理模块 - 重构版"

# 导入主要类和函数
from .core.preprocessor import Preprocessor, create_preprocessor, preprocess_text
from .core.text_replacer import TextReplacer, create_replacer
from .extensions.medical_expander import MedicalExpander, expand_medical_terms
from .config.config_manager import ConfigManager, get_config_manager
from .data.rule_loader import RuleLoader, load_replacement_rules

# 导入便捷函数
from .utils.text_utils import (
    timing_decorator,
    clean_whitespace,
    normalize_punctuation,
    split_sentences,
    is_valid_medical_text
)

# 定义公开的API
__all__ = [
    # 核心功能
    'Preprocessor',
    'TextReplacer', 
    'MedicalExpander',
    'ConfigManager',
    'RuleLoader',
    
    # 便捷函数
    'preprocess_text',
    'create_preprocessor',
    'create_replacer',
    'expand_medical_terms',
    'load_replacement_rules',
    'get_config_manager',
    
    # 工具函数
    'timing_decorator',
    'clean_whitespace',
    'normalize_punctuation',
    'split_sentences',
    'is_valid_medical_text',
    
    # 版本信息
    '__version__',
    '__author__',
    '__description__'
]

# 模块信息
def get_version_info():
    """获取版本信息"""
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'components': {
            'core': ['Preprocessor', 'TextReplacer'],
            'extensions': ['MedicalExpander'],
            'config': ['ConfigManager', 'RegexPatterns'],
            'data': ['RuleLoader'],
            'utils': ['text_utils']
        }
    }

def get_supported_modalities():
    """获取支持的设备类型"""
    return ['通用', 'CT', 'MR', 'DR', '病理', '超声']

def get_supported_versions():
    """获取支持的规则版本"""
    return ['报告', '标题', '申请单']

def quick_test():
    """快速测试功能"""
    test_text = """
    急诊报告： 与2023/1/7日片比较: 两肺多发斑片渗出实变影，边界不清,内见空洞形成
    双侧胸腔少量积液与前相仿，双肺下叶膨胀不全，右肺下叶较前改善；左侧斜裂胸膜积液较前减少。
    双肺见多发片状模糊影及片状影，部分实变。双肺下叶部分支气管狭窄，余气管及主要支气管通畅。
    未见左侧肺门及右纵隔增大淋巴结。心脏增大，心腔密度减低，主动脉、冠状动脉钙化；心包少量积液。
    附见：右侧部分肋骨陈旧性骨折。
    与2022/8/23日片比较: 肝脏增大。肝实质密度均匀，肝左外叶见低密度灶。无肝内外胆管明显扩张。肝脾周围可见积液；
    腹腔内脂肪间隙稍模糊。 胆囊内可见团片状稍高密度影，范围约53×19mm，形态不规则。
    胰腺形态大小、密度未见异常，胰管未见明显扩张。 脾脏形态、大小、密度未见明确异常。
    双肾形态、大小、密度未见明显异常，双侧肾盂、肾盏未见明显扩张积水。 膀胱欠充盈显示不清。
    前列腺形态、大小及密度未见异常。 小肠稍积液；腹主动脉及双侧髂动脉钙化。腹膜后未见明显增大淋巴结。盆腔少量积液。
    腰椎骨质增生。 附见：心脏增大，心腔密度减低，CT值约31HU；主动脉及冠脉钙化；心包积液。右下肺节段性体积缩小。
    与2022/6/23日片比较: 双侧基底节区少许小斑点状低密度影，余脑实质内未见异常密度影。脑沟稍增宽，腔内无异常密度影。
    颅内中线结构居中。双侧颈内动脉颅内段可见钙化,边界不清。
    """
    
    try:
        results = preprocess_text(test_text)
        print(f"快速测试成功:")
        print(f"输入文本: {test_text}")
        print(f"分句结果数量: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"句子{i} - 原始: {result['original']}")
            print(f"句子{i} - 处理后: {result['preprocessed']}")
        return True
    except Exception as e:
        print(f"快速测试失败: {e}")
        return False

# 初始化日志
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
