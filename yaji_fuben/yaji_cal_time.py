import pymysql
from datetime import datetime, date, timedelta
# 在文件顶部添加新的导入
import tempfile
import os
from email.mime.application import MIMEApplication
from Yaji_mysql_email import eternal
from Yaji_mysql_main import saika
from yaji_obsidian import thread_safe_print
import os
# 在文件顶部导入所需模块
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from io import BytesIO
import xlsxwriter

import schedule
import time


# ... 其他现有代码保持不变 ...

def get_date_range():
    """
    获取用户输入的日期范围

    Returns:
        tuple: (start_date, end_date) 日期范围
    """
    print("请选择日期范围查询模式:")
    print("1. 查询当天数据")
    print("2. 查询指定日期数据")
    print("3. 查询日期范围数据")

    choice = input("请输入选项 (1-3, 默认为1): ").strip() or "1"

    if choice == "1":
        # 当天数据
        start_date = date.today()
        end_date = date.today()
    elif choice == "2":
        # 指定日期
        date_input = input("请输入日期 (格式: YYYY-MM-DD, 默认为今天): ").strip() or date.today().strftime("%Y-%m-%d")
        try:
            target_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            start_date = target_date
            end_date = target_date
        except ValueError:
            print("日期格式错误，使用当天日期")
            start_date = date.today()
            end_date = date.today()
    elif choice == "3":
        # 日期范围
        start_input = input("请输入开始日期 (格式: YYYY-MM-DD, 默认为今天): ").strip() or date.today().strftime(
            "%Y-%m-%d")
        end_input = input("请输入结束日期 (格式: YYYY-MM-DD, 默认为今天): ").strip() or date.today().strftime(
            "%Y-%m-%d")
        try:
            start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_input, "%Y-%m-%d").date()
            if start_date > end_date:
                print("开始日期晚于结束日期，自动调整")
                start_date, end_date = end_date, start_date
        except ValueError:
            print("日期格式错误，使用当天日期")
            start_date = date.today()
            end_date = date.today()
    else:
        print("无效选项，使用当天日期")
        start_date = date.today()
        end_date = date.today()

    print(f"查询日期范围: {start_date} 至 {end_date}")
    return start_date, end_date


def query_alo_and_booking_mapping(start_date=None, end_date=None):
    """
    查询yaji_email_records中指定日期范围记录的alo字段，
    并在yaji_main中查找对应的cds_booking_no

    Args:
        start_date (date): 开始日期，默认为当天
        end_date (date): 结束日期，默认为当天
    """
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()

    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 查询yaji_email_records中指定日期范围的记录，获取alo字段
            select_email_sql = '''
            SELECT DISTINCT alo 
            FROM yaji_email_records 
            WHERE DATE(received_time) BETWEEN %s AND %s
            AND alo IS NOT NULL 
            AND alo != '无al0信息'
            AND status_str ='未处理'
            '''

            cursor.execute(select_email_sql, (start_date, end_date))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print(f"在 {start_date} 至 {end_date} 期间没有找到任何邮件记录")
                return []

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
            return main_records

    except Exception as e:
        thread_safe_print(f"查询ALO和Booking映射关系失败: {e}")
        return []
    finally:
        connection.close()


def query_all_alo_records(start_date=None, end_date=None):
    """
    查询yaji_email_records中指定日期范围的所有alo记录（包括已处理和未处理）

    Args:
        start_date (date): 开始日期，默认为当天
        end_date (date): 结束日期，默认为当天
    """
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()

    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 查询yaji_email_records中指定日期范围的所有记录，获取alo字段
            select_email_sql = '''
            SELECT id, alo, received_time, status_str
            FROM yaji_email_records 
            WHERE DATE(received_time) BETWEEN %s AND %s
            AND alo IS NOT NULL 
            AND alo != '无al0信息'
            ORDER BY received_time DESC
            '''

            cursor.execute(select_email_sql, (start_date, end_date))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print(f"在 {start_date} 至 {end_date} 期间没有找到任何ALO邮件记录")
                return []

            thread_safe_print(f"找到 {len(email_records)} 个ALO邮件记录")

            return email_records

    except Exception as e:
        thread_safe_print(f"查询所有ALO记录失败: {e}")
        return []
    finally:
        connection.close()


