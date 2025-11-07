#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Configuration file for the quota processing system
# Get the absolute path of the current directory
CURRENT_DIR = Path(__file__).parent

# Database path - absolute path
DATABASE_PATH = str(CURRENT_DIR.parent / "payroll_database.db")

# Common directory path - absolute path
COMMON = str(CURRENT_DIR.parent / "common")

# Translation dictionary path - absolute path
TRANSLATION_DICT = str(CURRENT_DIR.parent / "common" / "translation_dict.pkl")

# 20200401
# 精加工里有：机座，端盖，轴，转子。喷漆装配就是装配和特殊电机装配。
# 绕嵌排 对应 绕嵌排
# 19000101 TODO

def calculate_effected_from(file_name):
    """
    Calculate the effected_from value based on file_name.
    For now, hardcoded to return 20200401.
    
    Args:
        file_name (str): The filename (e.g., '202006.xls')
        
    Returns:
        str: The effected_from value ('20200401' or '19000101')
    """
    # TODO: Implement proper logic for calculating effected_from
    # For now, hardcoded to return 20200401
    return "20200401"


category_mapping = {
    "精加工":{ "20200401":["机座","端盖","轴","转子"] },
    "喷漆装配":{"20200401":["装配","特殊电机装配"] },
    "绕嵌排":{ "20200401":["绕嵌排"] }
}
