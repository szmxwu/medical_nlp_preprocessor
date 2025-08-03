#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据管理模块
"""

from .rule_loader import RuleLoader, ReplacementRule, get_rule_loader, load_replacement_rules

__all__ = [
    'RuleLoader',
    'ReplacementRule',
    'get_rule_loader',
    'load_replacement_rules'
]
