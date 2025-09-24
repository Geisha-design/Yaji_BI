
import json
import time
import requests
from loguru import logger
from DrissionPage import WebPage, ChromiumOptions, SessionOptions
import random


def randomSleep():
    # 设置随机休眠时间，范围从min_seconds到max_seconds，整数秒
    min_seconds = 1
    max_seconds = 3
    # 生成一个随机整数，表示休眠的时间（秒）
    sleep_time = random.randint(min_seconds, max_seconds)
    print(f"Randomly selected sleep time: {sleep_time} seconds")
    # 让程序休眠这个随机时间
    time.sleep(sleep_time)

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
    #cookiea = page.cookies(as_dict=True)  xpath://*[@id="cvf-page-content"]/div/div/div/div[2]/div/img
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
    print(cookieb.get('vue_admin_template_token').replace('%20',' '))
    headers = {
               "authorization": cookieb.get('vue_admin_template_token').replace('%20',' ')}
    payload = {
 "pageNo":1,
 "pageSize":100000,
        "cdsBookingNo":"FBE"
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
                        print(f"    邮件数量: {len(mail_records)}")
                        # 检查是否有状态为"未处理"的邮件
                        need_manual_intervention = False
                        for mail in mail_records:
                            mail_title = mail.get('title', '无标题')
                            mail_create_date = mail.get('createDate', '未知时间')
                            mail_status_str = mail.get('statusStr', '')  # 获取邮件状态
                            print(f"      邮件: {mail_title}, 创建时间: {mail_create_date}")
                            # 检查是否有邮件状态为"未处理"
                            if mail_status_str == "未处理":
                                need_manual_intervention = True
                                # 如果有任何邮件状态为"未处理"，则打印"人工介入"
                        if need_manual_intervention:
                            print("人工介入")
                    else:
                        print("    无相关邮件")
                except Exception as e:
                    print(f"    邮件查询解析失败: {e}")

        # 魁得利 框架    https://www.yagikoifish.com/vms/fbaMail/getListByRelApplyId?relApplyFileId=27566



    return page,cookie_str
if __name__ == '__main__':
    page,cookie_str = rpapage()


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
