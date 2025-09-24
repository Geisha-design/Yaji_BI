import pymysql
from datetime import datetime, date
# 在文件顶部添加新的导入
import tempfile
from email.mime.application import MIMEApplication
from Yaji_mysql_email import eternal
from Yaji_mysql_main import saika, saika_fba
from yaji_obsidian import thread_safe_print
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from io import BytesIO
import time

# def job():
#     print("每半小时执行一次的任务")
#     # 在这里添加你的具体任务逻辑
#
# # 设置每半小时执行一次
# schedule.every(30).minutes.do(job)
#
# # 或者设置具体的半小时间隔时间点
# # schedule.every().hour.at(":00").do(job)
# # schedule.every().hour.at(":30").do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)


# MySQL数据库配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # 替换为你的MySQL用户名
    'password': 'qyzh12260315',  # 替换为你的MySQL密码
    'database': 'yaji_db',  # 替换为你的数据库名
    'charset': 'utf8mb4'
}


# 在文件顶部添加新的导入


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
def _generate_alo_without_fbe_section(data):
    """生成没有FBE单子的ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-envelope"></i> 邮件ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-file-invoice"></i> FBE编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


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
        return []

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
            AND status_str ='未处理'

            '''

            cursor.execute(select_email_sql, (today,))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print("今天没有找到任何邮件记录")
                return []

            thread_safe_print(f"找到 {len(email_records)} 个不同的ALO编号")

            # 提取所有alo值
            alo_list = [record['alo'] for record in email_records]

            # 在yaji_main中查找对应的cds_booking_no
            # 使用IN查询提高效率
            placeholders = ','.join(['%s'] * len(alo_list))
            select_main_sql = f'''
            SELECT er.id, er.booking_key, er.cds_booking_no, er.ffc_no, er.submit_status_str, er.create_date,m.subject
            FROM yaji_main er
            INNER JOIN yaji_email_records m ON m.alo = er.booking_key
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


def generate_html_report(data):
    """
    生成HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['booking_key']}</strong></td>
            <td><span class="icon">📄</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">🔢</span> {record['ffc_no'] or 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
            <td><span class="icon">📅</span> {record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集即时未处理邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> 亚集统计数据表</h1>
            <p>基于当天邮件记录与主数据的关联分析</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-database"></i> 匹配记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number"><span class="pulse"></span></div>
                <div class="stat-label"><i class="fas fa-sync-alt"></i> 实时数据</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-fingerprint"></i> ID</th>
                        <th><i class="fas fa-key"></i> Booking Key (ALO)</th>
                        <th><i class="fas fa-file-contract"></i> CDS Booking No</th>
                        <th><i class="fas fa-hashtag"></i> FFC No</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                        <th><i class="far fa-calendar-plus"></i> 创建日期</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def save_html_report(html_content, filename=None):
    """
    保存HTML报表到文件
    """
    if filename is None:
        filename = f"alo_booking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        thread_safe_print(f"HTML报表已保存至: {os.path.abspath(filename)}")
        return filename
    except Exception as e:
        thread_safe_print(f"保存HTML报表失败: {e}")
        return None
def generate_html_report2(data):
    # # 确保以下变量都已正确定义
    # id = data.get('id', '')
    # key = data.get('key', '')  # 添加这行或确保key变量已定义
    # cds = data.get('cds', '')
    # ffc = data.get('ffc', '')
    # status = data.get('status', '')
    # date = data.get('date', '')
    from datetime import datetime, date
    """
    生成现代化 HTML 报表（带搜索、主题切换、详情弹窗）
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr onclick="showDetails('{record['id']}','{record['booking_key']}','{record['cds_booking_no'] or 'N/A'}','{record['ffc_no'] or 'N/A'}','{record['submit_status_str'] or '未知'}','{record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}','{record['subject'] or 'N/A'}')">
            <td>{record['id']}</td>
            <td>{record['booking_key']}</td>
            <td>{record['cds_booking_no'] or 'N/A'}</td>
            <td>{record['ffc_no'] or 'N/A'}</td>
            <td><span class="{status_class}">{status_icon} {record['submit_status_str'] or '未知'}</span></td>
            <td>{record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
            <td>{record['subject'] or 'N/A'}</td>
        </tr>
        '''

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>亚集即时未处理邮件统计</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<style>
:root {{
  --bg-light: #f6f8fb;
  --bg-dark: #121826;
  --card-light: rgba(255,255,255,0.92);
  --card-dark: rgba(24,28,36,0.92);
  --text-light: #222;
  --text-dark: #eee;
}}
body {{
  margin:0; font-family:"Segoe UI",sans-serif;
  background: var(--bg-light);
  color: var(--text-light);
  transition: background .3s,color .3s;
}}
[data-theme="dark"] body {{
  background: var(--bg-dark);
  color: var(--text-dark);
}}
.container {{
  max-width:1200px; margin:20px auto;
  background: var(--card-light);
  border-radius:12px; padding:20px;
  box-shadow:0 8px 20px rgba(0,0,0,0.1);
  transition: background .3s;
}}
[data-theme="dark"] .container {{
  background: var(--card-dark);
}}
.header {{
  display:flex;justify-content:space-between;align-items:center;
}}
.theme-toggle {{
  cursor:pointer; border:none; background:#667eea;color:white;
  padding:8px 14px;border-radius:8px;font-size:14px;
}}
.stats {{
  display:flex;justify-content:space-around;flex-wrap:wrap;margin:20px 0;
}}
.stat-item {{
  padding:10px;text-align:center;min-width:160px;
}}
.stat-number {{font-size:1.8em;font-weight:700;color:#667eea;}}
table {{
  width:100%;border-collapse:collapse;margin-top:15px;
}}
th,td {{
  padding:12px;text-align:left;border-bottom:1px solid #ddd;
}}
tr:hover {{
  background:#f1f5ff;cursor:pointer;
}}
.status-active {{color:#155724;background:#d4edda;padding:4px 10px;border-radius:12px;}}
.status-pending {{color:#856404;background:#fff3cd;padding:4px 10px;border-radius:12px;}}
.status-other {{color:#0c5460;background:#d1ecf1;padding:4px 10px;border-radius:12px;}}
/* 弹窗 */
.modal {{
  display:none;position:fixed;top:0;left:0;width:100%;height:100%;
  background:rgba(0,0,0,0.6);align-items:center;justify-content:center;
}}
.modal-content {{
  background:white;padding:20px;border-radius:10px;max-width:500px;width:90%;
}}
[data-theme="dark"] .modal-content {{
  background:#1f2533;color:#fff;
}}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2><i class="fas fa-chart-line"></i> 亚集统计报表</h2>
      <button class="theme-toggle" onclick="toggleTheme()">切换主题</button>
    </div>

    <div class="stats">
      <div class="stat-item">
        <div class="stat-number">{len(data)}</div>
        <div>匹配记录数</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{current_time}</div>
        <div>生成时间</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
        <div>报告日期</div>
      </div>
    </div>

    <input type="text" id="search" placeholder="🔍 搜索 Booking Key..." style="width:100%;padding:10px;margin:10px 0;border-radius:8px;border:1px solid #ccc;">

    <table id="report-table">
      <thead>
        <tr>
          <th>ID</th><th>Booking Key</th><th>CDS No</th><th>FFC No</th><th>状态</th><th>创建日期</th><th>主题</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>

  <!-- 详情弹窗 -->
  <div class="modal" id="detailModal">
    <div class="modal-content">
      <h3>记录详情</h3>
      <p id="detailBody"></p>
      <button onclick="closeModal()">关闭</button>
    </div>
  </div>

<script>
function toggleTheme(){{
  const html=document.documentElement;
  const theme=html.getAttribute("data-theme")==="dark"?"light":"dark";
  html.setAttribute("data-theme",theme);
}}

document.getElementById("search").addEventListener("keyup",function(){{
  let filter=this.value.toLowerCase();
  let rows=document.querySelectorAll("#report-table tbody tr");
  rows.forEach(r=>{{
    r.style.display=r.innerText.toLowerCase().includes(filter)?"":"none";
  }});
}});

function showDetails(id, bookingKey, cdsNo, ffcNo, status, createDate, subject) {{
  const detailBody = document.getElementById('detailBody');
  detailBody.innerHTML = `
    <strong>ID:</strong> ${{id}}<br>
    <strong>Booking Key:</strong> ${{bookingKey}}<br>
    <strong>CDS No:</strong> ${{cdsNo}}<br>
    <strong>FFC No:</strong> ${{ffcNo}}<br>
    <strong>状态:</strong> ${{status}}<br>
    <strong>创建日期:</strong> ${{createDate}}<br>
    <strong>主题:</strong> ${{subject}}<br>
  `;
  document.getElementById("detailModal").style.display="flex";
}}

function closeModal(){{
  document.getElementById("detailModal").style.display="none";
}}
</script>
</body>
</html>
"""
    return html_content

# 在文件末尾添加以下函数

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
    # 邮件配置
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.em.dingtalk.com',  # 阿里云邮箱SMTP服务器，可根据实际邮箱服务商修改
        'smtp_port': 25,
        'sender_email': 'qiyz@smartebao.com',  # 替换为您的邮箱
        'sender_password': 'HHnDyT5v7beJ9Mog',  # 替换为您的邮箱密码或授权码
        'sender_name': 'qiyz@smartebao.com'
    }

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


