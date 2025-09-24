import json
import time
import requests
from loguru import logger
from DrissionPage import WebPage, ChromiumOptions, SessionOptions
import random
from datetime import datetime


def randomSleep():
    # 设置随机休眠时间，范围从min_seconds到max_seconds，整数秒
    min_seconds = 1
    max_seconds = 3
    # 生成一个随机整数，表示休眠的时间（秒）
    sleep_time = random.randint(min_seconds, max_seconds)
    print(f"Randomly selected sleep time: {sleep_time} seconds")
    # 让程序休眠这个随机时间
    time.sleep(sleep_time)


def generate_html_report(records_data):
    """
    生成美观的HTML报表，对未处理的数据行标红
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Yaji Data Check Report</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f7fa;
                color: #333;
                line-height: 1.6;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
            }

            header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }

            h1 {
                font-size: 2.2em;
                margin-bottom: 10px;
            }

            .report-time {
                font-size: 1.1em;
                opacity: 0.9;
            }

            .summary-cards {
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }

            .card {
                flex: 1;
                min-width: 250px;
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease;
            }

            .card:hover {
                transform: translateY(-5px);
            }

            .card.total {
                border-top: 5px solid #4e73df;
            }

            .card.unprocessed {
                border-top: 5px solid #e74a3b;
            }

            .card.processed {
                border-top: 5px solid #1cc88a;
            }

            .card h3 {
                font-size: 1.1em;
                margin-bottom: 10px;
                color: #555;
            }

            .card .number {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }

            .card.total .number {
                color: #4e73df;
            }

            .card.unprocessed .number {
                color: #e74a3b;
            }

            .card.processed .number {
                color: #1cc88a;
            }

            .data-table-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                margin-bottom: 30px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: left;
                padding: 15px 20px;
                font-weight: 600;
            }

            td {
                padding: 12px 20px;
                border-bottom: 1px solid #eee;
            }

            tr:nth-child(even) {
                background-color: #f8f9fc;
            }

            tr:hover {
                background-color: #e3f2fd;
            }

            .unprocessed-row {
                background-color: #ffebee !important;
                border-left: 4px solid #e74a3b;
            }

            .processed-row {
                background-color: #e8f5e9;
            }

            .status-badge {
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
                text-align: center;
            }

            .badge-unprocessed {
                background-color: #f8d7da;
                color: #721c24;
            }

            .badge-processed {
                background-color: #d4edda;
                color: #155724;
            }

            .action-required {
                color: #e74a3b;
                font-weight: bold;
            }

            .action-normal {
                color: #1cc88a;
                font-weight: bold;
            }

            footer {
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                color: #6c757d;
                font-size: 0.9em;
            }

            @media (max-width: 768px) {
                .summary-cards {
                    flex-direction: column;
                }

                th, td {
                    padding: 10px 15px;
                }

                .card {
                    min-width: 100%;
                }
            }
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
    """.format(
        report_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_records=len(records_data),
        unprocessed_count=sum(1 for record in records_data if record.get('need_manual_intervention', False)),
        processed_count=sum(1 for record in records_data if not record.get('need_manual_intervention', False))
    )

    for record in records_data:
        # 判断是否需要人工介入
        row_class = "unprocessed-row" if record.get('need_manual_intervention', False) else "processed-row"
        status_badge_class = "badge-unprocessed" if record.get('need_manual_intervention', False) else "badge-processed"
        action_class = "action-required" if record.get('need_manual_intervention', False) else "action-normal"
        action_text = "需要人工介入" if record.get('need_manual_intervention', False) else "正常"

        html_content += f"""
                        <tr class="{row_class}">
                            <td><strong>{record.get('booking_no', '')}</strong></td>
                            <td><span class="status-badge {status_badge_class}">{record.get('submit_status', '')}</span></td>
                            <td>{record.get('creater', '')}</td>
                            <td>{record.get('create_date', '')}</td>
                            <td>{record.get('id', '')}</td>
                            <td>{record.get('mail_count', 0)}</td>
                            <td>{'是' if record.get('has_unprocessed_mail', False) else '否'}</td>
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
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML报表已生成: {filename}")
    return filename


# def generate_html_report(records_data):
#     """
#     生成HTML报表，对未处理的数据行标红
#     """
#     html_content = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <title>Yaji Data Check Report</title>
#         <style>
#             body {
#                 font-family: Arial, sans-serif;
#                 margin: 20px;
#             }
#             h1 {
#                 color: #333;
#             }
#             table {
#                 border-collapse: collapse;
#                 width: 100%;
#                 margin-top: 20px;
#             }
#             th, td {
#                 border: 1px solid #ddd;
#                 padding: 12px;
#                 text-align: left;
#             }
#             th {
#                 background-color: #f2f2f2;
#                 font-weight: bold;
#             }
#             tr:nth-child(even) {
#                 background-color: #f9f9f9;
#             }
#             .unprocessed {
#                 background-color: #ffcccc !important; /* 红色背景 */
#                 font-weight: bold;
#             }
#             .processed {
#                 background-color: #ccffcc; /* 绿色背景 */
#             }
#             .summary {
#                 margin-top: 20px;
#                 padding: 15px;
#                 background-color: #f0f0f0;
#                 border-radius: 5px;
#             }
#         </style>
#     </head>
#     <body>
#         <h1>Yaji 数据检查报告</h1>
#         <p>生成时间: {report_time}</p>
#
#         <div class="summary">
#             <h2>统计摘要</h2>
#             <p>总记录数: {total_records}</p>
#             <p>需要人工介入的记录数: {unprocessed_count}</p>
#         </div>
#
#         <table>
#             <thead>
#                 <tr>
#                     <th>订舱号</th>
#                     <th>状态</th>
#                     <th>创建人</th>
#                     <th>创建时间</th>
#                     <th>ID</th>
#                     <th>邮件数量</th>
#                     <th>未处理邮件</th>
#                     <th>操作建议</th>
#                 </tr>
#             </thead>
#             <tbody>
#     """.format(
#         report_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         total_records=len(records_data),
#         unprocessed_count=sum(1 for record in records_data if record.get('need_manual_intervention', False))
#     )
#
#     for record in records_data:
#         # 判断是否需要人工介入
#         row_class = "unprocessed" if record.get('need_manual_intervention', False) else "processed"
#
#         html_content += f"""
#                 <tr class="{row_class}">
#                     <td>{record.get('booking_no', '')}</td>
#                     <td>{record.get('submit_status', '')}</td>
#                     <td>{record.get('creater', '')}</td>
#                     <td>{record.get('create_date', '')}</td>
#                     <td>{record.get('id', '')}</td>
#                     <td>{record.get('mail_count', 0)}</td>
#                     <td>{'是' if record.get('has_unprocessed_mail', False) else '否'}</td>
#                     <td>{'需要人工介入' if record.get('need_manual_intervention', False) else '正常'}</td>
#                 </tr>
#         """
#
#     html_content += """
#             </tbody>
#         </table>
#     </body>
#     </html>
#     """
#
#     # 保存HTML文件
#     filename = f"yaji_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
#     with open(filename, 'w', encoding='utf-8') as f:
#         f.write(html_content)
#
#     print(f"HTML报表已生成: {filename}")
#     return filename


