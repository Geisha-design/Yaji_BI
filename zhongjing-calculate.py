# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件合并工具
功能：将指定文件夹下的所有Excel文件合并到一个Excel文件中
作者：豆包编程助手
日期：2025-08-25
"""

import os
import pandas as pd
import datetime
import logging
from typing import List, Dict, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("excel_merge.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_excel_files(folder_path: str = '.') -> List[str]:
    """
    获取指定文件夹下所有Excel文件的路径

    Args:
        folder_path: 文件夹路径，默认为当前目录

    Returns:
        Excel文件路径列表
    """
    excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    excel_files = []

    try:
        for file in os.listdir(folder_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in excel_extensions:
                file_path = os.path.join(folder_path, file)
                excel_files.append(file_path)
                logger.info(f"发现Excel文件: {file_path}")

        if not excel_files:
            logger.warning("未找到任何Excel文件")
        else:
            logger.info(f"共找到 {len(excel_files)} 个Excel文件")

        return excel_files

    except Exception as e:
        logger.error(f"获取Excel文件时出错: {str(e)}")
        return []


def read_excel_file(file_path: str) -> List[Tuple[str, pd.DataFrame]]:
    """
    读取Excel文件中的所有工作表

    Args:
        file_path: Excel文件路径

    Returns:
        工作表名称和数据的元组列表
    """
    sheets_data = []

    try:
        excel_file = pd.ExcelFile(file_path)
        logger.info(f"读取文件: {file_path}，包含 {len(excel_file.sheet_names)} 个工作表")

        for sheet_name in excel_file.sheet_names:
            try:
                # 尝试读取数据，跳过可能的标题行
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # 检查是否需要跳过第一行（如果第一行是标题）
                if df.shape[0] > 0 and df.columns.str.contains('Unnamed').any():
                    # 如果有很多Unnamed列，尝试从第一行作为列名
                    df.columns = df.iloc[0]
                    df = df.drop(df.index[0]).reset_index(drop=True)
                    logger.info(f"工作表 '{sheet_name}' 自动调整列名")

                sheets_data.append((sheet_name, df))
                logger.info(f"成功读取工作表 '{sheet_name}'，数据行数: {len(df)}")

            except Exception as e:
                logger.error(f"读取工作表 '{sheet_name}' 时出错: {str(e)}")

        return sheets_data

    except Exception as e:
        logger.error(f"读取文件 {file_path} 时出错: {str(e)}")
        return []


def merge_excel_files(folder_path: str = '.', output_file: str = None) -> Tuple[pd.DataFrame, Dict]:
    """
    合并文件夹下的所有Excel文件

    Args:
        folder_path: 文件夹路径，默认为当前目录
        output_file: 输出文件名，默认为 'merged_excel_当前时间.xlsx'

    Returns:
        合并后的DataFrame和统计信息
    """
    # 获取Excel文件列表
    excel_files = get_excel_files(folder_path)
    if not excel_files:
        return None, {"error": "未找到Excel文件"}

    # 准备输出文件名
    if output_file is None:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"merged_excel_{current_time}.xlsx"

    # 存储所有数据
    all_data = []
    file_stats = {
        "total_files": len(excel_files),
        "total_sheets": 0,
        "total_rows": 0,
        "files_processed": [],
        "files_failed": []
    }

    # 读取并合并所有文件
    for file_path in excel_files:
        file_name = os.path.basename(file_path)
        try:
            sheets_data = read_excel_file(file_path)

            if sheets_data:
                file_rows = 0
                for sheet_name, df in sheets_data:
                    # 添加源文件和工作表信息
                    df['源文件'] = file_name
                    df['源工作表'] = sheet_name

                    all_data.append(df)
                    file_rows += len(df)
                    file_stats["total_sheets"] += 1
                    file_stats["total_rows"] += len(df)

                file_stats["files_processed"].append({
                    "file": file_name,
                    "sheets": len(sheets_data),
                    "rows": file_rows
                })
                logger.info(f"成功处理文件: {file_name}，总行数: {file_rows}")

            else:
                file_stats["files_failed"].append({
                    "file": file_name,
                    "reason": "未读取到有效数据"
                })
                logger.warning(f"文件 {file_name} 未读取到有效数据")

        except Exception as e:
            file_stats["files_failed"].append({
                "file": file_name,
                "reason": str(e)
            })
            logger.error(f"处理文件 {file_name} 时出错: {str(e)}")

    # 合并所有数据
    if all_data:
        try:
            merged_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"成功合并所有数据，总行数: {len(merged_df)}")

            # 保存合并后的数据
            merged_df.to_excel(output_file, index=False)
            logger.info(f"合并后的数据已保存到: {output_file}")

            file_stats["output_file"] = output_file
            file_stats["merged_rows"] = len(merged_df)

            return merged_df, file_stats

        except Exception as e:
            logger.error(f"合并数据时出错: {str(e)}")
            file_stats["error"] = f"合并数据时出错: {str(e)}"
            return None, file_stats
    else:
        logger.warning("没有可合并的数据")
        file_stats["error"] = "没有可合并的数据"
        return None, file_stats


def display_stats(stats: Dict) -> None:
    """
    显示合并统计信息

    Args:
        stats: 统计信息字典
    """
    print("\n" + "=" * 60)
    print("Excel文件合并统计信息")
    print("=" * 60)

    if "error" in stats:
        print(f"错误: {stats['error']}")
        return

    print(f"处理文件总数: {stats['total_files']}")
    print(f"处理工作表总数: {stats['total_sheets']}")
    print(f"处理数据总行数: {stats['total_rows']}")
    print(f"合并后总行数: {stats['merged_rows']}")
    print(f"输出文件名: {stats['output_file']}")

    print("\n成功处理的文件:")
    for file_info in stats["files_processed"]:
        print(f"  - {file_info['file']}: {file_info['sheets']}个工作表, {file_info['rows']}行数据")

    if stats["files_failed"]:
        print("\n处理失败的文件:")
        for file_info in stats["files_failed"]:
            print(f"  - {file_info['file']}: {file_info['reason']}")

    print("=" * 60)


def main():
    """
    主函数
    """
    print("Excel文件合并工具")
    print("-" * 40)

    # 获取当前目录
    current_dir = os.getcwd()+'/saika'
    print(f"将合并 '{current_dir}' 目录下的所有Excel文件")

    # 执行合并
    merged_df, stats = merge_excel_files(current_dir)

    # 显示统计信息
    display_stats(stats)

    if merged_df is not None:
        print(f"\n合并成功！数据已保存到: {stats['output_file']}")
    else:
        print("\n合并失败，请查看日志了解详情。")


if __name__ == "__main__":
    main()