def send_report_via_email(recipients, data):
    """
    生成并发送报表邮件

    Args:
        recipients (list): 收件人邮箱列表
        data (list): 报表数据

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    if not data:
        thread_safe_print("没有数据可发送邮件")
        return False

    try:
        # 生成HTML报表
        html_content = generate_html_report2(data)

        # 发送邮件
        success = send_email_report(html_content, recipients)

        if success:
            thread_safe_print("报表邮件发送成功")
            return True
        else:
            thread_safe_print("报表邮件发送失败")
            return False

    except Exception as e:
        thread_safe_print(f"发送报表邮件过程中出错: {e}")
        return False


# 在文件末尾添加以下新函数

def query_all_alo_records():
    """
    查询yaji_email_records中当天的所有alo记录（包括已处理和未处理）
    """
    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天的所有记录，获取alo字段
            select_email_sql = '''
            SELECT id, alo, received_time, status_str,subject
            FROM yaji_email_records 
            WHERE DATE(received_time) = %s 
            AND alo IS NOT NULL 
            AND alo != '无al0信息'
            ORDER BY received_time DESC
            '''

            cursor.execute(select_email_sql, (today,))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print("今天没有找到任何ALO邮件记录")
                return []

            thread_safe_print(f"找到 {len(email_records)} 个ALO邮件记录")

            return email_records

    except Exception as e:
        thread_safe_print(f"查询所有ALO记录失败: {e}")
        return []
    finally:
        connection.close()


def generate_all_alo_html_report(data):
    """
    生成包含当天所有ALO号的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天所有ALO邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-envelope"></i> 亚集当天所有ALO邮件统计</h1>
            <p>包含已处理和未处理的所有ALO邮件记录</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-database"></i> 总记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number"><span class="pulse"></span></div>
                <div class="stat-label"><i class="fas fa-sync-alt"></i> 实时数据</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-fingerprint"></i> ID</th>
                        <th><i class="fas fa-key"></i> ALO编号</th>
                        <th><i class="fas fa-envelope"></i> 邮件主题</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def send_all_alo_report_via_email(recipients, data):
    """
    生成并发送包含当天所有ALO号的报表邮件

    Args:
        recipients (list): 收件人邮箱列表
        data (list): 报表数据

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    if not data:
        thread_safe_print("没有ALO数据可发送邮件")
        return False

    try:
        # 生成HTML报表
        html_content = generate_all_alo_html_report(data)

        # 设置邮件主题
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"亚集当天所有ALO邮件统计报表 - {current_time}"

        # 发送邮件
        success = send_email_report(html_content, recipients, subject)

        if success:
            thread_safe_print("所有ALO邮件统计报表发送成功")
            return True
        else:
            thread_safe_print("所有ALO邮件统计报表发送失败")
            return False

    except Exception as e:
        thread_safe_print(f"发送所有ALO邮件统计报表过程中出错: {e}")
        return False


# sairen

# 在文件末尾添加以下新函数

def query_alo_with_fbe_records():
    """
    查询yaji_email_records中当天有对应FBE单子的alo记录
    即在yaji_main中能找到对应booking_key且有fbe_no的记录
    """
    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天的记录，并关联yaji_main查找有cds_booking_no的记录
            select_sql = '''
            SELECT 
                er.id as email_id,
                er.alo,
                er.received_time,
                er.status_str as email_status,
                er.subject,
                m.id as main_id,
                m.cds_booking_no,
                m.submit_status_str,
                m.create_date
            FROM yaji_email_records er
            INNER JOIN yaji_main m ON er.alo = m.booking_key
            WHERE DATE(er.received_time) = %s
            AND er.alo IS NOT NULL
            AND er.alo != '无al0信息'
            AND m.cds_booking_no IS NOT NULL
            AND m.cds_booking_no != ''
            ORDER BY er.received_time DESC
            '''

            cursor.execute(select_sql, (today,))
            records = cursor.fetchall()

            if not records:
                thread_safe_print("今天没有找到有对应FBE单子的ALO邮件记录")
                return []

            thread_safe_print(f"找到 {len(records)} 个有对应FBE单子的ALO邮件记录")
            return records

    except Exception as e:
        thread_safe_print(f"查询有FBE单子的ALO记录失败: {e}")
        return []
    finally:
        connection.close()


def generate_alo_with_fbe_html_report(data):
    """
    生成包含当天有FBE单子的ALO记录的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天有FBE单子的ALO邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-file-invoice"></i> 亚集当天有FBE单子的ALO邮件统计</h1>
            <p>显示当天有对应FBE单子的ALO邮件记录</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-database"></i> 匹配记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number"><span class="pulse"></span></div>
                <div class="stat-label"><i class="fas fa-sync-alt"></i> 实时数据</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-envelope"></i> 邮件ID</th>
                        <th><i class="fas fa-key"></i> ALO编号</th>
                        <th><i class="fas fa-envelope"></i> 邮件主题</th>
                        <th><i class="fas fa-box"></i> CDS编号</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content

