"""
邮件发送器
"""
import smtplib
import tempfile
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config.email_config import EMAIL_CONFIG
from reports.generator import generate_combined_html_report, generate_html_report2, generate_all_alo_html_report, \
    generate_alo_with_fbe_html_report, generate_no_alo_html_report
from utils.helpers import thread_safe_print
from io import BytesIO
import pandas as pd


def send_email_report(html_content, recipients, subject=None):
    """
    发送HTML报表邮件给指定用户

    Args:
        html_content (str): HTML邮件内容
        recipients (list): 收件人邮箱列表
        subject (str): 邮件主题，默认为自动生成

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    try:
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg['To'] = ', '.join(recipients)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg['Subject'] = subject or f"亚集即时未处理邮件统计报表 - {current_time}"

        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()

        thread_safe_print(f"邮件已成功发送至: {', '.join(recipients)}")
        return True

    except Exception as e:
        thread_safe_print(f"发送邮件失败: {e}")
        return False


def _convert_data_to_excel(data_dict):
    """
    将数据转换为Excel格式的字节流

    Args:
        data_dict (dict): 包含各类报表数据的字典

    Returns:
        BytesIO: Excel文件的字节流
    """
    # 创建内存中的Excel文件
    excel_buffer = BytesIO()

    # 创建Excel写入器
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        # 转换ALO与Booking映射数据
        if data_dict.get('alo_booking'):
            alo_booking_df = pd.DataFrame(data_dict['alo_booking'])
            # 处理datetime对象
            for col in alo_booking_df.columns:
                if pd.api.types.is_datetime64_any_dtype(alo_booking_df[col]):
                    alo_booking_df[col] = alo_booking_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            alo_booking_df.to_excel(writer, sheet_name='ALO_Booking映射', index=False)

        # 转换所有ALO记录数据
        if data_dict.get('all_alo'):
            all_alo_df = pd.DataFrame(data_dict['all_alo'])
            # 处理datetime对象
            for col in all_alo_df.columns:
                if pd.api.types.is_datetime64_any_dtype(all_alo_df[col]):
                    all_alo_df[col] = all_alo_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            all_alo_df.to_excel(writer, sheet_name='所有ALO记录', index=False)

        # 转换有FBE单子的ALO记录数据
        if data_dict.get('alo_with_fbe'):
            alo_with_fbe_df = pd.DataFrame(data_dict['alo_with_fbe'])
            # 处理datetime对象
            for col in alo_with_fbe_df.columns:
                if pd.api.types.is_datetime64_any_dtype(alo_with_fbe_df[col]):
                    alo_with_fbe_df[col] = alo_with_fbe_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            alo_with_fbe_df.to_excel(writer, sheet_name='有FBE单子的ALO', index=False)

        # 转换无ALO信息的邮件记录数据
        if data_dict.get('no_alo'):
            no_alo_df = pd.DataFrame(data_dict['no_alo'])
            # 处理datetime对象
            for col in no_alo_df.columns:
                if pd.api.types.is_datetime64_any_dtype(no_alo_df[col]):
                    no_alo_df[col] = no_alo_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            no_alo_df.to_excel(writer, sheet_name='无ALO信息邮件', index=False)

        # 转换在主表中都不存在的ALO记录数据
        if data_dict.get('alo_not_in_main'):
            alo_not_in_main_df = pd.DataFrame(data_dict['alo_not_in_main'])
            # 处理datetime对象
            for col in alo_not_in_main_df.columns:
                if pd.api.types.is_datetime64_any_dtype(alo_not_in_main_df[col]):
                    alo_not_in_main_df[col] = alo_not_in_main_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            alo_not_in_main_df.to_excel(writer, sheet_name='主表中不存在的ALO', index=False)

        # 转换没有FBE单子的ALO记录数据（新增）
        if data_dict.get('alo_without_fbe'):
            alo_without_fbe_df = pd.DataFrame(data_dict['alo_without_fbe'])
            # 处理datetime对象
            for col in alo_without_fbe_df.columns:
                if pd.api.types.is_datetime64_any_dtype(alo_without_fbe_df[col]):
                    alo_without_fbe_df[col] = alo_without_fbe_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            alo_without_fbe_df.to_excel(writer, sheet_name='无FBE单子的ALO', index=False)

    # 重置缓冲区指针到开始位置
    excel_buffer.seek(0)
    return excel_buffer


def send_combined_report_with_attachments_and_excel(recipients, data_dict):
    """
    生成并发送综合报表邮件，同时附上四份报表作为HTML附件和一个Excel文件

    Args:
        recipients (list): 收件人邮箱列表
        data_dict (dict): 包含各类报表数据的字典

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    try:
        # 生成综合HTML报表
        html_content = generate_combined_html_report(data_dict)

        # 设置邮件主题
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"亚集RPA数字化报表 - {current_time}"

        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        msg['From'] = 'qiyz@smartebao.com'
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject

        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # 生成并添加四个报表作为HTML附件
        attachments = [
            ("alo_booking_report.html", generate_html_report2(data_dict.get('alo_booking', []))),
            ("all_alo_report.html", generate_all_alo_html_report(data_dict.get('all_alo', []))),
            ("alo_with_fbe_report.html", generate_alo_with_fbe_html_report(data_dict.get('alo_with_fbe', []))),
            ("no_alo_report.html", generate_no_alo_html_report(data_dict.get('no_alo', [])))
        ]

        for filename, content in attachments:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.html') as f:
                f.write(content)
                temp_filename = f.name

            # 添加附件
            with open(temp_filename, 'rb') as attachment:
                part = MIMEApplication(attachment.read(), _subtype="html")
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(part)

            # 删除临时文件
            os.unlink(temp_filename)

        # 生成并添加Excel文件作为附件
        try:
            excel_buffer = _convert_data_to_excel(data_dict)
            excel_part = MIMEApplication(excel_buffer.read(),
                                         _subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            excel_part.add_header('Content-Disposition', 'attachment', filename="亚集RPA数据报表.xlsx")
            msg.attach(excel_part)
        except Exception as e:
            thread_safe_print(f"生成Excel附件时出错: {e}")

        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP('smtp.em.dingtalk.com', 25)
        server.starttls()
        server.login('qiyz@smartebao.com', 'HHnDyT5v7beJ9Mog')
        server.send_message(msg)
        server.quit()

        thread_safe_print(f"综合报表邮件(含HTML和Excel附件)已成功发送至: {', '.join(recipients)}")
        return True

    except Exception as e:
        thread_safe_print(f"发送综合报表邮件(含附件)过程中出错: {e}")
        return False