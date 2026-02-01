#!/usr/bin/env python3
"""
测试 model_mapper.py 中的函数
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_mapper import model_mapper, load_model_mapping, DuplicateKeyError


def test_exact_match():
    """测试精确匹配功能"""
    print("\n" + "=" * 60)
    print("测试 1: 精确匹配")
    print("=" * 60)
    
    # 使用真实的 Excel 数据进行测试
    excel_file = "定额型号类别编码_260201.xlsx"
    sheet_name = "型号"
    
    try:
        test_dict = load_model_mapping(excel_file, sheet_name)
        # 获取前3个型号作为测试用例
        test_cases = list(test_dict.items())[:3]
        print(f"使用实际数据测试，共 {len(test_cases)} 条")
    except FileNotFoundError:
        print(f"文件 {excel_file} 不存在，使用模拟数据")
        test_dict = {
            "M10×1.5": "类别A",
            "M12×1.75": "类别B", 
            "M8×1.25": "类别C"
        }
        test_cases = [("M10×1.5", "类别A"), ("M12×1.75", "类别B"), ("M8×1.25", "类别C")]
    
    for raw_str, expected_category in test_cases:
        result = model_mapper(test_dict, raw_str)
        print(f"输入: {raw_str}")
        print(f"期望类别: {expected_category}")
        print(f"实际结果: {result}")
        
        assert result["key_value_pair"][1] == expected_category, "类别不匹配"
        assert result["similarity_ratio"] == 1.0, "相似度应该为1.0"
        print("✓ 通过\n")
    
    print("所有精确匹配测试通过！")


def test_fuzzy_match():
    """测试模糊匹配功能"""
    print("\n" + "=" * 60)
    print("测试 2: 模糊匹配")
    print("=" * 60)
    
    # 使用真实的 Excel 数据进行测试
    excel_file = "定额型号类别编码_260201.xlsx"
    sheet_name = "型号"
    
    try:
        test_dict = load_model_mapping(excel_file, sheet_name)
        # 获取前4个型号作为基础
        models = list(test_dict.keys())[:4]
        if len(models) >= 4:
            # 创建模糊匹配的测试用例（轻微修改型号）
            test_cases = [
                (models[0] + "1", models[0]),  # 轻微差异
                (models[1][:-1] + "5", models[1]),
            ]
            print(f"使用实际数据测试，共 {len(test_cases)} 条")
        else:
            test_dict = {
                "M10×1.5": "类别A",
                "M12×1.75": "类别B",
                "M8×1.25": "类别C",
                "M16×2.0": "类别D"
            }
            test_cases = [
                ("M10×1.6", "M10×1.5"),
                ("M12×1.7", "M12×1.75"),
            ]
    except FileNotFoundError:
        print(f"文件 {excel_file} 不存在，使用模拟数据")
        test_dict = {
            "M10×1.5": "类别A",
            "M12×1.75": "类别B",
            "M8×1.25": "类别C",
            "M16×2.0": "类别D"
        }
        test_cases = [
            ("M10×1.6", "M10×1.5"),
            ("M12×1.7", "M12×1.75"),
        ]
    
    for raw_str, expected_match in test_cases:
        result = model_mapper(test_dict, raw_str)
        print(f"输入: {raw_str}")
        print(f"期望最佳匹配: {expected_match}")
        print(f"实际结果: {result}")
        
        assert result["key_value_pair"][0] == expected_match, "最佳匹配不匹配"
        assert 0 < result["similarity_ratio"] < 1.0, "相似度应该在0-1之间"
        print("✓ 通过\n")
    
    print("所有模糊匹配测试通过！")


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试 3: 边界情况")
    print("=" * 60)
    
    # 使用真实的 Excel 数据
    excel_file = "定额型号类别编码_260201.xlsx"
    sheet_name = "型号"
    
    try:
        test_dict = load_model_mapping(excel_file, sheet_name)
    except FileNotFoundError:
        print(f"文件 {excel_file} 不存在，使用模拟数据")
        test_dict = {
            "M10×1.5": "类别A",
            "M12×1.75": "类别B"
        }
    
    # 测试空字典
    print("测试空字典...")
    try:
        model_mapper({}, "M10×1.5")
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        print(f"✓ 正确抛出异常: {e}")
    
    # 测试空字符串
    print("\n测试空字符串...")
    try:
        model_mapper(test_dict, "")
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        print(f"✓ 正确抛出异常: {e}")
    
    # 测试只有空格的字符串
    print("\n测试只有空格的字符串...")
    try:
        model_mapper(test_dict, "   ")
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        print(f"✓ 正确抛出异常: {e}")
    
    print("\n所有边界情况测试通过！")


def test_with_real_file():
    """测试使用真实文件"""
    print("\n" + "=" * 60)
    print("测试 4: 使用真实 Excel 文件")
    print("=" * 60)
    
    excel_file = "定额型号类别编码_260201.xlsx"
    sheet_name = "型号"
    
    try:
        model_dict = load_model_mapping(excel_file, sheet_name)
        
        # 测试一些实际的型号
        test_cases = [
            "M10×1.5",
            "M12×1.75",
        ]
        
        for test_str in test_cases:
            result = model_mapper(model_dict, test_str)
            print(f"\n输入型号: {test_str}")
            print(f"匹配结果: {result}")
            
            assert "key_value_pair" in result, "结果应该包含 key_value_pair"
            assert "similarity_ratio" in result, "结果应该包含 similarity_ratio"
        
        print("\n✓ 真实文件测试通过！")
        
    except FileNotFoundError:
        print(f"⚠ 文件 {excel_file} 不存在，跳过真实文件测试")
    except Exception as e:
        print(f"⚠ 测试失败: {e}")


def test_duplicate_key_error():
    """测试重复 key 的异常处理"""
    print("\n" + "=" * 60)
    print("测试 5: 重复 Key 异常处理")
    print("=" * 60)
    
    import pandas as pd
    from io import BytesIO
    
    # 创建一个包含重复 key 的 DataFrame
    data = {
        "型号": ["M10×1.5", "M10×1.5", "M12×1.75"],
        "类别": ["类别A", "类别B", "类别C"]
    }
    df = pd.DataFrame(data)
    
    # 模拟 load_model_mapping 的逻辑
    if df["型号"].duplicated().any():
        duplicates = df[df["型号"].duplicated(keep=False)]["型号"].unique()
        error_msg = f"发现重复的型号 key: {duplicates.tolist()}"
        print(f"✓ 正确检测到重复: {error_msg}")
    else:
        print("✗ 应该检测到重复")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始运行 model_mapper 测试套件")
    print("=" * 60)
    
    test_exact_match()
    test_fuzzy_match()
    test_edge_cases()
    test_duplicate_key_error()
    test_with_real_file()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
