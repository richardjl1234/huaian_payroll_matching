#!/usr/bin/env python3
"""
Batch Matching Program
Process payroll records in batch mode to match with quota data
"""

import sys
import os
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from query_quota_table import query_quota_table
from payroll_generator import payroll_records_gen
from match import filter_quota_data, NODECISION
from model_mapper import load_model_mapping, model_mapper
from config import calculate_effected_from, COLUMN_WIDTHS


def get_model_category(model_dict, record, field_name):
    """
    使用 model_mapper 获取指定字段的模型类别
    
    Args:
        model_dict: 型号映射字典
        record: 工资记录
        field_name: 字段名
        
    Returns:
        dict: model_mapper 的结果
    """
    if field_name not in record:
        return None
    
    value = record[field_name]
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    
    try:
        return model_mapper(model_dict, str(value))
    except Exception as e:
        print(f"    ⚠ {field_name} 映射失败: {e}")
        return None


def format_model_result(result):
    """格式化 model_mapper 结果为字符串"""
    if result is None:
        return "无"
    return f"型号:{result['key_value_pair'][0]} -> 类别:{result['key_value_pair'][1]} (相似度:{result['similarity_ratio']:.2%})"


def get_best_model_category(model_results):
    """
    从多个 model_mapper 结果中选择相似度最高的
    
    Args:
        model_results: 包含多个结果的字典
        
    Returns:
        tuple: (best_category, best_similarity, source_field)
    """
    best_category = None
    best_similarity = 0
    source_field = None
    
    for field, result in model_results.items():
        if result and result.get('key_value_pair'):
            category = result['key_value_pair'][1]
            similarity = result['similarity_ratio']
            if similarity > best_similarity:
                best_similarity = similarity
                best_category = category
                source_field = field
    
    return best_category, best_similarity, source_field


def calculate_string_similarity(str1, str2):
    """计算两个字符串的相似度"""
    if not str1 or not str2:
        return 0
    return SequenceMatcher(None, str(str1), str(str2)).ratio()


def filter_quota_data_with_code(quota_data, payroll_record, file_name):
    """
    Filter quota data based on payroll record information (包含代码获取)
    
    Args:
        quota_data (list): List of quota data dictionaries
        payroll_record (dict): Payroll record from generator
        file_name (str): The filename being processed
        
    Returns:
        tuple: (filter1_count, filter2_count, filtered_data)
    """
    # Get sheet name from payroll record
    sheet_name = payroll_record['sheet名']
    
    # Calculate effected_from
    effected_from = calculate_effected_from(file_name, sheet_name)
    
    # Import category_mapping here
    from config import category_mapping
    
    # Get valid categories
    if sheet_name in category_mapping and effected_from in category_mapping[sheet_name]:
        valid_categories = category_mapping[sheet_name][effected_from]
    else:
        valid_categories = []
    
    # Filter 1: match category
    filter1_data = []
    for item in quota_data:
        if (item.get('类别1') in valid_categories and 
            item.get('effected_from') == effected_from):
            filter1_data.append(item)
    
    filter1_count = len(filter1_data)
    
    # Filter 2: match quota value AND retrieve 代码
    filter2_data = []
    for item in filter1_data:
        if item.get('定额') == payroll_record['定额']:
            filter2_data.append(item)
    
    filter2_count = len(filter2_data)
    
    return filter1_count, filter2_count, filter2_data


def format_quota_record_with_code(item):
    """格式化定额记录为字符串(包含代码): 代码 | 类别1 | 类别2 | 加工工序 | 型号 | 定额"""
    code = item.get('代码', '')
    # 移除代码前导零
    if isinstance(code, str):
        code = code.lstrip('0') or '0'
    elif isinstance(code, (int, float)):
        code = int(code) if code == int(code) else code
    return f"{code} | {item.get('类别1', '')} | {item.get('类别2', '')} | {item.get('加工工序', '')} | {item.get('型号', '')} | {item.get('定额', '')}"


