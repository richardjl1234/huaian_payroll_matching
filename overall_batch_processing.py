#!/usr/bin/env python3
"""
Overall Batch Processing Program
Process all payroll records across multiple months and generate combined HTML report
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_PATH
from one_file_batch_matching import one_file_batch_matching


def get_all_yyyymm_from_db():
    """
    Get all unique YYYYMM values from the SQLite database.
    
    Returns:
        list: List of unique YYYYMM strings sorted in ascending order
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Extract YYYYMM from the 文件名 column
        # The filename format is like '202005.xls', so we take first 6 characters
        sql_query = """
        SELECT DISTINCT SUBSTR(文件名, 1, 6) as yyyymm 
        FROM payroll_details 
        ORDER BY yyyymm
        """
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        yyyymm_list = [result[0] for result in results]
        
        conn.close()
        
        return yyyymm_list
    
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return []


def main():
    """
    Main function for overall batch processing
    """
    print("=" * 60)
    print("整体批量处理程序 - Overall Batch Processing Program")
    print("=" * 60)
    print()
    
    # Step 1: Get all YYYYMM from database
    print("正在从数据库获取所有月份...")
    yyyymm_list = get_all_yyyymm_from_db()
    
    if not yyyymm_list:
        print("错误: 无法从数据库获取月份数据")
        return
    
    print(f"找到 {len(yyyymm_list)} 个月份: {yyyymm_list}")
    print()
    
    # Step 2: Process each month and collect results
    all_summaries = []
    
    for yyyymm in yyyymm_list:
        print(f"\n{'=' * 60}")
        print(f"正在处理月份: {yyyymm}")
        print('=' * 60)
        
        # Call one_file_batch_matching and get the summary
        # Use verbose=False to reduce output for batch processing
        summary = one_file_batch_matching(yyyymm, verbose=False)
        all_summaries.append({
            '月份': yyyymm,
            **summary
        })
    
    # Step 3: Create summary DataFrame
    print(f"\n{'=' * 60}")
    print("处理完成 - 生成汇总报告")
    print('=' * 60)
    
    # Create DataFrame from summaries
    df_summary = pd.DataFrame(all_summaries)
    
    # Display summary
    print("\n处理汇总:")
    print(df_summary.to_string(index=False))
    
    # Step 4: Output to HTML file
    output_file = f"overall_processing_result.html"
    
    # Generate HTML with styling
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工资匹配处理汇总报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .summary-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-table th, .summary-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .summary-table th {{
            background-color: #4CAF50;
            color: white;
        }}
        .summary-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .summary-table tr:hover {{
            background-color: #f1f1f1;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .total-row {{
            font-weight: bold;
            background-color: #e8f5e9 !important;
        }}
    </style>
