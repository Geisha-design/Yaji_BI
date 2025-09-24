"""
网页客户端，用于登录和数据抓取
"""
import concurrent
import json
import requests
from loguru import logger
from DrissionPage import WebPage, ChromiumOptions, SessionOptions
from utils.helpers import thread_safe_print, random_sleep
from scraper.web_parser import fetch_detailed_list_data, fetch_mail_data, generate_html_report


def rpapage():
    """
    带界面的网页登录和数据抓取
    """
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
        random_sleep()
        page.ele('xpath://*[@id="app"]/span/div[1]/form/div[3]/div/div/input').input('Y123456')
        random_sleep()
        # 这个按钮标签为了稳定安全考虑 后续更换为点控式按钮
        page.ele('xpath://*[@id="app"]/span/div[1]/form/button').click()
        random_sleep()
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
    thread_safe_print(cookie_str)
    thread_safe_print(99999)
    thread_safe_print(cookieb.get('vue_admin_template_token').replace('%20', ' '))
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

    thread_safe_print(f"API响应消息: {response_msg}")
    thread_safe_print(f"API响应状态: {response_status}")

    # 用于生成HTML报表的数据
    report_data = []

    if data:
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
            booking_no = record.get('cdsBookingNo')
            status_code = record.get('status')
            submit_status = record.get('submitStatusStr')
            creater = record.get('creater')
            create_date = record.get('createDate')
            id = record.get('id')
            thread_safe_print(
                f"  订舱号: {booking_no}, 状态: {submit_status}, 创建人: {creater}, 创建时间: {create_date},ID: {id}")

            if id:
                records_to_process.append({
                    'booking_no': booking_no,
                    'submit_status': submit_status,
                    'creater': creater,
                    'create_date': create_date,
                    'id': id,
                    'record_data': record
                })

        # 使用多线程批量处理邮件查询
        mail_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务
            future_to_id = {
                executor.submit(fetch_mail_data, record['id'], headers): record
                for record in records_to_process
            }

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_id):
                record = future_to_id[future]
                try:
                    result = future.result()
                    mail_results[result['id']] = result
                except Exception as exc:
                    thread_safe_print(f"ID {record['id']} 生成异常: {exc}")
                    mail_results[record['id']] = {
                        'id': record['id'],
                        'mail_count': 0,
                        'has_unprocessed_mail': False,
                        'need_manual_intervention': False,
                        'error': str(exc)
                    }

        # 整理最终报表数据
        for record in records_to_process:
            record_id = record['id']
            mail_result = mail_results.get(record_id, {})

            # 收集报表数据
            report_data.append({
                'booking_no': record['booking_no'],
                'submit_status': record['submit_status'],
                'creater': record['creater'],
                'create_date': record['create_date'],
                'id': record['id'],
                'mail_count': mail_result.get('mail_count', 0),
                'has_unprocessed_mail': mail_result.get('has_unprocessed_mail', False),
                'need_manual_intervention': mail_result.get('need_manual_intervention', False)
            })

        # 魁得利 框架    https://www.yagikoifish.com/vms/fbaMail/getListByRelApplyId?relApplyFileId=27566

        # 生成HTML报表
        report_file = generate_html_report(report_data)
        thread_safe_print(f"\n报表已生成: {report_file}")

    return page, cookie_str


def rpapageshadow():
    """
    无界面的网页登录和数据抓取
    """
    # co = ChromiumOptions()
    co = ChromiumOptions().headless()
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
        random_sleep()
        page.ele('xpath://*[@id="app"]/span/div[1]/form/div[3]/div/div/input').input('Y123456')
        random_sleep()
        # 这个按钮标签为了稳定安全考虑 后续更换为点控式按钮
        page.ele('xpath://*[@id="app"]/span/div[1]/form/button').click()
        random_sleep()
    logger.info('第二次cookie状态检测')
    cookieb = page.cookies()
    dictionary = {cookie['name']: cookie['value'] for cookie in cookieb}
    cookieb = dictionary
    logger.info(cookieb)
    logger.info('登录标识状态B  ')
    logger.info(cookieb.get('vue_admin_template_token'))
    cookie_str = cookieb.get('vue_admin_template_token').replace('%20', ' ')
    return page, cookie_str