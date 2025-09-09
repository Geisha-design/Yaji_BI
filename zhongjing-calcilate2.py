#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件合并工具 - 支持ISF NO去重
功能：合并指定文件夹下的所有Excel文件，并基于ISF NO字段去重
作者：豆包编程助手
日期：2025-08-25
"""

import pandas as pd
import os
import datetime
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("merge_excel.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def process_excel_file(file_path):
    """
    处理单个Excel文件

    Args:
        file_path (str): Excel文件路径

    Returns:
        pandas.DataFrame: 处理后的数据
    """
    try:
        # 读取Excel文件，跳过第一行标题，使用第二行作为表头
        df = pd.read_excel(file_path, skiprows=1)

        # 检查是否包含必要的列
        required_columns = ['ISF NO']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logging.warning(f"文件 {file_path} 缺少必要的列: {missing_columns}")
            return None

        # 添加源文件信息列
        df['源文件'] = os.path.basename(file_path)

        logging.info(f"成功读取文件: {file_path}, 行数: {len(df)}")
        return df

    except Exception as e:
        logging.error(f"处理文件 {file_path} 时出错: {str(e)}")
        return None


def merge_excel_files(input_dir=None, output_file=None, keep_last=True):
    """
    合并Excel文件并去重

    Args:
        input_dir (str): 输入文件夹路径，默认为当前目录
        output_file (str): 输出文件路径，默认为"合并后的ISF报表数据.xlsx"
        keep_last (bool): 去重时是否保留最后一条记录，默认为True

    Returns:
        tuple: (合并后的数据, 统计信息)
    """
    # 设置默认值
    if input_dir is None:
        input_dir = os.getcwd()+"/saika"

    if output_file is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"合并后的ISF报表数据_{timestamp}.xlsx"

    logging.info(f"开始合并Excel文件，输入目录: {input_dir}")

    # 获取所有Excel文件
    excel_extensions = ['.xlsx', '.xls']
    excel_files = [
        os.path.join(input_dir, file)
        for file in os.listdir(input_dir)
        if os.path.splitext(file)[1].lower() in excel_extensions
    ]

    if not excel_files:
        logging.warning("未找到任何Excel文件")
        return None, None

    logging.info(f"找到 {len(excel_files)} 个Excel文件")

    # 读取并合并所有文件
    all_data = []
    for file in excel_files:
        df = process_excel_file(file)
        if df is not None:
            all_data.append(df)

    if not all_data:
        logging.error("没有成功读取任何数据")
        return None, None

    # 合并所有数据
    combined_df = pd.concat(all_data, ignore_index=True)
    original_count = len(combined_df)
    logging.info(f"合并前总记录数: {original_count}")

    # 检查并处理重复的ISF NO
    isf_duplicates = combined_df[combined_df.duplicated(subset=['ISF NO'], keep=False)]
    duplicate_count = len(isf_duplicates) - combined_df['ISF NO'].nunique()

    if duplicate_count > 0:
        logging.info(f"发现 {duplicate_count} 条重复的ISF NO记录")

        # 显示重复的ISF NO示例
        duplicate_isfs = isf_duplicates['ISF NO'].unique()[:10]  # 只显示前10个
        logging.info(f"重复的ISF NO示例: {', '.join(duplicate_isfs)}")

        # 去重 - 保留最后一条记录
        if keep_last:
            combined_df = combined_df.drop_duplicates(subset=['ISF NO'], keep='last')
            logging.info("去重策略: 保留最后一条记录")
        else:
            combined_df = combined_df.drop_duplicates(subset=['ISF NO'], keep='first')
            logging.info("去重策略: 保留第一条记录")

    # 重置索引
    combined_df = combined_df.reset_index(drop=True)
    final_count = len(combined_df)
    removed_count = original_count - final_count

    logging.info(f"去重后记录数: {final_count}")
    logging.info(f"移除的重复记录数: {removed_count}")

    # 保存合并后的数据
    try:
        combined_df.to_excel(output_file, index=False)
        logging.info(f"合并后的数据已保存到: {output_file}")
    except Exception as e:
        logging.error(f"保存文件时出错: {str(e)}")
        return None, None

    # 生成统计信息
    stats = {
        'input_files': len(excel_files),
        'original_records': original_count,
        'final_records': final_count,
        'removed_duplicates': removed_count,
        'unique_isf_count': combined_df['ISF NO'].nunique(),
        'output_file': output_file,
        'processing_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return combined_df, stats


def generate_merge_report(stats, output_dir=None):
    """
    生成合并报告

    Args:
        stats (dict): 统计信息
        output_dir (str): 输出目录，默认为当前目录

    Returns:
        str: 报告文件路径
    """
    if output_dir is None:
        output_dir = os.getcwd()

    if stats is None:
        logging.error("无法生成报告：统计信息为空")
        return None

    report_file = os.path.join(output_dir, "合并报告.txt")

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("          ISF报表数据合并报告          \n")
            f.write("=" * 60 + "\n")
            f.write(f"处理时间: {stats['processing_time']}\n")
            f.write(f"输入文件数量: {stats['input_files']} 个\n")
            f.write(f"合并前总记录数: {stats['original_records']} 条\n")
            f.write(f"去重后记录数: {stats['final_records']} 条\n")
            f.write(f"移除的重复记录数: {stats['removed_duplicates']} 条\n")
            f.write(f"唯一ISF NO数量: {stats['unique_isf_count']} 个\n")
            f.write(f"输出文件路径: {stats['output_file']}\n")
            f.write("=" * 60 + "\n")
            f.write("去重策略: 保留最后一条重复记录\n")
            f.write("=" * 60 + "\n")

        logging.info(f"合并报告已生成: {report_file}")
        return report_file

    except Exception as e:
        logging.error(f"生成报告时出错: {str(e)}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("          Excel文件合并工具 - 支持ISF NO去重          ")
    print("=" * 60)
    print("功能：合并指定文件夹下的所有Excel文件，并基于ISF NO字段去重")
    print("=" * 60)

    # 合并Excel文件
    combined_df, stats = merge_excel_files()

    if stats:
        # 生成报告
        report_file = generate_merge_report(stats)

        # 显示结果摘要
        print("\n合并完成！")
        print(f"输入文件数量: {stats['input_files']} 个")
        print(f"合并前总记录数: {stats['original_records']} 条")
        print(f"去重后记录数: {stats['final_records']} 条")
        print(f"移除的重复记录数: {stats['removed_duplicates']} 条")
        print(f"输出文件: {stats['output_file']}")
        if report_file:
            print(f"合并报告: {report_file}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
