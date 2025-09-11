import pymysql
from datetime import datetime, date
from yaji_obsidian import thread_safe_print
# MySQL数据库配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # 替换为你的MySQL用户名
    'password': 'qyzh12260315',  # 替换为你的MySQL密码
    'database': 'yaji_db',  # 替换为你的数据库名
    'charset': 'utf8mb4'
}

def get_mysql_connection():
    """
    获取MySQL数据库连接
    """
    try:
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            charset=MYSQL_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except Exception as e:
        thread_safe_print(f"MySQL数据库连接失败: {e}")
        return None


def query_alo_and_booking_mapping():
    """
    查询yaji_email_records中当天记录的alo字段，
    并在yaji_main中查找对应的cds_booking_no
    """
    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天的记录，获取alo字段
            select_email_sql = '''
            SELECT DISTINCT alo 
            FROM yaji_email_records 
            WHERE DATE(received_time) = %s 
            AND alo IS NOT NULL 
            AND alo != '无al0信息'
            '''

            cursor.execute(select_email_sql, (today,))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print("今天没有找到任何邮件记录")
                return

            thread_safe_print(f"找到 {len(email_records)} 个不同的ALO编号")

            # 提取所有alo值
            alo_list = [record['alo'] for record in email_records]

            # 在yaji_main中查找对应的cds_booking_no
            # 使用IN查询提高效率
            placeholders = ','.join(['%s'] * len(alo_list))
            select_main_sql = f'''
            SELECT id, booking_key, cds_booking_no, ffc_no, submit_status_str, create_date
            FROM yaji_main 
            WHERE booking_key IN ({placeholders})
            '''

            cursor.execute(select_main_sql, alo_list)
            main_records = cursor.fetchall()

            thread_safe_print(f"找到 {len(main_records)} 条匹配的主要记录:")

            # 输出结果
            for record in main_records:
                thread_safe_print(
                    f"ID: {record['id']}, "
                    f"Booking Key: {record['booking_key']}, "
                    f"CDS Booking No: {record['cds_booking_no']}, "
                    f"FFC No: {record['ffc_no']}, "
                    f"Status: {record['submit_status_str']}, "
                    f"Create Date: {record['create_date']}"
                )

            return main_records

    except Exception as e:
        thread_safe_print(f"查询ALO和Booking映射关系失败: {e}")
    finally:
        connection.close()


# 在主函数中调用
if __name__ == '__main__':
    query_alo_and_booking_mapping()
