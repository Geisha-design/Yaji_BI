from yaji_obsidian import *

import sqlite3
from datetime import datetime
import sqlite3
from datetime import datetime


def parse_and_store_email_data(data, db_path="yaji_email_data.db"):
    """
    解析邮件API返回的数据并存储到数据库
    """
    if not data or data.get('status') != 'success':
        thread_safe_print("邮件数据获取失败或状态不正确")
        return

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建邮件表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_records (
            id INTEGER PRIMARY KEY,
            message_id TEXT,
            from_addresses TEXT,
            content TEXT,
            content_text TEXT,
            received_time TEXT,
            status TEXT,
            mail_addr TEXT,
            rel_fba_apply_id INTEGER,
            subject TEXT,
            status_str TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 解析并插入数据
    records = data.get('data', {}).get('records', [])
    thread_safe_print(f"准备处理 {len(records)} 条邮件记录")

    for record in records:
        # 提取字段并处理None值
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
            record.get('statusStr')
        )

        # 使用INSERT OR REPLACE避免重复记录
        cursor.execute('''
            INSERT OR REPLACE INTO email_records (
                id, message_id, from_addresses, content, content_text,
                received_time, status, mail_addr, rel_fba_apply_id, subject, status_str
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)

    # 提交事务并关闭连接
    conn.commit()
    conn.close()

    thread_safe_print(f"成功存储 {len(records)} 条邮件记录到数据库 {db_path}")


# 修改 fetch_detailed_list_data 函数以支持数据存储
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
        response = requests.post(url, params=params, headers=headers, timeout=30)
        data = json.loads(response.text)

        # 解析并存储数据
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


# 在主函数中调用
if __name__ == '__main__':
    page, cookie_str = rpapageshadow()
    headers = {
        "authorization": cookie_str
    }

    # 获取所有数据（分页处理）
    page_no = 1
    page_size = 100  # 增大页面大小以减少请求次数
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






