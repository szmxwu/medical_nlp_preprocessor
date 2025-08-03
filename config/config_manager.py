#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
统一管理所有配置文件的加载和访问
"""

import configparser
import json
import os
from functools import lru_cache
from typing import Dict, Any, Optional
from .regex_patterns import get_regex_manager, compile_pattern

class ConfigManager:
    """配置管理类"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，如果为None则使用默认路径
        """
        self.config_dir = config_dir or os.path.dirname(os.path.abspath(__file__))
        self._ini_config = None
        self._version_info = None
        self._compiled_patterns = {}
        
        self._load_all_configs()
    
    def _load_all_configs(self):
        """加载所有配置文件"""
        self._load_ini_config()
        self._load_version_info()
        self._compile_config_patterns()
    
    def _load_ini_config(self):
        """加载INI配置文件"""
        # 优先查找新位置的配置文件，然后查找原始位置
        config_paths = [
            os.path.join(self.config_dir, '..', 'data', 'system_config.ini'),
            'user_input_files/system_config.ini'
        ]
        
        self._ini_config = configparser.ConfigParser()
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                self._ini_config.read(config_path, encoding='utf-8')
                print(f"加载配置文件: {config_path}")
                break
        else:
            raise FileNotFoundError("找不到system_config.ini配置文件")
    
    def _load_version_info(self):
        """加载版本信息"""
        version_path = os.path.join(self.config_dir, '..', 'data', 'version_info.json')
        
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                self._version_info = json.load(f)
        else:
            self._version_info = {'version': 'unknown', 'date': 'unknown'}
    
    def _compile_config_patterns(self):
        """编译配置文件中的正则表达式"""
        regex_manager = get_regex_manager()
        
        # 编译配置文件中的关键正则表达式
        config_patterns = {
            'STOP_PATTERN': self.get('sentence', 'stop_pattern'),
            'SENTENCE_PATTERN': self.get('sentence', 'sentence_pattern'),
            'NORM_KEYWORDS': self.get('positive', 'NormKeyWords'),
            'ILLNESS_WORDS': self.get('positive', 'illness_words'),
            'SPINE_WORDS': self.get('clean', 'spine'),
            'IGNORE_SENTENCE': self.get('clean', 'Ignore_sentence'),
            'STOPWORDS': self.get('clean', 'stopwords'),
        }
        
        for name, pattern_str in config_patterns.items():
            if pattern_str:
                self._compiled_patterns[name] = compile_pattern(pattern_str)
    
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """获取配置值
        
        Args:
            section: 配置节名
            option: 配置项名
            fallback: 默认值
            
        Returns:
            配置值
        """
        if self._ini_config:
            return self._ini_config.get(section, option, fallback=fallback)
        return fallback
    
    def get_list(self, section: str, option: str, separator: str = '|', fallback: list = None) -> list:
        """获取配置值并按分隔符分割为列表
        
        Args:
            section: 配置节名
            option: 配置项名
            separator: 分隔符
            fallback: 默认值
            
        Returns:
            配置值列表
        """
        value = self.get(section, option)
        if value:
            return value.split(separator)
        return fallback or []
    
    def get_compiled_pattern(self, pattern_name: str):
        """获取编译后的正则表达式
        
        Args:
            pattern_name: 模式名称
            
        Returns:
            编译后的正则表达式对象
        """
        return self._compiled_patterns.get(pattern_name)
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        return self._version_info or {}
    
    def get_all_config_data(self) -> Dict[str, Any]:
        """获取所有配置数据，用于调试"""
        config_data = {}
        
        if self._ini_config:
            for section in self._ini_config.sections():
                config_data[section] = dict(self._ini_config.items(section))
        
        config_data['version_info'] = self._version_info
        config_data['compiled_patterns'] = list(self._compiled_patterns.keys())
        
        return config_data

# 全局配置管理器实例
_config_manager = None

@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例（单例模式）"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# 便捷函数
def get_config(section: str, option: str, fallback: Any = None) -> str:
    """便捷函数：获取配置值"""
    return get_config_manager().get(section, option, fallback)

def get_config_list(section: str, option: str, separator: str = '|', fallback: list = None) -> list:
    """便捷函数：获取配置列表"""
    return get_config_manager().get_list(section, option, separator, fallback)

def get_config_pattern(pattern_name: str):
    """便捷函数：获取编译后的正则表达式"""
    return get_config_manager().get_compiled_pattern(pattern_name)
