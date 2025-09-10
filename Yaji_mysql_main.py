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
# AL0
# 亚马逊正则工具

def alo_capture(text):

    # text = "Re: Re: 【报关问题】 AL0-SVXPKX7XE4TQE 报关资料（紧急!!!）"

    # 正则表达式匹配以 AL0 开头的字符串，通常格式为 AL0-后面跟大写字母和数字
    match = re.search(r'\bAL0-[A-Z0-9]+\b', text)

    if match:
        print("提取到的编号是:", match.group())
        return match.group()
    else:
        print("未找到匹配项")
        return "无al0信息"




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
def create_email_table_mysql():
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
            CREATE TABLE IF NOT EXISTS main (
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
    accepter VARCHAR(100) NULL,
    accept_time DATETIME NULL,
    auditer VARCHAR(100) NULL,
    audit_time DATETIME NULL,
    audit_exception TEXT NULL,
    attachment VARCHAR(100) NULL,
    submit_channel_str VARCHAR(100),
    status_str VARCHAR(100),
    submit_status_str varchar(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            cursor.execute(create_table_sql)

        connection.commit()
        thread_safe_print("MySQL核验主表创建成功")

    except Exception as e:
        thread_safe_print(f"MySQL表创建失败: {e}")
    finally:
        connection.close()



def parse_and_store_email_data_mysql(data):
    """
    解析邮件API返回的数据并存储到MySQL数据库
    """
    if not data or data.get('status') != 'success':
        thread_safe_print("邮件数据获取失败或状态不正确")
        return

    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 解析并插入数据
            records = data.get('data', {}).get('records', [])
            thread_safe_print(f"准备处理 {len(records)} 条邮件记录")

            for record in records:
                # 提取字段并处理None值
                insert_sql = '''
                INSERT INTO yaji_email_records_1 (
                    id, message_id, from_addresses, content, content_text,
                    received_time, status, mail_addr, rel_fba_apply_id, subject, status_str,alo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                ON DUPLICATE KEY UPDATE
                    message_id = VALUES(message_id),
                    from_addresses = VALUES(from_addresses),
                    content = VALUES(content),
                    content_text = VALUES(content_text),
                    received_time = VALUES(received_time),
                    status = VALUES(status),
                    mail_addr = VALUES(mail_addr),
                    rel_fba_apply_id = VALUES(rel_fba_apply_id),
                    subject = VALUES(subject),
                    status_str = VALUES(status_str),
                    alo = VALUES(alo),
                    updated_at = CURRENT_TIMESTAMP
                '''

                values = (
                    record.get('id'),
                    record.get('messageId'),
                    record.get('fromAddresses'),
                    record.get('content'),
                    record.get('contentText'),
                    record.get('receivedTime'),
                    record.get('status'),
                    record.get('mailAddr'),
                    record.get('relFbaApplyId'),
                    record.get('subject'),
                    record.get('statusStr'),
                    alo_capture(record.get('subject'))
                )

                cursor.execute(insert_sql, values)

        connection.commit()
        thread_safe_print(f"成功存储 {len(records)} 条邮件记录到MySQL数据库")

    except Exception as e:
        thread_safe_print(f"MySQL数据存储失败: {e}")
        connection.rollback()
    finally:
        connection.close()


# 修改 fetch_detailed_list_data 函数以支持MySQL数据存储
def fetch_detailed_list_data(headers, submit_status=0, booking_keys="", cds_booking_no="", page_no=1, page_size=20):
    """
    获取详细列表数据的函数  https://www.yagikoifish.com/vms/fbaMail/v/getList4Page?subjectKeys=&status=&pageNo=1&pageSize=20
    """
    url = "https://www.yagikoifish.com/vms/fbaMail/v/getList4Page"
    params = {
        "status": submit_status,
        "pageNo": page_no,
        "pageSize": page_size
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=50)
        data = json.loads(response.text)

        # 解析并存储数据到MySQL
        parse_and_store_email_data_mysql(data)

        thread_safe_print(f"详细列表接口响应: {data.get('msg')}, 状态: {data.get('status')}")

        # 打印记录详情
        records = data.get('data', {}).get('records', [])
        thread_safe_print(f"准备处理 {len(records)} 条记录")

        for record in records:
            thread_safe_print(
                f"ID: {record.get('id')}, "
                f"主题: {record.get('subject')}, "
                f"发件人: {record.get('fromAddresses')}, "
                f"状态: {record.get('statusStr')}, "
                f"alo: {alo_capture(record.get('subject'))}, "
                f"接收时间: {record.get('receivedTime')}"
            )

        return data
    except Exception as e:
        thread_safe_print(f"获取详细列表数据失败: {e}")
        return None

    #
    # headers = {
    #     "authorization": cookieb.get('vue_admin_template_token').replace('%20', ' ')}
    # payload = {
    #     "pageNo": 1,
    #     "pageSize": 100000,
    #     "cdsBookingNo": "FBE"
    # }
    # # searchBookingDetailsByFilter   指令5的数据状态接口
    # response = requests.post("https://www.yagikoifish.com/vms/fbaApply/v/getList4Page", params=payload,
    #                          headers=headers)
    # # thejson = json.loads(response.text)
    # # status = thejson.get('status')
    # # data = thejson.get('data')
    # # print( status)
    # # print( data)
    #
    # thejson = json.loads(response.text)
    # response_msg = thejson.get('msg')
    # response_status = thejson.get('status')
    # data = thejson.get('data')
    #
    # thread_safe_print(f"API响应消息: {response_msg}")
    # thread_safe_print(f"API响应状态: {response_status}")
    #
    # # 用于生成HTML报表的数据
    # report_data = []
    #
    # if data:
    #     total_records = data.get('total')
    #     current_page = data.get('current')
    #     page_size = data.get('size')
    #     total_pages = data.get('pages')
    #
    #     thread_safe_print(f"总记录数: {total_records}")
    #     thread_safe_print(f"当前页: {current_page}/{total_pages}")
    #     thread_safe_print(f"本页记录数: {page_size}")
    #
    #     records = data.get('records', [])
    #     thread_safe_print(f"\n解析到 {len(records)} 条记录:")
    #
    #     # 收集所有需要查询邮件的记录ID
    #     records_to_process = []
    #     for record in records:
    #         booking_no = record.get('cdsBookingNo')
    #         status_code = record.get('status')
    #         submit_status = record.get('submitStatusStr')
    #         creater = record.get('creater')
    #         create_date = record.get('createDate')
    #         id = record.get('id')
    #












# 在主函数中调用
if __name__ == '__main__':
    # 首先创建表
    create_email_table_mysql()

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
            headers=headers,
            page_no=page_no,
            page_size=page_size
        )

        if data and data.get('data'):
            total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)
