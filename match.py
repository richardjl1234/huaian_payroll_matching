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
    # Get sheet name from payroll record
    sheet_name = payroll_record['sheet名']
    
    # Calculate effected_from with both file_name and sheet_name
    effected_from = calculate_effected_from(file_name, sheet_name)
    # print the value of effected_from
    print(f"the value of {effected_from =}")
    
    
    # Filter 1: quota_data[类别1] in category_mapping[sheet名][effected_from]
    # and quota_data[effected_from] == effected_from
    
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



def main():
    """
    Main function to match payroll records with quota data
    """
    print("=" * 60)
    print("工资记录与定额数据匹配程序")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python match.py <文件名前缀> [工作表名]")
        print("例如: python match.py 202005")
        print("      python match.py 202005 精加工")
        print("当只提供文件名前缀时，处理所有相关记录")
        print("当提供工作表名时，只处理指定工作表的记录")
        return
    
    file_prefix = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) == 3 else None
    
    if sheet_name:
        print(f"正在处理文件名前缀为 '{file_prefix}'，工作表名为 '{sheet_name}' 的记录")
    else:
        print(f"正在处理文件名前缀为 '{file_prefix}' 的所有记录")
    print()
    
    # Step a: Call query_quota_table and store as quota_data
    print("正在查询定额数据...")
    quota_data = query_quota_table()
    print(f"获取到 {len(quota_data)} 条定额记录")
    print()
    
    # Step b: Call payroll_generator with the file prefix and optional sheet name
    print(f"正在处理文件前缀: {file_prefix}")
    if sheet_name:
        print(f"工作表名: {sheet_name}")
    print()
    
    # Reconstruct file name for display and filter purposes
    file_name = f"{file_prefix}.xls"
    
    generator = payroll_records_gen(file_prefix, sheet_name)
    
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
            
            # Display detailed filter information
            print(f"过滤条件详情:")
            print(f"  文件名: {file_name}")
            print(f"  工作表名: {payroll_record['sheet名']}")
            print(f"  生效日期: {calculate_effected_from(file_name, payroll_record['sheet名'])}")
            print(f"  定额值: {payroll_record['定额']}")
            print()
            
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
                        print("-" * 80)
                        
                        # Create a DataFrame for better formatting
                        import pandas as pd
                        
                        # Prepare data for DataFrame
                        records_data = []
                        for i, record in enumerate(filtered_data, 1):
                            record_data = {
                                '记录': f'记录{i}',
                                '类别1': record.get('类别1', 'N/A'),
                                '类别2': record.get('类别2', 'N/A'),
                                '加工工序': record.get('加工工序', 'N/A'),
                                '型号': record.get('型号', 'N/A'),
                                '定额': record.get('定额', 'N/A'),
                                'effected_from': record.get('effected_from', 'N/A')
                            }
                            records_data.append(record_data)
                        
                        # Create DataFrame and transpose it
                        df = pd.DataFrame(records_data)
                        df_transposed = df.set_index('记录')
                        
                        # Display the transposed DataFrame
                        print(df_transposed.to_string())
                        print("-" * 80)
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
