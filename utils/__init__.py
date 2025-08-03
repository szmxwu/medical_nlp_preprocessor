#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具模块
"""

from .text_utils import (
    timing_decorator,
    clean_whitespace,
    normalize_punctuation,
    remove_numbered_prefix,
    split_sentences,
    is_valid_medical_text,
    extract_numbers,
    extract_measurements,
    contains_keywords,
    highlight_keywords,
    truncate_text,
    count_chinese_chars,
    validate_regex_pattern,
    safe_regex_replace,
    TextStatistics,
    COMMON_PATTERNS,
    get_pattern
)

__all__ = [
    'timing_decorator',
    'clean_whitespace', 
    'normalize_punctuation',
    'remove_numbered_prefix',
    'split_sentences',
    'is_valid_medical_text',
    'extract_numbers',
    'extract_measurements',
    'contains_keywords',
    'highlight_keywords',
    'truncate_text',
    'count_chinese_chars',
    'validate_regex_pattern',
    'safe_regex_replace',
    'TextStatistics',
    'COMMON_PATTERNS',
    'get_pattern'
]
