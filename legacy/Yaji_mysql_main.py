import time

import pymysql
from yaji_obsidian import thread_safe_print, rpapageshadow
import requests
import json
import re
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
def create_main_table_mysql():
    """
    在MySQL中创建邮件表
    """
    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 创建邮件表
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS yaji_main (
                   id INT PRIMARY KEY,
                    rel_company_id INT,
                    booking_key VARCHAR(255),
                    cds_booking_no VARCHAR(255),
                    ffc_no VARCHAR(255) NULL,
                    submit_channel VARCHAR(50),
                    phone VARCHAR(100),
                    mail_addr VARCHAR(255),
                    status VARCHAR(100),
                    remark VARCHAR(100),
                    creater VARCHAR(100),
                    create_date DATETIME,
                    submit_time DATETIME NULL,
                    submit_status_str varchar(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            cursor.execute(create_table_sql)

        connection.commit()
        thread_safe_print("MySQL核验主表创建成功")

    except Exception as e:
        thread_safe_print(f"MySQL表创建失败: {e}")
    finally:
        connection.close()

def create_main_table_mysql_fba():
    """
    在MySQL中创建邮件表
    """
    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 创建邮件表
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS yaji_main_fba (
                   id INT PRIMARY KEY,
                    rel_company_id INT,
                    booking_key VARCHAR(255),
                    cds_booking_no VARCHAR(255),
                    ffc_no VARCHAR(255) NULL,
                    submit_channel VARCHAR(50),
                    phone VARCHAR(100),
                    mail_addr VARCHAR(255),
                    status VARCHAR(100),
                    remark VARCHAR(100),
                    creater VARCHAR(100),
                    create_date DATETIME,
                    submit_time DATETIME NULL,
                    submit_status_str varchar(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            cursor.execute(create_table_sql)

        connection.commit()
        thread_safe_print("MySQL核验主表创建成功")

    except Exception as e:
        thread_safe_print(f"MySQL表创建失败: {e}")
    finally:
        connection.close()

def parse_and_store_main_data_mysql(data,response_msg):
    """
    解析主数据API返回的数据并存储到MySQL数据库
    """
    if response_msg != '成功':
        thread_safe_print("主数据获取失败或状态不正确")
        return

    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 解析并插入数据
            records = data.get('records', [])
            thread_safe_print(f"准备处理 {len(records)} 条主记录")

            for record in records:
                # 提取字段并处理None值
                insert_sql = '''
                INSERT INTO yaji_main (
                    id, rel_company_id, booking_key, cds_booking_no, ffc_no,
                    submit_channel, phone, mail_addr, status, remark,
                    creater, create_date, submit_time, submit_status_str
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    rel_company_id = VALUES(rel_company_id),
                    booking_key = VALUES(booking_key),
                    cds_booking_no = VALUES(cds_booking_no),
                    ffc_no = VALUES(ffc_no),
                    submit_channel = VALUES(submit_channel),
                    phone = VALUES(phone),
                    mail_addr = VALUES(mail_addr),
                    status = VALUES(status),
                    remark = VALUES(remark),
                    creater = VALUES(creater),
                    create_date = VALUES(create_date),
                    submit_time = VALUES(submit_time),
                    submit_status_str = VALUES(submit_status_str),
                    updated_at = CURRENT_TIMESTAMP
                '''

                values = (
                    record.get('id'),
                    record.get('relCompanyId'),
                    record.get('bookingKey'),
                    record.get('cdsBookingNo'),
                    record.get('ffcNo'),
                    record.get('submitChannelStr'),
                    record.get('phone'),
                    record.get('mailAddr'),
                    record.get('status'),
                    record.get('remark'),
                    record.get('creater'),
                    record.get('createDate'),
                    record.get('submitTime'),
                    record.get('submitStatusStr')
                )

                cursor.execute(insert_sql, values)

        connection.commit()
        thread_safe_print(f"成功存储 {len(records)} 条主记录到MySQL数据库")

    except Exception as e:
        thread_safe_print(f"MySQL主数据存储失败: {e}")
        connection.rollback()
    finally:
        connection.close()


def parse_and_store_main_data_mysql_fba(data,response_msg):
    """
    解析主数据API返回的数据并存储到MySQL数据库
    """
    if response_msg != '成功':
        thread_safe_print("主数据获取失败或状态不正确")
        return

    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 解析并插入数据
            records = data.get('records', [])
            thread_safe_print(f"准备处理 {len(records)} 条主记录")

            for record in records:
                # 提取字段并处理None值
                insert_sql = '''
                INSERT INTO yaji_main_fba (
                    id, rel_company_id, booking_key, cds_booking_no, ffc_no,
                    submit_channel, phone, mail_addr, status, remark,
                    creater, create_date, submit_time, submit_status_str
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    rel_company_id = VALUES(rel_company_id),
                    booking_key = VALUES(booking_key),
                    cds_booking_no = VALUES(cds_booking_no),
                    ffc_no = VALUES(ffc_no),
                    submit_channel = VALUES(submit_channel),
                    phone = VALUES(phone),
                    mail_addr = VALUES(mail_addr),
                    status = VALUES(status),
                    remark = VALUES(remark),
                    creater = VALUES(creater),
                    create_date = VALUES(create_date),
                    submit_time = VALUES(submit_time),
                    submit_status_str = VALUES(submit_status_str),
                    updated_at = CURRENT_TIMESTAMP
                '''

                values = (
                    record.get('id'),
                    record.get('relCompanyId'),
                    record.get('bookingKey'),
                    record.get('cdsBookingNo'),
                    record.get('ffcNo'),
                    record.get('submitChannelStr'),
                    record.get('phone'),
                    record.get('mailAddr'),
                    record.get('status'),
                    record.get('remark'),
                    record.get('creater'),
                    record.get('createDate'),
                    record.get('submitTime'),
                    record.get('submitStatusStr')
                )

                cursor.execute(insert_sql, values)

        connection.commit()
        thread_safe_print(f"成功存储 {len(records)} 条主记录到MySQL数据库")

    except Exception as e:
        thread_safe_print(f"MySQL主数据存储失败: {e}")
        connection.rollback()
    finally:
        connection.close()

# 修改 fetch_detailed_list_data 函数以支持MySQL数据存储
def fetch_detailed_list_data(headers):
    """
    获取详细列表数据的函数  https://www.yagikoifish.com/vms/fbaMail/v/getList4Page?subjectKeys=&status=&pageNo=1&pageSize=20
    """
    url = "https://www.yagikoifish.com/vms/fbaApply/v/getList4Page"
    payload = {
        "pageNo": 1,
        "pageSize": 100000,
        "cdsBookingNo": "FBE"
    }

    try:
        response = requests.post(url, params=payload, headers=headers, timeout=50)
        thejson = json.loads(response.text)
        response_msg = thejson.get('msg')
        response_status = thejson.get('status')
        data = thejson.get('data')

        thread_safe_print(f"API响应消息: {response_msg}")
        thread_safe_print(f"API响应状态: {response_status}")
        # data = json.loads(response.text)

        if data:
            parse_and_store_main_data_mysql(data,response_msg)
            total_records = data.get('total')
            current_page = data.get('current')
            page_size = data.get('size')
            total_pages = data.get('pages')

            thread_safe_print(f"总记录数: {total_records}")
            thread_safe_print(f"当前页: {current_page}/{total_pages}")
            thread_safe_print(f"本页记录数: {page_size}")

            records = data.get('records', [])
            thread_safe_print(f"\n解析到 {len(records)} 条记录:")

            # 收集所有需要查询邮件的记录ID
            records_to_process = []
            for record in records:
                id = record.get('id')
                relCompanyId = record.get('relCompanyId')
                bookingKey = record.get('bookingKey')
                booking_no = record.get('cdsBookingNo')
                ffcNo = record.get('ffcNo')
                submit_channel = record.get('submitChannelStr')
                phone = record.get('phone')
                mail_addr = record.get('mailAddr')
                status = record.get('status')
                remark = record.get('remark')
                creater = record.get('creater')
                create_date = record.get('createDate')
                submitTime = record.get('submitTime')
                submit_status = record.get('submitStatusStr')
                #
                thread_safe_print(f"cds BK号: {booking_no},"
                                  f"进仓编号: {bookingKey},"
                                  f"状态: {submit_status},"
                                  f"创建人: {creater},"
                                  f"创建时间: {create_date},"
                                  f"提交时间: {submitTime},"
                                  f"ID: {id},"
                                  f"公司关联ID：{relCompanyId},"
                                  f"状态代码: {status}"
                                  f"手机号: {phone},"
                                  f"邮箱: {mail_addr},"
                                  f"备注: {remark},"
                                  f"提交渠道: {submit_channel},"
                                  f"FFC编号: {ffcNo}"
                                  )
    except Exception as e:
        thread_safe_print(f"获取详细列表数据失败: {e}")
        return None




# 修改 fetch_detailed_list_data_fba 函数以支持MySQL数据存储
def fetch_detailed_list_data_fba(headers):
    """
    获取详细列表数据的函数  https://www.yagikoifish.com/vms/fbaMail/v/getList4Page?subjectKeys=&status=&pageNo=1&pageSize=20
    """
    url = "https://www.yagikoifish.com/vms/fbaApply/v/getList4Page"
    payload = {
        "pageNo": 1,
        "pageSize": 100000,
        "cdsBookingNo": "FBA"
    }

    try:
        response = requests.post(url, params=payload, headers=headers, timeout=50)
        thejson = json.loads(response.text)
        response_msg = thejson.get('msg')
        response_status = thejson.get('status')
        data = thejson.get('data')

        thread_safe_print(f"API响应消息: {response_msg}")
        thread_safe_print(f"API响应状态: {response_status}")
        # data = json.loads(response.text)

        if data:
            parse_and_store_main_data_mysql_fba(data,response_msg)
            total_records = data.get('total')
            current_page = data.get('current')
            page_size = data.get('size')
            total_pages = data.get('pages')

            thread_safe_print(f"总记录数: {total_records}")
            thread_safe_print(f"当前页: {current_page}/{total_pages}")
            thread_safe_print(f"本页记录数: {page_size}")

            records = data.get('records', [])
            thread_safe_print(f"\n解析到 {len(records)} 条记录:")

            # 收集所有需要查询邮件的记录ID
            records_to_process = []
            for record in records:
                id = record.get('id')
                relCompanyId = record.get('relCompanyId')
                bookingKey = record.get('bookingKey')
                booking_no = record.get('cdsBookingNo')
                ffcNo = record.get('ffcNo')
                submit_channel = record.get('submitChannelStr')
                phone = record.get('phone')
                mail_addr = record.get('mailAddr')
                status = record.get('status')
                remark = record.get('remark')
                creater = record.get('creater')
                create_date = record.get('createDate')
                submitTime = record.get('submitTime')
                submit_status = record.get('submitStatusStr')
                #
                thread_safe_print(f"cds BK号: {booking_no},"
                                  f"进仓编号: {bookingKey},"
                                  f"状态: {submit_status},"
                                  f"创建人: {creater},"
                                  f"创建时间: {create_date},"
                                  f"提交时间: {submitTime},"
                                  f"ID: {id},"
                                  f"公司关联ID：{relCompanyId},"
                                  f"状态代码: {status}"
                                  f"手机号: {phone},"
                                  f"邮箱: {mail_addr},"
                                  f"备注: {remark},"
                                  f"提交渠道: {submit_channel},"
                                  f"FFC编号: {ffcNo}"
                                  )
    except Exception as e:
        thread_safe_print(f"获取详细列表数据失败: {e}")
        return None

# 在主函数中调用


def saika():
    # 首先创建主要信息表
    create_main_table_mysql()
    page, cookie_str = rpapageshadow()
    headers = {
        "authorization": cookie_str
    }

    # 获取所有数据（分页处理）
    page_no = 1
    page_size = 2000  # 调整为合适的页面大小
    total_pages = 1

    while page_no <= total_pages:
        thread_safe_print(f"正在获取第 {page_no} 页数据...")
        data = fetch_detailed_list_data(
            headers=headers
        )

        if data and data.get('data'):
            total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)

def saika_fba():
    # 首先创建主要信息表
    create_main_table_mysql_fba()
    page, cookie_str = rpapageshadow()
    headers = {
        "authorization": cookie_str
    }

    # 获取所有数据（分页处理）
    page_no = 1
    page_size = 2000  # 调整为合适的页面大小
    total_pages = 1

    while page_no <= total_pages:
        thread_safe_print(f"正在获取第 {page_no} 页数据...")
        data = fetch_detailed_list_data_fba(
            headers=headers
        )

        if data and data.get('data'):
            total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)



if __name__ == '__main__':

    # 首先创建主要信息表
    create_main_table_mysql()
    create_main_table_mysql_fba()
    page, cookie_str = rpapageshadow()
    headers = {
        "authorization": cookie_str
    }

    # 获取所有数据（分页处理）
    page_no = 1
    page_size = 2000  # 调整为合适的页面大小
    total_pages = 1

    while page_no <= total_pages:
        thread_safe_print(f"正在获取第 {page_no} 页数据...")
        data = fetch_detailed_list_data(
            headers=headers
        )

        if data and data.get('data'):
            total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)