def send_alo_with_fbe_report_via_email(recipients, data):
    """
    生成并发送包含当天有FBE单子的ALO记录报表邮件

    Args:
        recipients (list): 收件人邮箱列表
        data (list): 报表数据

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    if not data:
        thread_safe_print("没有有FBE单子的ALO数据可发送邮件")
        return False

    try:
        # 生成HTML报表
        html_content = generate_alo_with_fbe_html_report(data)

        # 设置邮件主题
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"亚集当天有FBE单子的ALO邮件统计报表 - {current_time}"

        # 发送邮件
        success = send_email_report(html_content, recipients, subject)

        if success:
            thread_safe_print("有FBE单子的ALO邮件统计报表发送成功")
            return True
        else:
            thread_safe_print("有FBE单子的ALO邮件统计报表发送失败")
            return False

    except Exception as e:
        thread_safe_print(f"发送有FBE单子的ALO邮件统计报表过程中出错: {e}")
        return False


# 在文件末尾添加以下新函数

def query_no_alo_records():
    """
    查询yaji_email_records中当天没有alo信息的记录
    """
    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天没有alo信息的记录
            select_sql = '''
            SELECT 
                id,
                message_id,
                subject,
                received_time,
                content_text,
                status_str,
                subject
            FROM yaji_email_records 
            WHERE DATE(received_time) = %s
            AND (alo IS NULL OR alo = '无al0信息')
            ORDER BY received_time DESC
            '''

            cursor.execute(select_sql, (today,))
            records = cursor.fetchall()

            if not records:
                thread_safe_print("今天没有找到无ALO信息的邮件记录")
                return []

            thread_safe_print(f"找到 {len(records)} 个无ALO信息的邮件记录")
            return records

    except Exception as e:
        thread_safe_print(f"查询无ALO信息的邮件记录失败: {e}")
        return []
    finally:
        connection.close()


def generate_no_alo_html_report(data):
    """
    生成包含当天无ALO信息邮件记录的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        # 转义邮件内容中的特殊字符，避免破坏HTML结构
        escaped_content = (record['content_text'] or '').replace('"', '&quot;').replace("'", "&#39;") if record[
            'content_text'] else ''

        table_rows += f'''
        <tr onclick="showDetails('{record['id']}', '{record['message_id'] or 'N/A'}', '{record['subject'] or 'N/A'}', '{record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}', '{status_class}', '{escaped_content}')">
            <td><span class="icon">📧</span> {record['id']}</td>
            <td><span class="icon">🆔</span> {record['message_id'] or 'N/A'}</td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天无ALO信息邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
            cursor: pointer;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}

        /* 弹窗样式 */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}

        .modal-content {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}

        .modal-header h3 {{
            margin: 0;
            color: #333;
        }}

        .close {{
            font-size: 1.5em;
            cursor: pointer;
            color: #999;
        }}

        .close:hover {{
            color: #333;
        }}

        .detail-item {{
            margin-bottom: 15px;
        }}

        .detail-label {{
            font-weight: bold;
            color: #667eea;
        }}

        .detail-value {{
            margin-top: 5px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .search-box {{
            margin-bottom: 20px;
        }}

        .search-box input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-question-circle"></i> 亚集当天无ALO信息邮件统计</h1>
            <p>显示当天没有ALO信息的邮件记录</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-database"></i> 记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number"><span class="pulse"></span></div>
                <div class="stat-label"><i class="fas fa-sync-alt"></i> 实时数据</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 搜索邮件主题、消息ID或内容..." onkeyup="searchTable()">
            </div>

            <table id="emailTable">
                <thead>
                    <tr>
                        <th><i class="fas fa-fingerprint"></i> ID</th>
                        <th><i class="fas fa-id-card"></i> 消息ID</th>
                        <th><i class="fas fa-envelope"></i> 主题</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>

    <!-- 详情弹窗 -->
    <div class="modal" id="detailModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-info-circle"></i> 邮件详情</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div id="detailBody"></div>
        </div>
    </div>

    <script>
        // 显示详情弹窗
        function showDetails(id, messageId, subject, receivedTime, statusClass, contentText) {{
            const detailBody = document.getElementById('detailBody');
            const statusText = document.querySelector('.' + statusClass).textContent;

            detailBody.innerHTML = `
                <div class="detail-item">
                    <div class="detail-label"><i class="fas fa-fingerprint"></i> ID:</div>
                    <div class="detail-value">${{id}}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label"><i class="fas fa-id-card"></i> 消息ID:</div>
                    <div class="detail-value">${{messageId}}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label"><i class="fas fa-envelope"></i> 主题:</div>
                    <div class="detail-value">${{subject}}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label"><i class="fas fa-download"></i> 接收时间:</div>
                    <div class="detail-value">${{receivedTime}}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label"><i class="fas fa-tasks"></i> 状态:</div>
                    <div class="detail-value"><span class="${{statusClass}}">${{statusText}}</span></div>
                </div>
                <div class="detail-item">
                    <div class="detail-label"><i class="fas fa-file-alt"></i> 邮件内容:</div>
                    <div class="detail-value">${{contentText || '无内容'}}</div>
                </div>
            `;

            document.getElementById('detailModal').style.display = 'flex';
        }}

        // 关闭弹窗
        function closeModal() {{
            document.getElementById('detailModal').style.display = 'none';
        }}

        // 点击弹窗外部关闭弹窗
        window.onclick = function(event) {{
            const modal = document.getElementById('detailModal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}

        // 搜索功能
        function searchTable() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const table = document.getElementById('emailTable');
            const rows = table.getElementsByTagName('tr');

            for (let i = 1; i < rows.length; i++) {{
                const row = rows[i];
                const cells = row.getElementsByTagName('td');
                let found = false;

                for (let j = 0; j < cells.length; j++) {{
                    const cell = cells[j];
                    if (cell.textContent.toLowerCase().includes(filter)) {{
                        found = true;
                        break;
                    }}
                }}

                row.style.display = found ? '' : 'none';
            }}
        }}
    </script>
</body>
</html>
'''

    return html_content


