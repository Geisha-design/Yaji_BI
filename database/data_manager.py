"""
数据库数据管理
"""
from database.connection import get_mysql_connection
from utils.helpers import thread_safe_print
from config.database_config import MYSQL_CONFIG
import re


def alo_capture(text, text2):
    """
    从文本中提取ALO编号
    """
    # 正则表达式匹配以 AL0 开头的字符串，通常格式为 AL0-后面跟大写字母和数字
    match = re.search(r'\bAL0-[A-Z0-9]+\b', text)

    if match:
        print("提取到的编号是:", match.group())
        return match.group()
    else:
        print("未找到匹配项,二次匹配")
        match = re.search(r'AL0-[A-Z0-9]+', text)
        if match:
            print("二次匹配成功:", match.group())
            return match.group()
        else:
            try:
                result = re.search(r'AL0-[A-Z0-9]+', text2)
                if result:
                    print("二次匹配成功:", result.group())
                    return result.group()
            except TypeError:
                # 处理非字符串输入的情况
                return "无al0信息"

            print("二次匹配失败")
            return "无al0信息"


def parse_and_store_main_data(data, response_msg):
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


def parse_and_store_main_data_fba(data, response_msg):
    """
    解析FBA主数据API返回的数据并存储到MySQL数据库
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


def parse_and_store_email_data(data):
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
                INSERT INTO yaji_email_records (
                    id, message_id, from_addresses, content, content_text,
                    received_time, status, mail_addr, rel_fba_apply_id, subject, status_str,alo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                ON DUPLICATE KEY UPDATE
                    id = VALUES(id),
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
                    alo_capture(record.get('subject'), record.get('contentText'))
                )

                cursor.execute(insert_sql, values)

        connection.commit()
        thread_safe_print(f"成功存储 {len(records)} 条邮件记录到MySQL数据库")

    except Exception as e:
        thread_safe_print(f"MySQL数据存储失败: {e}")
        connection.rollback()
    finally:
        connection.close()