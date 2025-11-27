#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive test program for calculate_effected_from function
Allows users to input file names and sheet names to test the function
"""

import sys
import os

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import calculate_effected_from, category_mapping


def display_available_sheets():
    """Display available sheet names from category_mapping"""
    print("\n" + "=" * 60)
    print("可用的工作表名称:")
    print("=" * 60)
    for sheet_name in category_mapping.keys():
        print(f"  - {sheet_name}")
    print()


def display_available_dates_for_sheet(sheet_name):
    """Display available dates for a specific sheet"""
    if sheet_name in category_mapping:
        print(f"\n工作表 '{sheet_name}' 可用的生效日期:")
        for date in sorted(category_mapping[sheet_name].keys()):
            print(f"  - {date}")
    else:
        print(f"\n工作表 '{sheet_name}' 不在配置中")


def test_single_case():
    """Test a single case with user input"""
    print("\n" + "=" * 60)
    print("测试单个用例")
    print("=" * 60)
    
    # Get file name from user
    while True:
        file_name = input("\n请输入文件名 (例如: 202005.xls, 202101_1.xlsx): ").strip()
        if file_name:
            break
        print("文件名不能为空，请重新输入")
    
    # Display available sheets
    display_available_sheets()
    
    # Get sheet name from user
    while True:
        sheet_name = input("请输入工作表名称: ").strip()
        if sheet_name:
            if sheet_name in category_mapping:
                break
            else:
                print(f"工作表 '{sheet_name}' 不在配置中，请从上面的列表中选择")
                display_available_sheets()
        else:
            print("工作表名称不能为空，请重新输入")
    
    # Display available dates for the selected sheet
    display_available_dates_for_sheet(sheet_name)
    
    # Get expected result from user (optional)
    expected = input("\n请输入期望结果 (可选，按回车跳过): ").strip()
    
    # Test the function
    print(f"\n正在测试...")
    print(f"  文件名: {file_name}")
    print(f"  工作表名: {sheet_name}")
    
    try:
        result = calculate_effected_from(file_name, sheet_name)
        print(f"  实际结果: {result}")
        
        if expected:
            if result == expected:
                print("  ✅ 结果与期望一致")
            else:
                print(f"  ❌ 结果与期望不一致")
                print(f"     期望: {expected}")
                print(f"     实际: {result}")
        else:
            print("  ℹ️  未提供期望结果，请手动验证")
            
    except Exception as e:
        print(f"  ❌ 测试失败 - 异常: {e}")
    
    return result


def batch_test_mode():
    """Allow user to test multiple cases in batch mode"""
    print("\n" + "=" * 60)
    print("批量测试模式")
    print("=" * 60)
    
    test_cases = []
    
    while True:
        print(f"\n当前测试用例数量: {len(test_cases)}")
        print("1. 添加测试用例")
        print("2. 运行所有测试用例")
        print("3. 清空测试用例")
        print("4. 返回主菜单")
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            # Add test case
            print("\n添加测试用例:")
            file_name = input("文件名: ").strip()
            sheet_name = input("工作表名: ").strip()
            expected = input("期望结果 (可选): ").strip()
            
            if file_name and sheet_name:
                test_cases.append({
                    'file_name': file_name,
                    'sheet_name': sheet_name,
                    'expected': expected if expected else None
                })
                print("✅ 测试用例已添加")
            else:
                print("❌ 文件名和工作表名不能为空")
                
        elif choice == "2":
            # Run all test cases
            if not test_cases:
                print("❌ 没有测试用例可运行")
                continue
                
            print(f"\n运行 {len(test_cases)} 个测试用例...")
            passed = 0
            failed = 0
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n测试用例 {i}:")
                print(f"  文件名: {test_case['file_name']}")
                print(f"  工作表名: {test_case['sheet_name']}")
                
                try:
                    result = calculate_effected_from(test_case['file_name'], test_case['sheet_name'])
                    print(f"  实际结果: {result}")
                    
                    if test_case['expected']:
                        if result == test_case['expected']:
                            print("  ✅ 测试通过")
                            passed += 1
                        else:
                            print(f"  ❌ 测试失败 - 期望: {test_case['expected']}, 实际: {result}")
                            failed += 1
                    else:
                        print("  ℹ️  未设置期望结果")
                        
                except Exception as e:
                    print(f"  ❌ 测试失败 - 异常: {e}")
                    failed += 1
            
            print(f"\n测试结果: 通过 {passed}, 失败 {failed}, 总计 {len(test_cases)}")
            
        elif choice == "3":
            # Clear test cases
            test_cases.clear()
            print("✅ 所有测试用例已清空")
            
        elif choice == "4":
            # Return to main menu
            break
            
        else:
            print("❌ 无效选择，请选择 1-4")


def show_function_info():
    """Display information about the calculate_effected_from function"""
    print("\n" + "=" * 60)
    print("函数信息")
    print("=" * 60)
    print("函数名: calculate_effected_from")
    print("功能: 根据文件名和工作表名计算生效日期")
    print("参数:")
    print("  - file_name: 文件名 (例如: '202006.xls', '202005_1.xlsx')")
    print("  - sheet_name: 工作表名 ('精加工', '喷漆装配', '绕嵌排')")
    print("返回值: 生效日期字符串 (例如: '19000101', '20200401', '20201201')")
    print()
    print("算法说明:")
    print("  1. 从文件名中提取年月 (前6位数字)")
    print("  2. 在工作表的可用日期中查找")
    print("  3. 返回小于等于目标日期的最大可用日期")
    print("  4. 如果没有找到，返回最早的可用日期")
    print()


def main():
    """Main interactive test program"""
    print("=" * 60)
    print("calculate_effected_from 函数交互式测试程序")
    print("=" * 60)
    
    while True:
        print("\n请选择测试模式:")
        print("1. 测试单个用例")
        print("2. 批量测试模式")
        print("3. 查看函数信息")
        print("4. 查看可用工作表")
        print("5. 退出程序")
        
        choice = input("\n请选择操作 (1-5): ").strip()
        
        if choice == "1":
            test_single_case()
            
        elif choice == "2":
            batch_test_mode()
            
        elif choice == "3":
            show_function_info()
            
        elif choice == "4":
            display_available_sheets()
            
        elif choice == "5":
            print("\n感谢使用测试程序！")
            break
            
        else:
            print("❌ 无效选择，请选择 1-5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序发生错误: {e}")