def one_file_batch_matching(yyyymm, verbose=True):
    """
    Process payroll records for a single month and return summary.
    
    Args:
        yyyymm (str): The year-month string (e.g., '202005')
        verbose (bool): If True, print detailed progress messages (default: True)
        
    Returns:
        dict: Summary information with keys:
            - processed_count: Total processed records
            - success_count: Successfully matched records
            - skip_count: Skipped records
            - error_count: Error records
    """
    def log(msg):
        if verbose:
            print(msg)
    
    log("=" * 60)
    log(f"批量匹配程序 - Batch Matching Program: {yyyymm}")
    log("=" * 60)
    
    file_prefix = yyyymm
    log(f"正在处理文件前缀为 '{file_prefix}' 的记录")
    log("")
    
    # Step 0: Load model mapping
    log("正在加载型号映射数据...")
    try:
        model_dict = load_model_mapping("../sqlite_2_mysql/定额型号类别编码_updated.xlsx", "型号映射")
    except FileNotFoundError:
        log("错误: 找不到型号映射文件，../sqlite_2_mysql/定额型号类别编码_updated.xlsx")
        model_dict = {}
    except Exception as e:
        log(f"错误: 加载型号映射失败: {e}")
        model_dict = {}
    log(f"加载了 {len(model_dict)} 条型号映射记录")
    log("")
    
    # Step 1: Load quota data
    log("正在查询定额数据...")
    quota_data = query_quota_table()
    log(f"获取到 {len(quota_data)} 条定额记录")
    log("")
    
    # Step 2: Create payroll records generator with file prefix
    log(f"正在获取工资记录 (文件前缀: {file_prefix})...")
    file_name = f"{file_prefix}.xls"
    generator = payroll_records_gen(file_prefix)
    
    # Results storage for Excel output
    results = []
    
    # Counter for processed records
    processed_count = 0
    
    # Detailed counters for summary
    # Case 1: Filter3 has result (successful match)
    case1_filter3_matched = 0
    # Case 2: Filter2 has result, Filter3 has no result
    case2_filter2_only = 0
    # Case 3: Filter2 has no result
    case3_filter2_none = 0
    # Case 4: Skipped (quota = 0)
    case4_skipped = 0
    # Case 5: Error
    case5_error = 0
    
    try:
        # Process all records
        while True:
            payroll_record = next(generator)
            processed_count += 1
            
            log(f"\n处理记录 #{processed_count}:")
            log(f"  文件名: {payroll_record['文件名']}")
            log(f"  工作表名: {payroll_record['sheet名']}")
            log(f"  职员: {payroll_record['职员全名']}")
            log(f"  定额: {payroll_record['定额']}")
            
            # Initialize result record
            result_record = {
                '工作表名': payroll_record.get('sheet名', ''),
                '职员全名': payroll_record.get('职员全名', ''),
                '定额': payroll_record.get('定额', ''),
                '计件数量': payroll_record.get('计件数量', ''),
                '系数': payroll_record.get('系数', ''),
                '型号': payroll_record.get('型号', ''),
                '工序': payroll_record.get('工序', ''),
                '工序全名': payroll_record.get('工序全名', ''),
                '最终匹配结果': '',
                '过滤条件2结果': '',
                '过滤条件3结果': '',
                '型号映射结果': '',
                '最佳匹配类别': '',
                '最佳匹配来源': '',
                '最佳匹配相似度': 0,
                '最终状态': '',
                '过滤条件1命中数': 0,
                'row_color': ''  # For Excel coloring
            }
            
            # Check if quota is 0 or empty - mark as gray
            is_zero_quota = payroll_record['定额'] == 0 or payroll_record['定额'] == '' or payroll_record['定额'] is None
            
            # Skip if quota is 0
            if is_zero_quota:
                log("  → 定额为0，跳过匹配")
                result_record['最终状态'] = '跳过(定额为0)'
                result_record['row_color'] = 'gray'
                case4_skipped += 1
                results.append(result_record)
                continue
            
            # Get file name from payroll record
            file_name = payroll_record['文件名']
            
            # Step 4: Use model_mapper on multiple fields
            log("  步骤4: 使用 model_mapper 分析记录...")
            model_results = {}
            
            # 4.1 Check 型号
            model_result = get_model_category(model_dict, payroll_record, '型号')
            if model_result:
                model_results['型号'] = model_result
                log(f"    型号: {format_model_result(model_result)}")
            
            # 4.2 Check 工序全名
            model_result = get_model_category(model_dict, payroll_record, '工序全名')
            if model_result:
                model_results['工序全名'] = model_result
                log(f"    工序全名: {format_model_result(model_result)}")
            
            # 4.3 Check 工序
            model_result = get_model_category(model_dict, payroll_record, '工序')
            if model_result:
                model_results['工序'] = model_result
                log(f"    工序: {format_model_result(model_result)}")
            
            # Format all model results with \n separator
            all_model_results_str = "\n".join([f"{k}: {format_model_result(v)}" for k, v in model_results.items()])
            result_record['型号映射结果'] = all_model_results_str
            
            # Get best model category
            best_category, best_similarity, source_field = get_best_model_category(model_results)
            result_record['最佳匹配类别'] = best_category if best_category else ''
            result_record['最佳匹配来源'] = source_field if source_field else ''
            result_record['最佳匹配相似度'] = best_similarity
            
            if best_category:
                log(f"  最佳匹配类别: {best_category} (来源:{source_field}, 相似度:{best_similarity:.2%})")
            
            try:
                # Step 3: Filter quota data (Filter 1 + Filter 2)
                filter1_count, filter2_count, filter2_data = filter_quota_data_with_code(
                    quota_data, payroll_record, file_name
                )
                
                result_record['过滤条件1命中数'] = filter1_count
                
                # Format filter 2 results with the new format (包含代码)
                if filter2_data:
                    filter2_str_parts = [format_quota_record_with_code(item) for item in filter2_data]
                    result_record['过滤条件2结果'] = "\n".join(filter2_str_parts)
                    log(f"  过滤结果: 条件1={filter1_count}, 条件1+2={filter2_count}")
                    for i, part in enumerate(filter2_str_parts[:3], 1):
                        log(f"    结果{i}: {part}")
                    if len(filter2_str_parts) > 3:
                        log(f"    ... 共 {len(filter2_str_parts)} 条")
                else:
                    result_record['过滤条件2结果'] = '无'
                    log(f"  过滤结果: 条件1={filter1_count}, 条件1+2={filter2_count}")
                
                # Step 6: Filter 3 - Match model category
                log("  步骤6: 执行 Filter 3 (模型类别匹配)...")
                filter3_results = []
                
                if filter2_data and best_category:
                    salary_model = payroll_record.get('型号', '')
                    
                    for quota_item in filter2_data:
                        quota_model = quota_item.get('型号', '')
                        if quota_model:
                            try:
                                quota_model_result = model_mapper(model_dict, str(quota_model))
                                quota_category = quota_model_result['key_value_pair'][1]
                                category_similarity = quota_model_result['similarity_ratio']
                                
                                # Check if categories match
                                if quota_category == best_category:
                                    filter3_results.append({
                                        'quota_item': quota_item,
                                        'quota_model': quota_model,
                                        'quota_category': quota_category,
                                        'category_similarity': category_similarity
                                    })
                            except Exception as e:
                                print(f"    ⚠ 定额记录 {quota_item.get('代码', '')} 映射失败: {e}")
                
                # Format filter 3 results with the same format as filter 2 (包含代码)
                if filter3_results:
                    filter3_str_parts = [format_quota_record_with_code(r['quota_item']) for r in filter3_results]
                    result_record['过滤条件3结果'] = "\n".join(filter3_str_parts)
                    log(f"  Filter 3 命中 {len(filter3_results)} 条记录")
                    for i, part in enumerate(filter3_str_parts[:5], 1):
                        log(f"    结果{i}: {part}")
                else:
                    result_record['过滤条件3结果'] = '无匹配'
                    log("  → Filter 3 无匹配记录")
                
                # Final result logic
                final_result = ''
                if len(filter3_results) == 1:
                    # If only one record in filter 3, use it directly
                    final_result = format_quota_record_with_code(filter3_results[0]['quota_item'])
                    log(f"  最终结果 (单条记录): {final_result}")
                elif len(filter3_results) > 1:
                    # If more than 2 records in filter 3, use similarity check
                    log(f"  Filter 3 有 {len(filter3_results)} 条记录，进行型号相似度筛选...")
                    for r in filter3_results:
                        model_sim = calculate_string_similarity(salary_model, r['quota_model'])
                        r['model_similarity'] = model_sim
                        log(f"    型号相似度: {r['quota_model']} vs {salary_model} = {model_sim:.2%}")
                    
                    # Get the one with highest similarity
                    best_match = max(filter3_results, key=lambda x: x['model_similarity'])
                    final_result = format_quota_record_with_code(best_match['quota_item'])
                    log(f"  最终结果 (最高相似度): {final_result}")
                # If no results in filter 3, leave final result as blank
                
                result_record['最终匹配结果'] = final_result
                
                # Set final status and row color
                if final_result:
                    # Case 1: Filter3 has result (successful match)
                    result_record['最终状态'] = '匹配成功'
                    result_record['row_color'] = 'green'
                    case1_filter3_matched += 1
                elif filter2_count > 0:
                    # Case 2: Filter2 has records, but Filter3 has no result
                    result_record['最终状态'] = 'Filter3无匹配'
                    result_record['row_color'] = 'yellow'
                    case2_filter2_only += 1
                else:
                    # Case 3: Filter2 has no records
                    result_record['最终状态'] = '无匹配记录'
                    result_record['row_color'] = 'pink'
                    case3_filter2_none += 1
                
            except NODECISION as e:
                log(f"  → 决策失败: {e}")
                result_record['最终状态'] = f'决策失败: {str(e)[:50]}'
                result_record['row_color'] = 'pink'
                case5_error += 1
            except Exception as e:
                log(f"  → 处理错误: {e}")
                result_record['最终状态'] = f'错误: {str(e)[:50]}'
                result_record['row_color'] = 'pink'
                case5_error += 1
            
            results.append(result_record)
        
    except StopIteration:
        log(f"\n所有记录已处理完毕 (共 {processed_count} 条记录)")
    
    # Step 7: Output results to Excel
    log("\n" + "=" * 60)
    log("正在生成 Excel 输出文件...")
    
    if results:
        # Replace None values with empty strings for all records
        for record in results:
            for key, value in record.items():
                if value is None:
                    record[key] = ''
        
        df = pd.DataFrame(results)
        
        # Generate output filename
        output_file = f"batch_matching_result_{file_prefix}.xlsx"
        
        # Adjust column width for better display
        from openpyxl import Workbook
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils.dataframe import dataframe_to_rows
        
        # Define colors
        green_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")  # Light green
        yellow_fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")  # Light yellow
        pink_fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")  # Pink
        gray_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")  # Light gray
        
        # Define border style (solid line, weight 0.25)
        thin_border = Border(
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000'),
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000')
        )
        
        # Define left alignment
        left_alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Reorder columns to match desired order
            column_order = [
                '工作表名', '职员全名', '定额', '计件数量', '系数', '型号', '工序', '工序全名',
                '最终匹配结果', '过滤条件2结果', '过滤条件3结果', '型号映射结果',
                '最佳匹配类别', '最佳匹配来源', '最佳匹配相似度', '最终状态', '过滤条件1命中数'
            ]
            # Only include columns that exist in df
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            df.to_excel(writer, index=False, sheet_name='匹配结果')
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['匹配结果']
            
            # Freeze the first header row
            worksheet.freeze_panes = 'A2'
            
            # Add grid lines
            worksheet.sheet_view.showGridlines = True
            
            # Set column widths and apply styles to all cells (including header)
            for column_idx, col_name in enumerate(df.columns, 1):
                column_letter = chr(64 + column_idx)  # Convert to letter (1=A, 2=B, etc.)
                # Get column width from configuration (use 10 as default)
                col_width = COLUMN_WIDTHS.get(col_name, 10)
                worksheet.column_dimensions[column_letter].width = col_width
            
            # Apply left alignment, border, and text wrapping to all cells
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.alignment = left_alignment
                    cell.border = thin_border
            
            # Apply row colors to data rows (starting from row 2)
            for row_idx, row_data in enumerate(results, 2):
                row_color = row_data.get('row_color', '')
                fill = None
                if row_color == 'green':
                    fill = green_fill
                elif row_color == 'yellow':
                    fill = yellow_fill
                elif row_color == 'pink':
                    fill = pink_fill
                elif row_color == 'gray':
                    fill = gray_fill
                
                for cell in worksheet[row_idx]:
                    if fill:
                        cell.fill = fill
        
        log(f"结果已保存到: {output_file}")
        log(f"共导出 {len(results)} 条记录")
    else:
        log("没有记录需要导出")
    
    # Return detailed summary
    return {
        'processed_count': processed_count,
        'case1_filter3_matched': case1_filter3_matched,
        'case2_filter2_only': case2_filter2_only,
        'case3_filter2_none': case3_filter2_none,
        'case4_skipped': case4_skipped,
        'case5_error': case5_error,
        # Legacy fields for backward compatibility
        # Success rate = case1 / (case1 + case2 + case3), ignoring case4
        'success_count': case1_filter3_matched,
        'skip_count': case2_filter2_only + case3_filter2_none,
        'error_count': case5_error
    }


