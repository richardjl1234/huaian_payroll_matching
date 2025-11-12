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

def calculate_effected_from(file_name, sheet_name):
    """
    Calculate the effected_from value based on file_name and sheet_name.
    this is to determine which quota sheet will be used. 
    
    Args:
        file_name (str): The filename (e.g., '202006.xls', '202005_1.xlsx')
        sheet_name (str): the sheet name in the payroll slip (can be "精加工", 
        "喷漆装配", "绕嵌排")
        
    Returns:
        str: The effected_from value (e.g., '19000101', '20200401', '20201201')
    """
    # Extract year and month from filename (first 6 characters)
    # Handle patterns like YYYYMM.xls, YYYYMM_x.xls, YYYYMM.xlsx, YYYYMM_x.xlsx
    import re
    
    # Extract the first 6 digits from the filename
    match = re.search(r'^(\d{6})', file_name)
    if not match:
        raise ValueError(f"Cannot extract year and month from filename: {file_name}")
    
    yyyymm = match.group(1)
    year = int(yyyymm[:4])
    month = int(yyyymm[4:6])
    
    # Get the target date in YYYYMM format for comparison
    target_date = year * 100 + month
    
    # Check if sheet_name exists in category_mapping
    if sheet_name not in category_mapping:
        raise ValueError(f"Sheet name '{sheet_name}' not found in category_mapping")
    
    # Get available date keys for this sheet
    available_dates = list(category_mapping[sheet_name].keys())
    
    # Convert date strings to integers and extract YYYYMM part for comparison
    date_ints = [int(date[:6]) for date in available_dates]
    
    # Find the largest date that is <= target_date
    valid_dates = [date for date in date_ints if date <= target_date]
    
    if not valid_dates:
        # If no valid dates found, use the earliest available date
        return min(available_dates)
    
    # Return the largest valid date (most recent that is <= target_date)
    max_valid_date = max(valid_dates)
    
    # Find the original date string that matches the YYYYMM part
    for date_str in available_dates:
        if int(date_str[:6]) == max_valid_date:
            return date_str
    
    # Fallback: return the earliest available date
    return min(available_dates)

# the structure of the following dictionary
# "精加工": the sheet name in the payroll file
# "20200401": the effected from date for a given quota sheet
# the value is the list of the sheet name in quota file 

category_mapping = {
    "精加工":{ 
        "19000101": [], 
        "20200401":["机座","端盖","轴","转子"] ,
        },
    "喷漆装配":{
        "19000101": [], 
        "20200401":["装配","特殊电机装配"] ,
        },
    "绕嵌排":{ 
        "19000101": ["绕嵌排"], 
        "20200401": ["绕嵌排"], 
        "20201201": ["绕嵌排"], 
        "20210101": ["绕嵌排"], 
        "20211001": ["绕嵌排"], 
        "20211201": ["绕嵌排"], 
          }
}
