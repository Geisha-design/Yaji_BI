"""
网页数据解析器
"""
import json
import requests
import concurrent.futures
from utils.helpers import thread_safe_print, escape_html_content
from datetime import datetime
import html


def fetch_detailed_list_data(headers, submit_status="", booking_keys="", cds_booking_no="", page_no=1, page_size=10):
    """
    获取详细列表数据的函数
    """
    url = "https://www.yagikoifish.com/vms/fbaApply/v/getList4Page"
    params = {
        "submitStatus": submit_status,
        "bookingKeys": booking_keys,
        "cdsBookingNo": cds_booking_no,
        "pageNo": page_no,
        "pageSize": page_size
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=30)
        data = json.loads(response.text)

        thread_safe_print(f"详细列表接口响应: {data.get('msg')}, 状态: {data.get('status')}")
        return data
    except Exception as e:
        thread_safe_print(f"获取详细列表数据失败: {e}")
        return None


def fetch_mail_data(record_id, headers):
    """
    多线程获取邮件数据的函数
    """
    try:
        mail_response = requests.post(
            f"https://www.yagikoifish.com/vms/fbaMail/getListByRelApplyId?relApplyFileId={record_id}",
            headers=headers,
            timeout=30  # 设置超时时间
        )

        mail_data = json.loads(mail_response.text)
        mail_msg = mail_data.get('msg')
        mail_status = mail_data.get('status')
        mail_records = mail_data.get('data', [])

        thread_safe_print(f"    ID {record_id} 邮件查询结果: {mail_msg}, 状态: {mail_status}")

        mail_count = len(mail_records) if mail_records else 0
        has_unprocessed_mail = False
        need_manual_intervention = False

        if mail_records:
            thread_safe_print(f"    ID {record_id} 邮件数量: {mail_count}")
            # 检查是否有状态为"未处理"的邮件
            for mail in mail_records:
                mail_title = mail.get('title', '无标题')
                mail_create_date = mail.get('createDate', '未知时间')
                mail_status_str = mail.get('statusStr', '')  # 获取邮件状态
                thread_safe_print(f"      ID {record_id} 邮件: {mail_title}, 创建时间: {mail_create_date}")
                # 检查是否有邮件状态为"未处理"
                if mail_status_str == "未处理":
                    has_unprocessed_mail = True
                    need_manual_intervention = True
            if need_manual_intervention:
                thread_safe_print(f"    ID {record_id} 人工介入")
        else:
            thread_safe_print(f"    ID {record_id} 无相关邮件")

        return {
            'id': record_id,
            'mail_count': mail_count,
            'has_unprocessed_mail': has_unprocessed_mail,
            'need_manual_intervention': need_manual_intervention,
            'error': None
        }
    except Exception as e:
        thread_safe_print(f"    ID {record_id} 邮件查询解析失败: {e}")
        return {
            'id': record_id,
            'mail_count': 0,
            'has_unprocessed_mail': False,
            'need_manual_intervention': False,
            'error': str(e)
        }