def main():
    """
    Main function - supports both command line and programmatic calls
    """
    # Check command line arguments
    if len(sys.argv) < 2:
        print("用法: python batch_matching.py <文件前缀>")
        print("例如: python batch_matching.py 202005")
        return
    
    yyyymm = sys.argv[1]
    
    # Determine verbose mode from command line
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    # Call one_file_batch_matching and get the summary
    summary = one_file_batch_matching(yyyymm, verbose=verbose)
    
    # Print detailed summary
    print("\n" + "=" * 60)
    print("处理摘要:")
    print(f"  总处理记录数: {summary['processed_count']}")
    print()
    print("  详细分类:")
    print(f"    情况1-匹配成功(Filter3有结果): {summary['case1_filter3_matched']}")
    print(f"    情况2-Filter2有结果但Filter3无匹配: {summary['case2_filter2_only']}")
    print(f"    情况3-Filter2无结果: {summary['case3_filter2_none']}")
    print(f"    情况4-跳过(定额为0): {summary['case4_skipped']}")
    print(f"    情况5-错误: {summary['case5_error']}")
    print()
    print("  统计汇总:")
    print(f"  成功数(情况1): {summary['success_count']}")
    print(f"  未成功数(情况2+情况3+情况5): {summary['skip_count'] + summary['case5_error']}")
    print(f"  成功率(情况1/(情况1+2+3)): {summary['success_rate_all'] if 'success_rate_all' in summary else 'N/A'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