# Message:
#     Tip1：通过接口的形式来探测回传结果
#     Tip2：通过页面度数元素  （尽量少用 不得已而为之，因为这样的方式会破坏稳定性）
#     Tip3：将两种技术方案结合 双重验证 只要有一个符合情况即判定为通过校验
#     长时间监控 每次启动重启要进行逻辑的处理
def rpapage():
    co = ChromiumOptions()
    # co = ChromiumOptions().headless()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)
    page.get('https://www.yagikoifish.com/vms/index.html#/login?redirect=%2F')
    logger.info('第一次cookie状态检测')
    # cookiea = page.cookies(as_dict=True)  xpath://*[@id="cvf-page-content"]/div/div/div/div[2]/div/img
    cookiea = page.cookies()
    dictionary = {cookie['name']: cookie['value'] for cookie in cookiea}
    cookiea = dictionary
    logger.info(cookiea)
    logger.info('登录标识状态A')
    logger.info(cookiea.get('vue_admin_template_token'))
    if cookiea.get('vue_admin_template_token') is None:
        page.ele('xpath://*[@id="app"]/span/div[1]/form/div[2]/div/div/input').input('YIBAO123')
        randomSleep()
        page.ele('xpath://*[@id="app"]/span/div[1]/form/div[3]/div/div/input').input('Y123456')
        randomSleep()
        # 这个按钮标签为了稳定安全考虑 后续更换为点控式按钮
        page.ele('xpath://*[@id="app"]/span/div[1]/form/button').click()
        randomSleep()
    logger.info('第二次cookie状态检测')
    cookieb = page.cookies()
    dictionary = {cookie['name']: cookie['value'] for cookie in cookieb}
    cookieb = dictionary
    logger.info(cookieb)
    logger.info('登录标识状态B  ')
    logger.info(cookieb.get('vue_admin_template_token'))
    # 此段逻辑针对特殊验证码 ， 在一些极端情况会出现 要予以解决 https://www.yagikoifish.com/vms/fbaApply/v/getList4Page
    # 极端情况下的验证码情况需要处理的逻辑
    # ele = page.ele(rpacapture('location','验证码图片位置'),timeout=3)

    cookie_str = "; ".join([f"{key}={value}" for key, value in cookieb.items()])
    print(cookie_str)
    print(99999)
    print(cookieb.get('vue_admin_template_token').replace('%20', ' '))
    headers = {
        "authorization": cookieb.get('vue_admin_template_token').replace('%20', ' ')}
    payload = {
        "pageNo": 1,
        "pageSize": 100000,
        "cdsBookingNo": "FBE"
    }
    # searchBookingDetailsByFilter   指令5的数据状态接口
    response = requests.post("https://www.yagikoifish.com/vms/fbaApply/v/getList4Page", params=payload,
                             headers=headers)
    # thejson = json.loads(response.text)
    # status = thejson.get('status')
    # data = thejson.get('data')
    # print( status)
    # print( data)

    thejson = json.loads(response.text)
    response_msg = thejson.get('msg')
    response_status = thejson.get('status')
    data = thejson.get('data')

    print(f"API响应消息: {response_msg}")
    print(f"API响应状态: {response_status}")

    # 用于生成HTML报表的数据
    report_data = []

    if data:
        total_records = data.get('total')
        current_page = data.get('current')
        page_size = data.get('size')
        total_pages = data.get('pages')

        print(f"总记录数: {total_records}")
        print(f"当前页: {current_page}/{total_pages}")
        print(f"本页记录数: {page_size}")

        records = data.get('records', [])
        print(f"\n解析到 {len(records)} 条记录:")

        for record in records:
            booking_no = record.get('cdsBookingNo')
            status_code = record.get('status')
            submit_status = record.get('submitStatusStr')
            creater = record.get('creater')
            create_date = record.get('createDate')
            id = record.get('id')
            print(f"  订舱号: {booking_no}, 状态: {submit_status}, 创建人: {creater}, 创建时间: {create_date},ID: {id}")

            # 调用查询邮件列表接口
            mail_count = 0
            has_unprocessed_mail = False
            need_manual_intervention = False

            if id:
                mail_response = requests.post(
                    f"https://www.yagikoifish.com/vms/fbaMail/getListByRelApplyId?relApplyFileId={id}",
                    headers=headers
                )

                try:
                    mail_data = json.loads(mail_response.text)
                    mail_msg = mail_data.get('msg')
                    mail_status = mail_data.get('status')
                    mail_records = mail_data.get('data', [])

                    print(f"    邮件查询结果: {mail_msg}, 状态: {mail_status}")
                    if mail_records:
                        mail_count = len(mail_records)
                        print(f"    邮件数量: {mail_count}")
                        # 检查是否有状态为"未处理"的邮件
                        for mail in mail_records:
                            mail_title = mail.get('title', '无标题')
                            mail_create_date = mail.get('createDate', '未知时间')
                            mail_status_str = mail.get('statusStr', '')  # 获取邮件状态
                            print(f"      邮件: {mail_title}, 创建时间: {mail_create_date}")
                            # 检查是否有邮件状态为"未处理"
                            if mail_status_str == "未处理":
                                has_unprocessed_mail = True
                                need_manual_intervention = True
                                # 如果有任何邮件状态为"未处理"，则打印"人工介入"
                        if need_manual_intervention:
                            print("人工介入")
                    else:
                        print("    无相关邮件")
                except Exception as e:
                    print(f"    邮件查询解析失败: {e}")

            # 收集报表数据
            report_data.append({
                'booking_no': booking_no,
                'submit_status': submit_status,
                'creater': creater,
                'create_date': create_date,
                'id': id,
                'mail_count': mail_count,
                'has_unprocessed_mail': has_unprocessed_mail,
                'need_manual_intervention': need_manual_intervention
            })

        # 魁得利 框架    https://www.yagikoifish.com/vms/fbaMail/getListByRelApplyId?relApplyFileId=27566

        # 生成HTML报表
        report_file = generate_html_report(report_data)
        print(f"\n报表已生成: {report_file}")

    return page, cookie_str


if __name__ == '__main__':
    page, cookie_str = rpapage()

# 亚马逊的这个RPA  可以在每次任务开始和结束的时候探测下其状态存活的情况

# def establish_connection():
#
#
#     msg,msg_count = get_release_messages(channel)
#     if(msg == '' or msg_count == -1 or msg_count is None):
#         #logger.info("没有消息")
#         return
#     # 在此处开始编写您的应用
#     if (msg != '' and msg_count != -1 and msg_count is not None):
#         # 只有有数据的时候才做浏览器数据的初始化
#         try:
#             # 先进行浏览器初始化操作 ，确保基本的登录不存在问题
#             page,cookie_str= rpapage()
#             page.wait(3)
#         except Exception as pex:
#             logger.info("RPA登陆页面异常：{}".format(pex))
#             callback_error(msg, "RPA执行异常：{}".format(pex))
#             time.sleep(3)
#             return
