#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test program for calculate_effected_from function
"""

import sys
import os

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import calculate_effected_from, category_mapping


def test_calculate_effected_from():
    """
    Test the calculate_effected_from function with various test cases
    """
    print("=" * 60)
    print("Testing calculate_effected_from function")
    print("=" * 60)
    
    test_cases = [
        # Test case 1: year=2015, month=05, sheet_name='绕嵌排' -> should return '19000101'
        {
            'file_name': '201505.xls',
            'sheet_name': '绕嵌排',
            'expected': '19000101',
            'description': '2015年5月 绕嵌排 - 应该返回 19000101'
        },
        # Test case 2: year=2020, month=05, sheet_name='绕嵌排' -> should return '20200401'
        {
            'file_name': '202005.xls',
            'sheet_name': '绕嵌排',
            'expected': '20200401',
            'description': '2020年5月 绕嵌排 - 应该返回 20200401'
        },
        # Test case 3: year=2020, month=12, sheet_name='绕嵌排' -> should return '20201201'
        {
            'file_name': '202012.xlsx',
            'sheet_name': '绕嵌排',
            'expected': '20201201',
            'description': '2020年12月 绕嵌排 - 应该返回 20201201'
        },
        # Test case 4: year=2021, month=01, sheet_name='绕嵌排' -> should return '20210101'
        {
            'file_name': '202101_1.xls',
            'sheet_name': '绕嵌排',
            'expected': '20210101',
            'description': '2021年1月 绕嵌排 - 应该返回 20210101'
        },
        # Test case 5: year=2021, month=10, sheet_name='绕嵌排' -> should return '20211001'
        {
            'file_name': '202110.xlsx',
            'sheet_name': '绕嵌排',
            'expected': '20211001',
            'description': '2021年10月 绕嵌排 - 应该返回 20211001'
        },
        # Test case 6: year=2021, month=12, sheet_name='绕嵌排' -> should return '20211201'
        {
            'file_name': '202112_2.xls',
            'sheet_name': '绕嵌排',
            'expected': '20211201',
            'description': '2021年12月 绕嵌排 - 应该返回 20211201'
        },
        # Test case 7: year=2022, month=01, sheet_name='绕嵌排' -> should return '20211201' (latest available)
        {
            'file_name': '202201.xls',
            'sheet_name': '绕嵌排',
            'expected': '20211201',
            'description': '2022年1月 绕嵌排 - 应该返回 20211201 (最新可用)'
        },
        # Test case 8: year=2020, month=04, sheet_name='精加工' -> should return '20200401'
        {
            'file_name': '202004.xls',
            'sheet_name': '精加工',
            'expected': '20200401',
            'description': '2020年4月 精加工 - 应该返回 20200401'
        },
        # Test case 9: year=2019, month=12, sheet_name='精加工' -> should return '19000101'
        {
            'file_name': '201912.xlsx',
            'sheet_name': '精加工',
            'expected': '19000101',
            'description': '2019年12月 精加工 - 应该返回 19000101'
        },
        # Test case 10: year=2020, month=03, sheet_name='喷漆装配' -> should return '19000101'
        {
            'file_name': '202003.xls',
            'sheet_name': '喷漆装配',
            'expected': '19000101',
            'description': '2020年3月 喷漆装配 - 应该返回 19000101'
        },
        # Test case 11: year=2020, month=04, sheet_name='喷漆装配' -> should return '20200401'
        {
            'file_name': '202004_1.xlsx',
            'sheet_name': '喷漆装配',
            'expected': '20200401',
            'description': '2020年4月 喷漆装配 - 应该返回 20200401'
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"  文件名: {test_case['file_name']}")
        print(f"  工作表名: {test_case['sheet_name']}")
        print(f"  期望结果: {test_case['expected']}")
        
        try:
            result = calculate_effected_from(test_case['file_name'], test_case['sheet_name'])
            print(f"  实际结果: {result}")
            
            if result == test_case['expected']:
                print("  ✅ 测试通过")
                passed += 1
            else:
                print(f"  ❌ 测试失败 - 期望: {test_case['expected']}, 实际: {result}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ 测试失败 - 异常: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果总结:")
    print(f"  总测试用例: {len(test_cases)}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print("=" * 60)
    
    # Display category_mapping for reference
    print("\n当前 category_mapping 配置:")
    for sheet_name, date_mapping in category_mapping.items():
        print(f"  {sheet_name}: {list(date_mapping.keys())}")
    
    return failed == 0


def test_edge_cases():
    """
    Test edge cases and error handling
    """
    print("\n" + "=" * 60)
    print("Testing edge cases and error handling")
    print("=" * 60)
    
    edge_cases = [
        # Invalid filename format
        {
            'file_name': 'invalid.xls',
            'sheet_name': '绕嵌排',
            'should_fail': True,
            'description': '无效文件名格式'
        },
        # Invalid sheet name
        {
            'file_name': '202005.xls',
            'sheet_name': '不存在的部门',
            'should_fail': True,
            'description': '不存在的工作表名'
        },
        # Empty filename
        {
            'file_name': '',
            'sheet_name': '绕嵌排',
            'should_fail': True,
            'description': '空文件名'
        },
        # None filename
        {
            'file_name': None,
            'sheet_name': '绕嵌排',
            'should_fail': True,
            'description': 'None文件名'
        },
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n边界测试用例 {i}: {test_case['description']}")
        print(f"  文件名: {test_case['file_name']}")
        print(f"  工作表名: {test_case['sheet_name']}")
        
        try:
            result = calculate_effected_from(test_case['file_name'], test_case['sheet_name'])
            if test_case['should_fail']:
                print(f"  ❌ 测试失败 - 期望异常但返回了结果: {result}")
            else:
                print(f"  ✅ 测试通过 - 返回结果: {result}")
                
        except Exception as e:
            if test_case['should_fail']:
                print(f"  ✅ 测试通过 - 正确抛出异常: {e}")
            else:
                print(f"  ❌ 测试失败 - 意外异常: {e}")


if __name__ == "__main__":
    # Run main tests
    success = test_calculate_effected_from()
    
    # Run edge case tests
    test_edge_cases()
    
    if success:
        print("\n🎉 所有主要测试用例通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试用例失败，请检查实现。")
        sys.exit(1)
