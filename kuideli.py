import pandas as pd
import sys
import os
import glob


def excel_to_sql(excel_file_path, table_name='your_table_name', id_col='宝贝ID', url_col='宝贝链接'):
    """
    将单个Excel文件转换为SQL插入语句列表

    参数:
    excel_file_path (str): Excel文件路径
    table_name (str): SQL表名
    id_col (str): 宝贝ID列名
    url_col (str): 宝贝链接列名

    返回:
    list: SQL插入语句列表
    """
    sql_statements = []

    try:
        # 检查文件是否存在
        if not os.path.exists(excel_file_path):
            print(f"警告: 文件 '{excel_file_path}' 不存在，已跳过")
            return sql_statements

        # 读取Excel文件
        print(f"正在读取Excel文件: {excel_file_path}")
        df = pd.read_excel(excel_file_path, dtype={id_col: str, url_col: str})

        # 检查列是否存在
        if id_col not in df.columns or url_col not in df.columns:
            missing_cols = [col for col in [id_col, url_col] if col not in df.columns]
            print(f"警告: 文件 '{excel_file_path}' 缺少列: {', '.join(missing_cols)}，已跳过")
            print(f"可用列: {', '.join(df.columns)}")
            return sql_statements

        # 过滤掉宝贝ID或宝贝链接为空的行
        original_count = len(df)
        df = df.dropna(subset=[id_col, url_col])
        filtered_count = len(df)
        if filtered_count < original_count:
            print(f"已过滤掉 {original_count - filtered_count} 行空数据")

        if df.empty:
            print(f"警告: 文件 '{excel_file_path}' 过滤后没有有效数据，已跳过")
            return sql_statements

        # 添加插入数据语句
        file_records = 0
        for index, row in df.iterrows():
            baby_id = row[id_col]
            contact_url = row[url_col].replace("'", "''")  # 转义单引号
            sql = f"INSERT INTO {table_name} (babyId, contact_url) VALUES ('{baby_id}', '{contact_url}');"
            sql_statements.append(sql)
            file_records += 1

        print(f"文件 '{excel_file_path}' 已处理，生成 {file_records} 条SQL记录")
        return sql_statements

    except Exception as e:
        print(f"处理文件 '{excel_file_path}' 时发生错误: {str(e)}，已跳过")
        return sql_statements


def process_excel_folder(folder_path, sql_file_path, table_name='your_table_name', id_col='宝贝ID', url_col='宝贝链接'):
    """
    处理文件夹中的所有Excel文件并生成单个SQL文件

    参数:
    folder_path (str): 包含Excel文件的文件夹路径
    sql_file_path (str): SQL文件输出路径
    table_name (str): SQL表名
    id_col (str): 宝贝ID列名
    url_col (str): 宝贝链接列名

    返回:
    bool: 处理是否成功
    """
    try:
        # 检查文件夹是否存在
        if not os.path.isdir(folder_path):
            print(f"错误: 文件夹 '{folder_path}' 不存在")
            return False

        # 获取所有Excel文件
        excel_files = glob.glob(os.path.join(folder_path, "*.xlsx")) + glob.glob(os.path.join(folder_path, "*.xls"))

        if not excel_files:
            print(f"错误: 文件夹 '{folder_path}' 中没有找到Excel文件")
            return False

        print(f"找到 {len(excel_files)} 个Excel文件")

        # 初始化SQL语句列表
        all_sql_statements = []

        # 添加创建表语句（只需要一次）
        create_table = f"""-- 创建表 {table_name}
CREATE TABLE IF NOT EXISTS {table_name} (
    babyId VARCHAR(255) PRIMARY KEY,
    contact_url TEXT NOT NULL
);
"""
        all_sql_statements.append(create_table)

        # 处理每个Excel文件
        total_records = 0
        for excel_file in excel_files:
            file_sql = excel_to_sql(excel_file, table_name, id_col, url_col)
            all_sql_statements.extend(file_sql)
            total_records += len(file_sql)

        if total_records == 0:
            print("错误: 处理完所有文件后没有生成任何SQL记录")
            return False

        # 写入SQL文件
        with open(sql_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_sql_statements))

        print(f"\n===== 处理完成 =====")
        print(f"SQL文件已生成: {sql_file_path}")
        print(f"表名: {table_name}")
        print(f"总文件数: {len(excel_files)}")
        print(f"总记录数: {total_records}")
        return True

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # 默认参数
    FOLDER_PATH = './商品数据0623'  # 包含Excel文件的文件夹
    SQL_FILE = './outputccccc'
    TABLE_NAME = 'product_info'

    print("===== Excel 文件夹转 SQL 工具 =====")

    # 获取用户输入（如果提供）
    if len(sys.argv) > 1:
        FOLDER_PATH = sys.argv[1]
        print(f"使用指定的Excel文件夹: {FOLDER_PATH}")

    if len(sys.argv) > 2:
        SQL_FILE = sys.argv[2]
        print(f"使用指定的SQL输出文件: {SQL_FILE}")

    if len(sys.argv) > 3:
        TABLE_NAME = sys.argv[3]
        print(f"使用指定的表名: {TABLE_NAME}")

    # 执行转换
    success = process_excel_folder(FOLDER_PATH, SQL_FILE, TABLE_NAME)

    if success:
        print("\n转换成功！")
        print(f"请查看生成的SQL文件: {SQL_FILE}")
    else:
        print("\n转换失败，请检查错误信息。")