def generate_html_report(records_data):
    """
    生成美观的HTML报表，对未处理的数据行标红
    """
    # 安全处理数据，防止特殊字符导致错误
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_records = len(records_data)
    unprocessed_count = sum(1 for record in records_data if record.get('need_manual_intervention', False))
    processed_count = total_records - unprocessed_count

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Yaji Data Check Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f7fa;
                color: #333;
                line-height: 1.6;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}

            h1 {{
                font-size: 2.2em;
                margin-bottom: 10px;
            }}

            .report-time {{
                font-size: 1.1em;
                opacity: 0.9;
            }}

            .summary-cards {{
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }}

            .card {{
                flex: 1;
                min-width: 250px;
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease;
            }}

            .card:hover {{
                transform: translateY(-5px);
            }}

            .card.total {{
                border-top: 5px solid #4e73df;
            }}

            .card.unprocessed {{
                border-top: 5px solid #e74a3b;
            }}

            .card.processed {{
                border-top: 5px solid #1cc88a;
            }}

            .card h3 {{
                font-size: 1.1em;
                margin-bottom: 10px;
                color: #555;
            }}

            .card .number {{
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }}

            .card.total .number {{
                color: #4e73df;
            }}

            .card.unprocessed .number {{
                color: #e74a3b;
            }}

            .card.processed .number {{
                color: #1cc88a;
            }}

            .data-table-container {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                margin-bottom: 30px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: left;
                padding: 15px 20px;
                font-weight: 600;
            }}

            td {{
                padding: 12px 20px;
                border-bottom: 1px solid #eee;
            }}

            tr:nth-child(even) {{
                background-color: #f8f9fc;
            }}

            tr:hover {{
                background-color: #e3f2fd;
            }}

            .unprocessed-row {{
                background-color: #ffebee !important;
                border-left: 4px solid #e74a3b;
            }}

            .processed-row {{
                background-color: #e8f5e9;
            }}

            .status-badge {{
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
                text-align: center;
            }}

            .badge-unprocessed {{
                background-color: #f8d7da;
                color: #721c24;
            }}

            .badge-processed {{
                background-color: #d4edda;
                color: #155724;
            }}

            .action-required {{
                color: #e74a3b;
                font-weight: bold;
            }}

            .action-normal {{
                color: #1cc88a;
                font-weight: bold;
            }}

            footer {{
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                color: #6c757d;
                font-size: 0.9em;
            }}

            @media (max-width: 768px) {{
                .summary-cards {{
                    flex-direction: column;
                }}

                th, td {{
                    padding: 10px 15px;
                }}

                .card {{
                    min-width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Yaji 数据检查报告</h1>
                <div class="report-time">生成时间: {report_time}</div>
            </header>

            <div class="summary-cards">
                <div class="card total">
                    <h3>总记录数</h3>
                    <div class="number">{total_records}</div>
                    <p>所有数据记录</p>
                </div>

                <div class="card unprocessed">
                    <h3>待处理记录</h3>
                    <div class="number">{unprocessed_count}</div>
                    <p>需要人工介入</p>
                </div>

                <div class="card processed">
                    <h3>已处理记录</h3>
                    <div class="number">{processed_count}</div>
                    <p>状态正常</p>
                </div>
            </div>

            <div class="data-table-container">
                <table>
                    <thead>
                        <tr>
                            <th>订舱号</th>
                            <th>状态</th>
                            <th>创建人</th>
                            <th>创建时间</th>
                            <th>ID</th>
                            <th>邮件数量</th>
                            <th>未处理邮件</th>
                            <th>操作建议</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for record in records_data:
        # 判断是否需要人工介入
        row_class = "unprocessed-row" if record.get('need_manual_intervention', False) else "processed-row"
        status_badge_class = "badge-unprocessed" if record.get('need_manual_intervention', False) else "badge-processed"
        action_class = "action-required" if record.get('need_manual_intervention', False) else "action-normal"
        action_text = "需要人工介入" if record.get('need_manual_intervention', False) else "正常"

        # 安全转义所有字段内容
        booking_no = escape_html_content(record.get('booking_no', ''))
        submit_status = escape_html_content(record.get('submit_status', ''))
        creater = escape_html_content(record.get('creater', ''))
        create_date = escape_html_content(record.get('create_date', ''))
        record_id = escape_html_content(record.get('id', ''))
        mail_count = escape_html_content(record.get('mail_count', 0))
        has_unprocessed_mail = '是' if record.get('has_unprocessed_mail', False) else '否'

        html_content += f"""
                        <tr class="{row_class}">
                            <td><strong>{booking_no}</strong></td>
                            <td><span class="status-badge {status_badge_class}">{submit_status}</span></td>
                            <td>{creater}</td>
                            <td>{create_date}</td>
                            <td>{record_id}</td>
                            <td>{mail_count}</td>
                            <td>{has_unprocessed_mail}</td>
                            <td class="{action_class}">{action_text}</td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>

            <footer>
                <p>© 2025 Yaji Data Check Report | 自动生成</p>
            </footer>
        </div>
    </body>
    </html>
    """

    # 保存HTML文件
    filename = f"yaji_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        thread_safe_print(f"HTML报表已生成: {filename}")
    except Exception as e:
        thread_safe_print(f"生成HTML报表时出错: {e}")
        # 尝试使用不同的编码
        try:
            with open(filename, 'w', encoding='gbk') as f:
                f.write(html_content)
            thread_safe_print(f"HTML报表已生成(GBK编码): {filename}")
        except Exception as e2:
            thread_safe_print(f"生成HTML报表失败: {e2}")

    return filename