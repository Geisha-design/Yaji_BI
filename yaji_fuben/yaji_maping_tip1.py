import pymysql
from datetime import datetime, date
from yaji_obsidian import thread_safe_print
import os

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
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"

        table_rows += f'''
        <tr>
            <td>{record['id']}</td>
            <td><strong>{record['booking_key']}</strong></td>
            <td>{record['cds_booking_no'] or 'N/A'}</td>
            <td>{record['ffc_no'] or 'N/A'}</td>
            <td><span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
            <td>{record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集即时未处理邮件统计</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .content {{
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 15px;
            font-weight: 500;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e9f7fe;
            transition: background-color 0.3s;
        }}
        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
        }}
        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
        }}
        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
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
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>亚集统计数据表</h1>
            <p>基于当天邮件记录与主数据的关联分析</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label">匹配记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label">生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label">报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Booking Key (ALO)</th>
                        <th>CDS Booking No</th>
                        <th>FFC No</th>
                        <th>状态</th>
                        <th>创建日期</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台 </p>
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


# 在主函数中调用
if __name__ == '__main__':
    # 查询数据
    data = query_alo_and_booking_mapping()

    # 生成HTML报表
    if data:
        html_content = generate_html_report(data)
        # 保存报表
        filename = save_html_report(html_content)

        if filename:
            thread_safe_print(f"报表生成成功: {filename}")
        else:
            thread_safe_print("报表生成失败")
    else:
        thread_safe_print("没有数据可生成报表")