def send_no_alo_report_via_email(recipients, data):
    """
    生成并发送包含当天无ALO信息邮件记录的报表邮件

    Args:
        recipients (list): 收件人邮箱列表
        data (list): 报表数据

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    if not data:
        thread_safe_print("没有无ALO信息的邮件数据可发送")
        return False

    try:
        # 生成HTML报表
        html_content = generate_no_alo_html_report(data)

        # 设置邮件主题
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"亚集当天无ALO信息邮件统计报表 - {current_time}"

        # 发送邮件
        success = send_email_report(html_content, recipients, subject)

        if success:
            thread_safe_print("无ALO信息邮件统计报表发送成功")
            return True
        else:
            thread_safe_print("无ALO信息邮件统计报表发送失败")
            return False

    except Exception as e:
        thread_safe_print(f"发送无ALO信息邮件统计报表过程中出错: {e}")
        return False


def generate_combined_html_report(data_dict):
    """
    生成包含所有报表的综合HTML报表

    Args:
        data_dict (dict): 包含各类报表数据的字典

    Returns:
        str: HTML内容
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成各部分报表内容
    alo_booking_content = _generate_alo_booking_section(data_dict.get('alo_booking', []))
    all_alo_content = _generate_all_alo_section(data_dict.get('all_alo', []))
    alo_with_fbe_content = _generate_alo_with_fbe_section(data_dict.get('alo_with_fbe', []))
    no_alo_content = _generate_no_alo_section(data_dict.get('no_alo', []))
    # 新增部分
    alo_not_in_main_content = _generate_alo_not_in_main_section(data_dict.get('alo_not_in_main', []))
    # 新增没有FBE单子的部分
    alo_without_fbe_content = _generate_alo_without_fbe_section(data_dict.get('alo_without_fbe', []))

    # 综合HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集RPA数字化报表</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        .section {{
            margin-bottom: 40px;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}

        .section-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            font-size: 1.3em;
            font-weight: 500;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> 亚集RPA数字化报表</h1>
            <p>综合统计分析报告</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data_dict.get('alo_booking', []))}</div>
                <div class="stat-label"><i class="fas fa-link"></i> ALO映射记录</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(data_dict.get('all_alo', []))}</div>
                <div class="stat-label"><i class="fas fa-envelope"></i> 总ALO邮件</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(data_dict.get('alo_with_fbe', []))}</div>
                <div class="stat-label"><i class="fas fa-file-invoice"></i> 有FBE单子</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(data_dict.get('alo_without_fbe', []))}</div>
                <div class="stat-label"><i class="fas fa-file-invoice"></i> 无FBE单子</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(data_dict.get('no_alo', []))}</div>
                <div class="stat-label"><i class="fas fa-question-circle"></i> 无ALO信息</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(data_dict.get('alo_not_in_main', []))}</div>
                <div class="stat-label"><i class="fas fa-exclamation-triangle"></i> 主表中不存在</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <!-- ALO与Booking映射部分 -->
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-link"></i> ALO与Booking映射关系
                </div>
                {alo_booking_content}
            </div>

            <!-- 所有ALO记录部分 -->
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-envelope"></i> 当天所有ALO邮件统计
                </div>
                {all_alo_content}
            </div>

            <!-- 有FBE单子的ALO记录部分 -->
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-file-invoice"></i> 有FBE单子的ALO记录
                </div>
                {alo_with_fbe_content}
            </div>

            <!-- 没有FBE单子的ALO记录部分 -->
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-file-invoice"></i> 无FBE单子的ALO记录
                </div>
                {alo_without_fbe_content}
            </div>

            <!-- 无ALO信息的邮件记录部分 -->
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-question-circle"></i> 无ALO信息的邮件记录
                </div>
                {no_alo_content}
            </div>

            <!-- 在主表中都不存在的ALO记录部分 -->
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-exclamation-triangle"></i> 主表中都不存在的ALO记录
                </div>
                {alo_not_in_main_content}
            </div>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''
    return html_content



