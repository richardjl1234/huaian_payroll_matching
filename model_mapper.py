#!/usr/bin/env python3
"""
型号映射器 - Model Mapper
从 Excel 文件读取型号和类别映射关系，支持精确匹配和模糊匹配
"""

import pandas as pd
from difflib import SequenceMatcher


class DuplicateKeyError(Exception):
    """Exception raised when duplicate keys are found in the dataframe"""
    pass


def load_model_mapping(excel_file: str, sheet_name: str = "型号") -> dict:
    """
    从 Excel 文件加载型号映射数据
    
    Args:
        excel_file: Excel 文件路径
        sheet_name: 工作表名称，默认为 "类别2"
        
    Returns:
        dict: 型号到类别的映射字典
        
    Raises:
        DuplicateKeyError: 当存在重复的型号 key 时抛出
    """
    # 读取 Excel 文件
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print(f"已读取 {len(df)} 条记录")
    print(f"列名: {df.columns.tolist()}")
    
    # 检查是否有重复的型号 key
    first_column = df.columns[0]  # 第一列，应该是 型号
    second_column = df.columns[1]  # 第二列，应该是 类别
    
    if df[first_column].duplicated().any():
        duplicates = df[df[first_column].duplicated(keep=False)][first_column].unique()
        raise DuplicateKeyError(
            f"发现重复的型号 key: {duplicates.tolist()}"
        )
    
    # 转换为字典
    model_dict = dict(zip(df[first_column], df[second_column]))
    
    print(f"成功创建映射字典，共 {len(model_dict)} 条记录")
    
    return model_dict


def model_mapper(model_dict: dict, raw_model_str: str) -> dict:
    """
    将原始型号字符串映射到类别
    
    Args:
        model_dict: 型号到类别的映射字典
        raw_model_str: 原始型号字符串
        
    Returns:
        dict: 包含 key_value_pair 和 similarity_ratio 的字典
              {
                  "key_value_pair": (型号, model_category),
                  "similarity_ratio": 相似度 (0-1)
              }
        
    Raises:
        ValueError: 当 model_dict 为空时抛出
    """
    if not model_dict:
        raise ValueError("model_dict 不能为空")
    
    if not raw_model_str or not raw_model_str.strip():
        raise ValueError("raw_model_str 不能为空")
    
    # Step 1: 精确匹配
    exact_match = model_dict.get(raw_model_str)
    if exact_match is not None:
        return {
            "key_value_pair": (raw_model_str, exact_match),
            "similarity_ratio": 1.0
        }
    
    # Step 2: 模糊匹配 - 找到最相似的型号
    best_match_key = None
    best_similarity = 0
    
    for model_key in model_dict.keys():
        # 使用 SequenceMatcher 计算相似度
        similarity = SequenceMatcher(None, raw_model_str, model_key).ratio()
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_key = model_key
    
    # 如果没有找到任何匹配（理论上不太可能发生，因为至少会有一些相似度）
    if best_match_key is None:
        return {
            "key_value_pair": (None, None),
            "similarity_ratio": 0.0
        }
    
    return {
        "key_value_pair": (best_match_key, model_dict[best_match_key]),
        "similarity_ratio": round(best_similarity, 4)
    }


def main():
    """主函数 - 演示如何使用 model_mapper"""
    excel_file = "../sqlite_2_mysql/定额型号类别编码_updated.xlsx"
    sheet_name = "型号映射"
    
    print("=" * 60)
    print("型号映射器 - Model Mapper")
    print("=" * 60)
    
    # Step 1: 加载映射数据
    print(f"\n正在读取 Excel 文件: {excel_file}")
    print(f"工作表: {sheet_name}")
    
    try:
        model_dict = load_model_mapping(excel_file, sheet_name)
        print(model_dict)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {excel_file}")
        return
    except DuplicateKeyError as e:
        print(f"错误: {e}")
        return
    
    # Step 2: 测试 model_mapper 函数
    print("\n" + "-" * 60)
    print("测试 model_mapper 函数")
    print("-" * 60)
    
    # 从 Excel 文件中获取实际的型号数据作为测试用例
    # 选择前5个型号作为精确匹配测试
    actual_models = list(model_dict.keys())[:5]
    
    print(f"\n使用 Excel 文件中的实际型号数据进行测试")
    print(f"可用型号示例: {actual_models}")
    
    # 测试用例：使用实际数据
    test_cases = actual_models + ["这是一个不存在的型号"]
    
    for test_str in test_cases:
        print(f"\n输入型号: {test_str}")
        result = model_mapper(model_dict, test_str)
        print(f"  匹配结果: {result['key_value_pair']}")
        print(f"  相似度: {result['similarity_ratio']:.2%}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
