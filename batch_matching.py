#!/usr/bin/env python3
"""
Batch Matching Program
Process payroll records in batch mode to match with quota data
"""

import sys
import os

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from query_quota_table import query_quota_table
from payroll_generator import payroll_records_gen
from match import filter_quota_data, final_decision, NODECISION


def main():
    """
    Main function for batch matching
    """
    print("=" * 60)
    print("批量匹配程序 - Batch Matching Program")
    print("=" * 60)
    
    # Step 1: Load quota data
    print("正在查询定额数据...")
    quota_data = query_quota_table()
    print(f"获取到 {len(quota_data)} 条定额记录")
    print()
    
    # Step 2: Create payroll records generator (no file_name prefix to get all records)
    print("正在获取工资记录...")
    generator = payroll_records_gen()  # No parameters to get all records
    
    # Counter for processed records
    processed_count = 0
    success_count = 0
    skip_count = 0
    error_count = 0
    
    try:
        # Process records one by one (limit to first 100 records for now)
        while processed_count < 100:
            payroll_record = next(generator)
            processed_count += 1
            
            print(f"\n处理记录 #{processed_count}:")
            print(f"  文件名: {payroll_record['文件名']}")
            print(f"  工作表名: {payroll_record['sheet名']}")
            print(f"  职员: {payroll_record['职员全名']}")
            print(f"  定额: {payroll_record['定额']}")
            
            # Skip if quota is 0
            if payroll_record['定额'] == 0:
                print("  → 定额为0，跳过匹配")
                skip_count += 1
                continue
            
            # Get file name from payroll record
            file_name = payroll_record['文件名']
            
            try:
                # Step 3: Filter quota data
                filter1_count, filter2_count, filtered_data = filter_quota_data(
                    quota_data, payroll_record, file_name
                )
                
                print(f"  过滤结果: 条件1={filter1_count}, 条件1+2={filter2_count}")
                
                # Step 4: Make final decision
                if filter2_count > 0:
                    decision_code = final_decision(payroll_record, filtered_data)
                    print(f"  → 最终决策代码: {decision_code}")
                    success_count += 1
                else:
                    print(f"  → 无匹配记录")
                    skip_count += 1
                    
            except NODECISION as e:
                print(f"  → 决策失败: {e}")
                error_count += 1
            except Exception as e:
                print(f"  → 处理错误: {e}")
                error_count += 1
        
        print(f"\n处理完成 (限制前100条记录)")
        
    except StopIteration:
        print(f"\n所有记录已处理完毕 (共 {processed_count} 条记录)")
    
    # Print summary
    print("\n" + "=" * 60)
    print("处理摘要:")
    print(f"  总处理记录数: {processed_count}")
    print(f"  成功匹配数: {success_count}")
    print(f"  跳过数 (定额为0或无匹配): {skip_count}")
    print(f"  错误数: {error_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