</head>
<body>
    <h1>工资匹配处理汇总报告</h1>
    <p class="timestamp">生成时间: 详见文件名</p>
    
    <table class="summary-table">
        <thead>
            <tr>
                <th>月份</th>
                <th>总处理记录数</th>
                <th>情况1-匹配成功</th>
                <th>情况2-Filter2有结果<br/>Filter3无匹配</th>
                <th>情况3-Filter2<br/>无结果</th>
                <th>情况4-跳过</th>
                <th>情况5-错误</th>
                <th>成功数<br/>(情况1)</th>
                <th>未成功数<br/>(情况2+3+5)</th>
                <th>成功率</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Add data rows
    for summary in all_summaries:
        total = summary['processed_count']
        case1 = summary.get('case1_filter3_matched', 0)
        case2 = summary.get('case2_filter2_only', 0)
        case3 = summary.get('case3_filter2_none', 0)
        case4 = summary.get('case4_skipped', 0)
        case5 = summary.get('case5_error', 0)
        success = case1 + case4  # case1 + case4
        not_success = case2 + case3 + case5  # case2 + case3 + case5
        success_rate = (success / total * 100) if total > 0 else 0
        
        html_content += f"""
            <tr>
                <td>{summary['月份']}</td>
                <td>{total}</td>
                <td>{case1}</td>
                <td>{case2}</td>
                <td>{case3}</td>
                <td>{case4}</td>
                <td>{case5}</td>
                <td>{success}</td>
                <td>{not_success}</td>
                <td>{success_rate:.2f}%</td>
            </tr>
"""
    
    # Add total row
    total_all = sum(s['processed_count'] for s in all_summaries)
    case1_all = sum(s.get('case1_filter3_matched', 0) for s in all_summaries)
    case2_all = sum(s.get('case2_filter2_only', 0) for s in all_summaries)
    case3_all = sum(s.get('case3_filter2_none', 0) for s in all_summaries)
    case4_all = sum(s.get('case4_skipped', 0) for s in all_summaries)
    case5_all = sum(s.get('case5_error', 0) for s in all_summaries)
    
    # Success rate = case1 / (case1 + case2 + case3), ignoring case4 (skipped)
    eligible_count = case1_all + case2_all + case3_all
    success_all = case1_all  # Only case1 is considered success
    not_success_all = case2_all + case3_all + case5_all
    success_rate_all = (case1_all / eligible_count * 100) if eligible_count > 0 else 0
    
    html_content += f"""
            <tr class="total-row">
                <td>合计</td>
                <td>{total_all}</td>
                <td>{case1_all}</td>
                <td>{case2_all}</td>
                <td>{case3_all}</td>
                <td>{case4_all}</td>
                <td>{case5_all}</td>
                <td>{success_all}</td>
                <td>{not_success_all}</td>
                <td>{success_rate_all:.2f}%</td>
            </tr>
"""
    
    html_content += """
        </tbody>
    </table>
</body>
</html>
"""
    
    # Generate bar chart using matplotlib and embed in HTML
    import io
    import base64
    import os
    from PIL import Image
    
    chart_html = ''
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # Try to use a Chinese font
        # First try common Chinese font names, then fallback to system fonts
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # WenQuanYi Micro Hei
            '/usr/share/fonts/truetype/arphic/ukai.ttc',       # AR PL UKai
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',  # Noto Sans CJK
            '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',  # Noto Serif CJK
        ]
        
        # Try to find and use a Chinese font
        font_prop = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font_prop = fm.FontProperties(fname=font_path)
                print(f"Using Chinese font: {font_path}")
                break
        
        if font_prop is None:
            # Fallback to system font manager
            chinese_fonts = [f.name for f in fm.fontManager.ttflist if 'Noto' in f.name or 'WenQuanYi' in f.name or 'UKai' in f.name]
            if chinese_fonts:
                plt.rcParams['font.sans-serif'] = chinese_fonts
        
        plt.rcParams['axes.unicode_minus'] = False
        
        # Sort summaries by total records in descending order
        sorted_summaries = sorted(all_summaries, key=lambda x: x['processed_count'], reverse=True)
        
        # Create 2 separate figures and combine them
        # Chart 1: 总体处理结果分类统计 (smaller, on top)
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        
        case_labels = ['情况1\n匹配成功', '情况2\nFilter2有结果\nFilter3无匹配', 
                 '情况3\nFilter2无结果', '情况4\n跳过', '情况5\n错误']
        case_values = [case1_all, case2_all, case3_all, case4_all, case5_all]
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6', '#9b59b6']
        
        bars = ax1.bar(case_labels, case_values, color=colors, alpha=0.8)
        ax1.set_xlabel('分类', fontsize=12, fontproperties=font_prop)
        ax1.set_ylabel('记录数', fontsize=12, fontproperties=font_prop)
        ax1.set_title('总体处理结果分类统计', fontsize=14, fontproperties=font_prop)
        ax1.grid(axis='y', alpha=0.3)
        
        # Fix Chinese font for xticklabels
        if font_prop:
            ax1.set_xticklabels(case_labels, fontproperties=font_prop)
        
        # Add value labels on bars
        for bar, value in zip(bars, case_values):
            height = bar.get_height()
            ax1.annotate(f'{value}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10)
        
        # Add summary text to chart 1
        summary_text = f'成功率: {success_rate_all:.1f}% (情况1/(情况1+2+3) = {case1_all}/{eligible_count})'
        fig1.text(0.5, 0.02, summary_text, ha='center', fontsize=12, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontproperties=font_prop)
        
        plt.tight_layout(rect=(0, 0.08, 1, 1))
        
        # Save chart 1 to BytesIO
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format='png', dpi=150, bbox_inches='tight')
        buf1.seek(0)
        plt.close(fig1)
        
        # Chart 2: 各月份处理统计 (larger, on bottom)
        num_months = len(sorted_summaries)
        fig_height = max(8, num_months * 0.3)
        fig2, ax2 = plt.subplots(figsize=(14, fig_height))
        
        months = [s['月份'] for s in sorted_summaries]
        totals = [s['processed_count'] for s in sorted_summaries]
        successes = [s.get('success_count', 0) for s in sorted_summaries]
        
        y = range(len(months))
        height = 0.35
        
        # Horizontal bar chart: x=record count, y=month
        ax2.barh([i - height/2 for i in y], totals, height, label='总记录数', color='#3498db', alpha=0.8)
        ax2.barh([i + height/2 for i in y], successes, height, label='成功数', color='#2ecc71', alpha=0.8)
        ax2.set_xlabel('记录数', fontsize=12, fontproperties=font_prop)
        ax2.set_ylabel('月份', fontsize=12, fontproperties=font_prop)
        ax2.set_title('各月份处理统计', fontsize=14, fontproperties=font_prop)
        ax2.set_yticks(y)
        ax2.set_yticklabels(months, fontsize=8)
        ax2.legend(prop=font_prop if font_prop else fm.FontProperties())
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()  # First month at top
        
        plt.tight_layout()
        
        # Save chart 2 to BytesIO
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format='png', dpi=150, bbox_inches='tight')
        buf2.seek(0)
        plt.close(fig2)
        
        # Combine both charts vertically
        from PIL import Image
        img1 = Image.open(buf1)
        img2 = Image.open(buf2)
        
        # Calculate combined size
        combined_width = max(img1.width, img2.width)
        combined_height = img1.height + img2.height
        
        combined = Image.new('RGB', (combined_width, combined_height), (255, 255, 255))
        combined.paste(img1, (0, 0))
        combined.paste(img2, (0, img1.height))
        
        # Save combined chart to BytesIO
        buf_combined = io.BytesIO()
        combined.save(buf_combined, format='PNG', quality=95)
        buf_combined.seek(0)
        
        img_base64 = base64.b64encode(buf_combined.read()).decode('utf-8')
        buf_combined.close()
        buf1.close()
        buf2.close()
        
        # Add chart to HTML
        chart_html = f'<img src="data:image/png;base64,{img_base64}" alt="处理统计图表" style="max-width:100%; height:auto; margin:20px 0;">' 
        
    except ImportError:
        print("\n注意: matplotlib未安装，跳过图表生成")
        chart_html = '<p>图表生成失败: matplotlib未安装</p>'
    except Exception as e:
        print(f"\n图表生成错误: {e}")
        chart_html = f'<p>图表生成失败: {str(e)}</p>'
    
    # Insert chart into HTML before </body>
    html_content = html_content.replace('</body>', f'{chart_html}</body>')
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n汇总报告已保存到: {output_file}")
    print(f"共处理 {len(yyyymm_list)} 个月份")
    print(f"总记录数: {total_all}")
    print(f"成功数(情况1): {success_all}")
    print(f"未成功数(情况2+3+5): {not_success_all}")
    print(f"  - 情况2-Filter2有结果但Filter3无匹配: {case2_all}")
    print(f"  - 情况3-Filter2无结果: {case3_all}")
    print(f"  - 情况5-错误: {case5_all}")
    print(f"  - 跳过(情况4): {case4_all}")
    print(f"成功率(情况1/(情况1+2+3)): {success_rate_all:.2f}%")


if __name__ == "__main__":
    main()
