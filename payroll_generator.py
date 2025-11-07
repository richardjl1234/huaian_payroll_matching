#!/usr/bin/env python3
"""
Payroll Records Generator
A Python program that generates payroll records using a generator function.
"""

import sqlite3
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


def payroll_records_gen(filename):
    """
    Generator function that yields payroll records one at a time.
    
    Args:
        filename (str): The filename to use in the SQL query template
        
    Yields:
        dict: A payroll record from the database
    """
    # SQL template as specified
    sql_template = "select * from payroll_details where 文件名 = '{}';"
    sql_query = sql_template.format(filename)
    
    print(f"Executing: {sql_query}")
    
    try:
        # Connect to the actual database
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(sql_query)
        
        # Yield records one by one
        for row in cursor:
            # Convert sqlite3.Row to dictionary
            record = dict(row)
            yield record
            
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return
    finally:
        if 'conn' in locals():
            conn.close()


def format_record(record):
    """
    Format a payroll record for display.
    
    Args:
        record (dict): The payroll record to format
        
    Returns:
        str: Formatted record string
    """
    return f"""
文件名: {record['文件名']}
工作表名: {record['sheet名']}
职员全名: {record['职员全名']}
日期: {record['日期']}
客户名称: {record['客户名称']}
型号: {record['型号']}
工序全名: {record['工序全名']}
工序: {record['工序']}
计件数量: {record['计件数量']}
系数: {record['系数']}
定额: {record['定额']}
金额: ¥{record['金额']:,.2f}
备注: {record['备注']}
{'='*50}
"""


def main():
    """
    Main function with testing code as specified.
    """
    print("=" * 60)
    print("工资记录生成器 - Payroll Records Generator")
    print("=" * 60)
    
    # Test with the specified filename
    filename = "202006.xls"
    print(f"正在处理文件: {filename}")
    print()
    
    # Create the generator
    generator = payroll_records_gen(filename)
    
    try:
        # Generate and display records one by one
        while True:
            record = next(generator)
            print(format_record(record))
            
            # Wait for user input to continue
            input("按 Enter 键继续生成下一条记录...")
            print()
            
    except StopIteration:
        print("所有记录已生成完毕！")
        print("程序结束。")


if __name__ == "__main__":
    main()
