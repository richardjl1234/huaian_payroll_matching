#!/usr/bin/env python3
"""
Match payroll records with quota data
"""

import sys
import os

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from query_quota_table import query_quota_table
from payroll_generator import payroll_records_gen, format_record
from config import category_mapping, calculate_effected_from


def filter_quota_data(quota_data, payroll_record, file_name):
    """
    Filter quota data based on payroll record information
    
    Args:
        quota_data (list): List of quota data dictionaries
        payroll_record (dict): Payroll record from generator
        file_name (str): The filename being processed
        
    Returns:
        tuple: (filter1_count, filter2_count, filtered_data)
    """
    # Calculate effected_from
    effected_from = calculate_effected_from(file_name)
    
    # Filter 1: quota_data[类别1] in category_mapping[sheet名][effected_from]
    # and quota_data[effected_from] == effected_from
    sheet_name = payroll_record['sheet名']
    
    if sheet_name in category_mapping and effected_from in category_mapping[sheet_name]:
        valid_categories = category_mapping[sheet_name][effected_from]
    else:
        valid_categories = []
    
    filter1_data = []
    for item in quota_data:
        if (item.get('类别1') in valid_categories and 
            item.get('effected_from') == effected_from):
            filter1_data.append(item)
    
    filter1_count = len(filter1_data)
    
    # Filter 2: quota_data[定额] == returned_record[定额]
    filter2_data = []
    for item in filter1_data:
        if item.get('定额') == payroll_record['定额']:
            filter2_data.append(item)
    
    filter2_count = len(filter2_data)
    
    return filter1_count, filter2_count, filter2_data


def format_quota_record(record):
    """
    Format a quota record for display
    
    Args:
        record (dict): Quota record to format
        
    Returns:
        str: Formatted record string
    """
    return f"""
类别1: {record.get('类别1', 'N/A')}
类别2: {record.get('类别2', 'N/A')}
加工工序: {record.get('加工工序', 'N/A')}
型号: {record.get('型号', 'N/A')}
定额: {record.get('定额', 'N/A')}
effected_from: {record.get('effected_from', 'N/A')}
{'='*40}
"""


def main():
    """
    Main function to match payroll records with quota data
    """
    print("=" * 60)
    print("工资记录与定额数据匹配程序")
    print("=" * 60)
    
    # Step a: Call query_quota_table and store as quota_data
    print("正在查询定额数据...")
    quota_data = query_quota_table()
    print(f"获取到 {len(quota_data)} 条定额记录")
    print()
    
    # Step b: Set filename and call payroll_generator
    file_name = '202006.xls'
    print(f"正在处理文件: {file_name}")
    print()
    
    generator = payroll_records_gen(file_name)
    
    try:
        # Process records one by one
        while True:
            payroll_record = next(generator)
            
            # Display the payroll record
            print("当前工资记录:")
            print(format_record(payroll_record))
            
            # Step c: Filter quota data
            filter1_count, filter2_count, filtered_data = filter_quota_data(
                quota_data, payroll_record, file_name
            )
            
            print(f"过滤结果:")
            print(f"  过滤条件1匹配的记录数: {filter1_count}")
            print(f"  过滤条件1+2匹配的记录数: {filter2_count}")
            print()
            
            # Prompt user for options
            while True:
                print("请选择操作:")
                print("1. 显示所有匹配过滤条件1+2的定额记录")
                print("2. 处理下一条工资记录")
                print("3. 退出程序")
                
                choice = input("请输入选择 (1/2/3): ").strip()
                
                if choice == '1':
                    if filtered_data:
                        print(f"\n显示 {len(filtered_data)} 条匹配的定额记录:")
                        print("-" * 40)
                        for record in filtered_data:
                            print(format_quota_record(record))
                    else:
                        print("没有匹配的定额记录")
                    print()
                    
                elif choice == '2':
                    print()
                    break
                    
                elif choice == '3':
                    print("程序结束。")
                    return
                    
                else:
                    print("无效选择，请重新输入")
                    print()
            
    except StopIteration:
        print("所有工资记录已处理完毕！")
        print("程序结束。")


if __name__ == "__main__":
    main()
