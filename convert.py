import pandas as pd
import sys
import os


def excel_to_sql(excel_file_path, sql_file_path, table_name='your_table_name', id_col='宝贝ID', url_col='宝贝链接'):
    """
    将Excel文件转换为SQL插入语句

    参数:
    excel_file_path (str): Excel文件路径
    sql_file_path (str): SQL文件输出路径
    table_name (str): SQL表名
    id_col (str): 宝贝ID列名
    url_col (str): 宝贝链接列名
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(excel_file_path):
            print(f"错误: 文件 '{excel_file_path}' 不存在")
            return False

        # 读取Excel文件
        print(f"正在读取Excel文件: {excel_file_path}")
        df = pd.read_excel(excel_file_path, dtype={id_col: str, url_col: str})

        # 检查列是否存在
        if id_col not in df.columns or url_col not in df.columns:
            missing_cols = [col for col in [id_col, url_col] if col not in df.columns]
            print(f"错误: Excel文件中缺少列: {', '.join(missing_cols)}")
            print(f"可用列: {', '.join(df.columns)}")
            return False

        # 过滤掉宝贝ID或宝贝链接为空的行
        original_count = len(df)
        df = df.dropna(subset=[id_col, url_col])
        filtered_count = len(df)
        if filtered_count < original_count:
            print(f"已过滤掉 {original_count - filtered_count} 行空数据")

        if df.empty:
            print("错误: 过滤后没有有效数据")
            return False

        # 生成SQL插入语句
        print(f"正在生成SQL插入语句，共 {len(df)} 条记录")
        sql_statements = []

        # 添加创建表语句
        create_table = f"""-- 创建表 {table_name}
CREATE TABLE IF NOT EXISTS {table_name} (
    babyId VARCHAR(255) PRIMARY KEY,
    contact_url TEXT NOT NULL
);
"""
        sql_statements.append(create_table)

        # 添加插入数据语句
        for index, row in df.iterrows():
            baby_id = row[id_col]
            contact_url = row[url_col].replace("'", "''")  # 转义单引号
            sql = f"INSERT INTO {table_name} (babyId, contact_url) VALUES ('{baby_id}', '{contact_url}');"
            sql_statements.append(sql)

        # 写入SQL文件
        with open(sql_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_statements))

        print(f"SQL文件已生成: {sql_file_path}")
        print(f"表名: {table_name}")
        print(f"总记录数: {len(df)}")
        return True

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False


if __name__ == "__main__":

    # 11
    # 默认参数。辉航 童助
    EXCEL_FILE = './1688采购助手-全店导出-浙江初品文具有限公司.xlsx'
    SQL_FILE = './output39.sql'
    TABLE_NAME = 'product_info'

    print("===== Excel 转 SQL 工具 =====")

    # 获取用户输入（如果提供）
    if len(sys.argv) > 1:
        EXCEL_FILE = sys.argv[1]
        print(f"使用指定的Excel文件: {EXCEL_FILE}")

    if len(sys.argv) > 2:
        SQL_FILE = sys.argv[2]
        print(f"使用指定的SQL输出文件: {SQL_FILE}")

    if len(sys.argv) > 3:
        TABLE_NAME = sys.argv[3]
        print(f"使用指定的表名: {TABLE_NAME}")

    # 执行转换
    success = excel_to_sql(EXCEL_FILE, SQL_FILE, TABLE_NAME)

    if success:
        print("\n转换成功！")
        print(f"请查看生成的SQL文件: {SQL_FILE}")
    else:
        print("\n转换失败，请检查错误信息。")