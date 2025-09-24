"""
项目主入口文件
"""
from scraper.web_client import rpapageshadow
from database.table_manager import create_main_table, create_main_table_fba, create_email_table
from database.data_manager import parse_and_store_main_data, parse_and_store_main_data_fba, parse_and_store_email_data
from reports.generator import query_alo_and_booking_mapping
from reports.email_sender import send_combined_report_with_attachments_and_excel
import requests
import json
import time
from utils.helpers import thread_safe_print


def fetch_main_data_fbe(headers):
    """
    获取FBE主数据并存储
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

        if data:
            parse_and_store_main_data(data, response_msg)
            total_records = data.get('total')
            current_page = data.get('current')
            page_size = data.get('size')
            total_pages = data.get('pages')

            thread_safe_print(f"总记录数: {total_records}")
            thread_safe_print(f"当前页: {current_page}/{total_pages}")
            thread_safe_print(f"本页记录数: {page_size}")

            records = data.get('records', [])
            thread_safe_print(f"\n解析到 {len(records)} 条记录:")

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


def fetch_main_data_fba(headers):
    """
    获取FBA主数据并存储
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

        if data:
            parse_and_store_main_data_fba(data, response_msg)
            total_records = data.get('total')
            current_page = data.get('current')
            page_size = data.get('size')
            total_pages = data.get('pages')

            thread_safe_print(f"总记录数: {total_records}")
            thread_safe_print(f"当前页: {current_page}/{total_pages}")
            thread_safe_print(f"本页记录数: {page_size}")

            records = data.get('records', [])
            thread_safe_print(f"\n解析到 {len(records)} 条记录:")

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


def fetch_email_data(headers):
    """
    获取邮件数据并存储
    """
    url = "https://www.yagikoifish.com/vms/fbaMail/v/getList4Page"
    params = {
        "pageNo": 1,
        "pageSize": 200
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=50)
        data = json.loads(response.text)

        # 解析并存储数据到MySQL
        parse_and_store_email_data(data)

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
                f"接收时间: {record.get('receivedTime')}"
            )

        return data
    except Exception as e:
        thread_safe_print(f"获取详细列表数据失败: {e}")
        return None


def main():
    """
    主函数
    """
    # 首先创建主要信息表
    create_main_table()
    create_main_table_fba()
    create_email_table()
    
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
        data = fetch_main_data_fbe(headers)

        if data and data.get('data'):
            total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)

    # 获取FBA数据
    page_no = 1
    total_pages = 1

    while page_no <= total_pages:
        thread_safe_print(f"正在获取第 {page_no} 页FBA数据...")
        data = fetch_main_data_fba(headers)

        if data and data.get('data'):
            total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)

    # 获取邮件数据
    page_no = 1
    page_size = 200
    total_pages = 5

    while page_no <= total_pages:
        thread_safe_print(f"正在获取第 {page_no} 页邮件数据...")
        data = fetch_email_data(headers)

        if data and data.get('data'):
            # total_pages = data['data'].get('pages', 1)
            thread_safe_print(f"总共 {total_pages} 页")

        page_no += 1

        # 添加延迟避免请求过于频繁
        time.sleep(1)

    # 查询ALO与Booking的映射关系
    alo_booking_data = query_alo_and_booking_mapping()

    # 准备报表数据
    report_data = {
        'alo_booking': alo_booking_data,
        # 可以添加更多报表数据
    }

    # 发送综合报表邮件（包含HTML和Excel附件）
    recipients = ['qiyz@smartebao.com',
        'luye@smartebao.com',
        'zhuke@smartebao.com',
        'wangk@smartebao.com',
        'xumy@smartebao.com']  # 收件人列表
    send_combined_report_with_attachments_and_excel(recipients, report_data)


if __name__ == '__main__':
    main()