def _generate_alo_not_in_main_section(data):
    """生成在主表中都不存在的ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-envelope"></i> 邮件主题</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_alo_booking_section(data):
    """生成ALO与Booking映射部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['booking_key']}</strong></td>
            <td><span class="icon">📄</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">🔢</span> {record['ffc_no'] or 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
            <td><span class="icon">📅</span> {record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-key"></i> Booking Key (ALO)</th>
                <th><i class="fas fa-file-contract"></i> CDS Booking No</th>
                <th><i class="fas fa-hashtag"></i> FFC No</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
                <th><i class="far fa-calendar-plus"></i> 创建日期</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_all_alo_section(data):
    """生成所有ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_alo_with_fbe_section(data):
    """生成有FBE单子的ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-envelope"></i> 邮件ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-file-invoice"></i> FBE编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_no_alo_section(data):
    """生成无ALO信息的邮件记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['id']}</td>
            <td><span class="icon">🆔</span> {record['message_id'] or 'N/A'}</td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
       
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-id-card"></i> 消息ID</th>
                <th><i class="fas fa-envelope"></i> 主题</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def send_combined_report_via_email(recipients, data_dict):
    """
    生成并发送综合报表邮件

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

        # 发送邮件
        success = send_email_report(html_content, recipients, subject)

        if success:
            thread_safe_print("综合报表邮件发送成功")
            return True
        else:
            thread_safe_print("综合报表邮件发送失败")
            return False

    except Exception as e:
        thread_safe_print(f"发送综合报表邮件过程中出错: {e}")
        return False


def send_combined_report_with_attachments(recipients, data_dict):
    """
    生成并发送综合报表邮件，同时附上四份报表作为附件

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

        # 生成并添加四个报表作为附件
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

        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP('smtp.em.dingtalk.com', 25)
        server.starttls()
        server.login('qiyz@smartebao.com', 'HHnDyT5v7beJ9Mog')
        server.send_message(msg)
        server.quit()

        thread_safe_print(f"综合报表邮件(含附件)已成功发送至: {', '.join(recipients)}")
        return True

    except Exception as e:
        thread_safe_print(f"发送综合报表邮件(含附件)过程中出错: {e}")
        return False


def query_alo_not_in_main_tables():
    """
    查询yaji_email_records中当天的alo记录，
    这些记录在yaji_main和yaji_main_fba表中都不存在
    """
    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天的记录，获取alo字段
            select_email_sql = '''
            SELECT id, alo, received_time, status_str, subject
            FROM yaji_email_records 
            WHERE DATE(received_time) = %s 
            AND alo IS NOT NULL 
            AND alo != '无al0信息'
            AND status_str = '未处理'
            '''

            cursor.execute(select_email_sql, (today,))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print("今天没有找到任何邮件记录")
                return []

            # 提取所有alo值
            alo_list = [record['alo'] for record in email_records]

            if not alo_list:
                return []

            # 在yaji_main中查找存在的alo
            placeholders = ','.join(['%s'] * len(alo_list))
            select_main_sql = f'''
            SELECT DISTINCT booking_key 
            FROM yaji_main 
            WHERE booking_key IN ({placeholders})
            '''

            cursor.execute(select_main_sql, alo_list)
            main_existing = cursor.fetchall()
            main_keys = {record['booking_key'] for record in main_existing}

            # 在yaji_main_fba中查找存在的alo
            select_main_fba_sql = f'''
            SELECT DISTINCT booking_key 
            FROM yaji_main_fba 
            WHERE booking_key IN ({placeholders})
            '''

            cursor.execute(select_main_fba_sql, alo_list)
            main_fba_existing = cursor.fetchall()
            main_fba_keys = {record['booking_key'] for record in main_fba_existing}

            # 找出在两个表中都不存在的alo记录
            existing_keys = main_keys.union(main_fba_keys)
            not_existing_records = [
                record for record in email_records
                if record['alo'] not in existing_keys
            ]

            thread_safe_print(f"找到 {len(not_existing_records)} 条在主表中都不存在的ALO记录")
            return not_existing_records

    except Exception as e:
        thread_safe_print(f"查询在主表中不存在的ALO记录失败: {e}")
        return []
    finally:
        connection.close()


def query_alo_without_fbe_records():
    """
    查询yaji_email_records中当天没有对应FBE单子的alo记录
    即在yaji_main中能找到对应booking_key但没有cds_booking_no的记录
    """
    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天的记录，并关联yaji_main查找没有cds_booking_no的记录
            select_sql = '''
            SELECT 
                er.id as email_id,
                er.alo,
                er.received_time,
                er.status_str as email_status,
                er.subject,
                m.id as main_id,
                m.cds_booking_no,
                m.submit_status_str,
                m.create_date
            FROM yaji_email_records er
            INNER JOIN yaji_main_fba m ON er.alo = m.booking_key
            WHERE DATE(er.received_time) = %s
            AND er.alo IS NOT NULL
            AND er.alo != '无al0信息'
            
            ORDER BY er.received_time DESC
            '''

            cursor.execute(select_sql, (today,))
            records = cursor.fetchall()

            if not records:
                thread_safe_print("今天没有找到没有对应FBE单子的ALO邮件记录")
                return []

            thread_safe_print(f"找到 {len(records)} 个没有对应FBE单子的ALO邮件记录")
            return records

    except Exception as e:
        thread_safe_print(f"查询没有FBE单子的ALO记录失败: {e}")
        return []
    finally:
        connection.close()


def generate_alo_without_fbe_html_report(data):
    """
    生成包含当天没有FBE单子的ALO记录的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天没有FBE单子的ALO邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-file-invoice"></i> 亚集当天没有FBE单子的ALO邮件统计</h1>
            <p>显示当天没有对应FBE单子的ALO邮件记录</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-database"></i> 匹配记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number"><span class="pulse"></span></div>
                <div class="stat-label"><i class="fas fa-sync-alt"></i> 实时数据</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-envelope"></i> 邮件ID</th>
                        <th><i class="fas fa-key"></i> ALO编号</th>
                        <th><i class="fas fa-envelope"></i> 邮件主题</th>
                        <th><i class="fas fa-box"></i> CDS编号</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def send_alo_without_fbe_report_via_email(recipients, data):
    """
    生成并发送包含当天没有FBE单子的ALO记录报表邮件

    Args:
        recipients (list): 收件人邮箱列表
        data (list): 报表数据

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    if not data:
        thread_safe_print("没有没有FBE单子的ALO数据可发送邮件")
        return False

    try:
        # 生成HTML报表
        html_content = generate_alo_without_fbe_html_report(data)

        # 设置邮件主题
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"亚集当天没有FBE单子的ALO邮件统计报表 - {current_time}"

        # 发送邮件
        success = send_email_report(html_content, recipients, subject)

        if success:
            thread_safe_print("没有FBE单子的ALO邮件统计报表发送成功")
            return True
        else:
            thread_safe_print("没有FBE单子的ALO邮件统计报表发送失败")
            return False

    except Exception as e:
        thread_safe_print(f"发送没有FBE单子的ALO邮件统计报表过程中出错: {e}")
        return False


# 修改主程序部分
def main():
    saika()
    saika_fba()
    eternal()

    # 查询数据
    data = query_alo_and_booking_mapping()
    # 查询所有ALO记录
    all_alo_data = query_all_alo_records()
    # 查询有FBE单子的ALO记录
    alo_with_fbe_data = query_alo_with_fbe_records()
    # 查询没有FBE单子的ALO记录（新增）
    alo_without_fbe_data = query_alo_without_fbe_records()
    # 查询无ALO信息的邮件记录
    no_alo_data = query_no_alo_records()
    # 查询在主表中都不存在的ALO记录
    alo_not_in_main_data = query_alo_not_in_main_tables()

    # 定义收件人列表
    recipients = [
        'qiyz@smartebao.com',
        'luye@smartebao.com',
        'zhuke@smartebao.com',
        'wangk@smartebao.com',
        'xumy@smartebao.com'
    ]

    # 准备综合报表数据
    combined_data = {
        'alo_booking': data,
        'all_alo': all_alo_data,
        'alo_with_fbe': alo_with_fbe_data,
        'alo_without_fbe': alo_without_fbe_data,  # 新增数据
        'no_alo': no_alo_data,
        'alo_not_in_main': alo_not_in_main_data  # 新增数据
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
        filename = save_html_report(html_content)
        if filename:
            thread_safe_print(f"ALO映射报表已保存: {filename}")

    # # ***************************************************
    # # 发送当天所有ALO号邮件统计报表
    # if all_alo_data:
    #     all_alo_email_sent = send_all_alo_report_via_email(recipients, all_alo_data)
    #
    # # ***************************************************
    # # 发送当天有FBE单子的ALO记录报表
    # if alo_with_fbe_data:
    #     alo_with_fbe_email_sent = send_alo_with_fbe_report_via_email(recipients, alo_with_fbe_data)
    #
    # # ***************************************************
    # # 发送当天无ALO信息的邮件记录报表
    # if no_alo_data:
    #     no_alo_email_sent = send_no_alo_report_via_email(recipients, no_alo_data)


def job():
    print("每半小时执行一次的任务")
    # 在这里添加你的具体任务逻辑
    main()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(3600)


