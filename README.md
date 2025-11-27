# 工资匹配系统 (Payroll Matching System)

## 系统功能概述

### 核心模块

1. **payroll_generator.py** - 工资记录生成器
   - `payroll_records_gen(file_name_prefix)` - 生成器函数，逐个生成工资记录
   - 连接实际数据库，使用SQL模板查询工资详情
   - 格式化显示工资记录

2. **query_quota_table.py** - 定额数据查询器
   - `query_quota_table()` - 查询定额表并返回字典列表
   - 从数据库获取所有定额记录

3. **match.py** - 工资与定额匹配程序
   - 调用定额查询和工资生成器
   - 实现两级过滤逻辑：
     - 过滤条件1：基于类别映射和生效日期
     - 过滤条件2：基于定额值匹配
   - 提供用户交互界面选择操作
   - 显示详细的过滤条件信息
   - 以表格形式展示匹配的定额记录

4. **config.py** - 配置文件
   - 数据库路径配置
   - 类别映射关系定义
   - `calculate_effected_from(file_name, sheet_name)` - 智能计算生效日期
     - 根据文件名提取年月信息
     - 基于类别映射选择最合适的生效日期

5. **test_calculate_effected_from.py** - 测试程序
   - 全面测试 `calculate_effected_from` 函数
   - 包含11个测试用例和边界情况测试

### 数据流程
1. 从工资数据库读取工资记录
2. 从定额数据库读取定额数据
3. 根据类别映射关系进行匹配
4. 显示匹配结果供用户决策

## 主要更新

### 功能增强
- ✅ 实现了完整的 `calculate_effected_from` 函数逻辑
- ✅ 添加了详细的过滤条件显示
- ✅ 改进了定额记录显示格式（使用DataFrame表格）
- ✅ 重构了 `payroll_records_gen` 函数参数
- ✅ 创建了全面的测试程序
- ✅ 添加了批量匹配程序 `batch_matching.py`
- ✅ 实现了 `final_decision` 函数用于自动决策
- ✅ 更新了 `payroll_records_gen` 支持可选文件名参数
- ✅ 清理了未使用的 `format_quota_record` 函数

### 新增模块

6. **batch_matching.py** - 批量匹配程序
   - 非交互式批量处理工资记录
   - 自动跳过定额为0的记录
   - 调用 `final_decision` 函数进行自动决策
   - 提供处理进度跟踪和统计摘要
   - 目前限制处理前100条记录（临时限制）

### 新增功能

- **自动决策机制**: `final_decision` 函数根据过滤结果自动返回匹配代码
- **批量处理模式**: 支持一次性处理所有工资记录，无需用户交互
- **灵活查询**: `payroll_records_gen` 现在支持查询所有记录或按条件过滤
- **错误处理**: 新增 `NODECISION` 异常类处理决策失败情况

### TODO
- [ ] 移除 `batch_matching.py` 中的100条记录限制，支持处理所有记录

### 智能生效日期计算
`calculate_effected_from` 函数现在能够：
- 从文件名中提取年月信息（支持 YYYYMM.xls, YYYYMM_x.xls 等格式）
- 根据类别映射选择最合适的生效日期
- 处理边界情况和错误输入
- 返回最接近但不大于目标日期的生效日期

### 用户界面改进
- 显示详细的过滤条件信息
- 以表格形式展示匹配的定额记录
- 提供更好的用户体验

## 使用方法

```bash
# 运行匹配程序
python match.py 202005

# 运行测试程序
python test_calculate_effected_from.py
```

## 类别映射配置

系统支持以下类别映射：
- 精加工：19000101, 20200401
- 喷漆装配：19000101, 20200401  
- 绕嵌排：19000101, 20200401, 20201201, 20210101, 20211001, 20211201