def query_alo_with_fbe_records(start_date=None, end_date=None):
    """
    查询指定日期范围内有对应FBE单子的alo记录

    Args:
        start_date (date): 开始日期，默认为当天
        end_date (date): 结束日期，默认为当天
    """
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()

    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 查询yaji_email_records中指定日期范围的记录，并关联yaji_main查找有cds_booking_no的记录
            select_sql = '''
            SELECT 
                er.id as email_id,
                er.alo,
                er.received_time,
                er.status_str as email_status,
                m.id as main_id,
                m.cds_booking_no,
                m.submit_status_str,
                m.create_date
            FROM yaji_email_records er
            INNER JOIN yaji_main m ON er.alo = m.booking_key
            WHERE DATE(er.received_time) BETWEEN %s AND %s
            AND er.alo IS NOT NULL
            AND er.alo != '无al0信息'
            AND m.cds_booking_no IS NOT NULL
            AND m.cds_booking_no != ''
            ORDER BY er.received_time DESC
            '''

            cursor.execute(select_sql, (start_date, end_date))
            records = cursor.fetchall()

            if not records:
                thread_safe_print(f"在 {start_date} 至 {end_date} 期间没有找到有对应FBE单子的ALO邮件记录")
                return []

            thread_safe_print(f"找到 {len(records)} 个有对应FBE单子的ALO邮件记录")
            return records

    except Exception as e:
        thread_safe_print(f"查询有FBE单子的ALO记录失败: {e}")
        return []
    finally:
        connection.close()


def query_no_alo_records(start_date=None, end_date=None):
    """
    查询指定日期范围内没有alo信息的记录

    Args:
        start_date (date): 开始日期，默认为当天
        end_date (date): 结束日期，默认为当天
    """
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()

    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 查询yaji_email_records中指定日期范围没有alo信息的记录
            select_sql = '''
            SELECT 
                id,
                message_id,
                subject,
                received_time,
                content_text,
                status_str
            FROM yaji_email_records 
            WHERE DATE(received_time) BETWEEN %s AND %s
            AND (alo IS NULL OR alo = '无al0信息')
            ORDER BY received_time DESC
            '''

            cursor.execute(select_sql, (start_date, end_date))
            records = cursor.fetchall()

            if not records:
                thread_safe_print(f"在 {start_date} 至 {end_date} 期间没有找到无ALO信息的邮件记录")
                return []

            thread_safe_print(f"找到 {len(records)} 个无ALO信息的邮件记录")
            return records

    except Exception as e:
        thread_safe_print(f"查询无ALO信息的邮件记录失败: {e}")
        return []
    finally:
        connection.close()


def update_html_report_titles(html_content, start_date, end_date):
    """
    更新HTML报表中的标题和时间信息以反映查询的日期范围

    Args:
        html_content (str): 原始HTML内容
        start_date (date): 查询开始日期
        end_date (date): 查询结束日期

    Returns:
        str: 更新后的HTML内容
    """
    # 更新报表标题中的日期信息
    date_range_text = f"{start_date} 至 {end_date}" if start_date != end_date else f"{start_date}"

    # 替换HTML中的日期显示
    html_content = html_content.replace(
        '<div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>',
        f'<div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期: {date_range_text}</div>'
    )

    return html_content


def main():
    # 获取用户指定的日期范围
    start_date, end_date = get_date_range()

    saika()
    eternal()

    # 查询指定日期范围的数据
    data = query_alo_and_booking_mapping(start_date, end_date)
    # 查询所有ALO记录
    all_alo_data = query_all_alo_records(start_date, end_date)
    # 查询有FBE单子的ALO记录
    alo_with_fbe_data = query_alo_with_fbe_records(start_date, end_date)
    # 查询无ALO信息的邮件记录
    no_alo_data = query_no_alo_records(start_date, end_date)

    # 定义收件人列表
    recipients = [
        'qiyz@smartebao.com',
        'luye@smartebao.com',
        'zhuke@smartebao.com',
        'wangk@smartebao.com'
    ]

    # 准备综合报表数据
    combined_data = {
        'alo_booking': data,
        'all_alo': all_alo_data,
        'alo_with_fbe': alo_with_fbe_data,
        'no_alo': no_alo_data
    }

    # 发送综合报表邮件(含HTML和Excel附件)
    combined_email_sent = send_combined_report_with_attachments_and_excel(recipients, combined_data)

    if combined_email_sent:
        thread_safe_print("综合报表邮件(含HTML和Excel附件)发送成功")
    else:
        thread_safe_print("综合报表邮件(含HTML和Excel附件)发送失败")

    # 如果需要，也可以单独保存各报表
    if data:
        html_content = generate_html_report2(data)
        # 更新报表中的日期信息
        html_content = update_html_report_titles(html_content, start_date, end_date)
        filename = save_html_report(html_content)
        if filename:
            thread_safe_print(f"ALO映射报表已保存: {filename}")


def job():
    print("每半小时执行一次的任务")
    # 在这里添加你的具体任务逻辑
    main()


if __name__ == '__main__':
    # 设置每半小时执行一次
    schedule.every(30).minutes.do(job)

    # 或者设置具体的半小时间隔时间点
    # schedule.every().hour.at(":00").do(job)
    # schedule.every().hour.at(":30").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
