from DrissionPage import WebPage, ChromiumOptions, SessionOptions
from AOSCCOCR import *
import AOSCCOCR
import json
import time
import requests
from loguru import logger
from rpacapture import *

company_name = baseConfig('config','company_name')
ebao_mq_ip = baseConfig('config','mq_ip')
ebao_mq_vhost = baseConfig('config','mq_vhost')
ebao_mq_port = baseConfig('config','mq_port')
mq_queue_name = baseConfig('config','queue_name')
ebao_mq_user = baseConfig('config','mq_user')
ebao_mq_password = baseConfig('config','mq_password')
theheadless = baseConfig('config','headless')
ebao_url_ip = baseConfig('config','oit_url_ip')


def timestampTool(timestamp_ms):
    from datetime import datetime
    # 假设时间戳是以毫秒为单位
    # timestamp_ms = 1731731909051
    # 将毫秒转换为秒
    timestamp_s = timestamp_ms / 1000.0
    # 转换为datetime对象
    dt_object = str(datetime.fromtimestamp(timestamp_s))
    print(dt_object)
    return dt_object

# 亚马逊的这个RPA  可以在每次任务开始和结束的时候探测下其状态存活的情况

def establish_connection():
    ebao_mq_ip = baseConfig('config', 'mq_ip')
    ebao_mq_vhost = baseConfig('config', 'mq_vhost')
    ebao_mq_port = baseConfig('config', 'mq_port')
    ebao_mq_user = baseConfig('config', 'mq_user')
    ebao_mq_password = baseConfig('config', 'mq_password')

    # ########################## consumer ##########################
    credentials = pika.PlainCredentials(ebao_mq_user, ebao_mq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(ebao_mq_ip, ebao_mq_port, ebao_mq_vhost, credentials))
    channel = connection.channel()

    msg,msg_count = get_release_messages(channel)
    if(msg == '' or msg_count == -1 or msg_count is None):
        #logger.info("没有消息")
        return
    # 在此处开始编写您的应用
    if (msg != '' and msg_count != -1 and msg_count is not None):
        # 只有有数据的时候才做浏览器数据的初始化
        try:
            # 先进行浏览器初始化操作 ，确保基本的登录不存在问题
            page,cookie_str= rpapage()
            page.wait(3)
        except Exception as pex:
            logger.info("RPA登陆页面异常：{}".format(pex))
            callback_error(msg, "RPA执行异常：{}".format(pex))
            time.sleep(3)
            return
    """
    这里根据获得的指令项运行对应的逻辑段
    """
    while (msg != ''and msg_count != -1 and msg_count is not None):
        result = json.loads(msg)
        msgType = result["msgType"]
        logger.info('输出测试时期的识别标记')
        logger.info(msgType)
        if (msgType == 1):
            time.sleep(3)
            # 就是浅层的数据检索


            orderone(page,msg,cookie_str,channel)



            # send_alarm_msg(str(e))


            # do_pay_confirm(page, msg)
        elif (msgType == 2):
            time.sleep(3)
            ordertwo(page,msg,cookie_str,channel)
        elif (msgType == 3):
            time.sleep(3)
            orderthree(page,msg,cookie_str,channel)
        elif (msgType == 4):
            time.sleep(3)
            orderfour(page,msg,cookie_str,channel)
            # do_query_order_detail(page, msg)
        elif(msgType == 5):
            orderfive(page,msg,cookie_str,channel)
            pass
        msg, msg_count = get_release_messages(channel)
        time.sleep(2)

# Message:
#     Tip1：通过接口的形式来探测回传结果
#     Tip2：通过页面度数元素  （尽量少用 不得已而为之，因为这样的方式会破坏稳定性）
#     Tip3：将两种技术方案结合 双重验证 只要有一个符合情况即判定为通过校验
#     长时间监控 每次启动重启要进行逻辑的处理
def rpapage():
    theheadless = str(baseConfig('config','headless'))
    if theheadless == 'false' or theheadless=='False':
        co = ChromiumOptions()
    else:
        co = ChromiumOptions().headless()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)
    if theheadless == 'false' or theheadless=='False' :
        logger.info("进入目标网址(有头模式)"+"https://xb-node.amazon.cn/")
    else:
        logger.info("进入目标网址(无头模式)"+"https://xb-node.amazon.cn/")
    page.get('https://xb-node.amazon.cn/')
    logger.info('第一次cookie状态检测')
    #cookiea = page.cookies(as_dict=True)
    cookiea = page.cookies()
    dictionary = {cookie['name']: cookie['value'] for cookie in cookiea}
    cookiea = dictionary
    logger.info(cookiea)
    logger.info('登录标识状态A')
    logger.info(cookiea.get('sess-at-main'))
    if cookiea.get('sess-at-main') is None:
        page.ele(rpacapture('location','账号')).input(baseConfig('config','username'))
        randomSleep()
        page.ele(rpacapture('location','密码')).input(baseConfig('config','password'))
        randomSleep()
        # 这个按钮标签为了稳定安全考虑 后续更换为点控式按钮
        page.ele(rpacapture('location','登录')).click()
        randomSleep()
    logger.info('第二次cookie状态检测')
    cookieb = page.cookies()
    dictionary = {cookie['name']: cookie['value'] for cookie in cookieb}
    cookieb = dictionary
    logger.info(cookieb)
    logger.info('登录标识状态B  ')
    logger.info(cookieb.get('sess-at-main'))
    # 此段逻辑针对特殊验证码 ， 在一些极端情况会出现 要予以解决
    # 极端情况下的验证码情况需要处理的逻辑
    ele = page.ele(rpacapture('location','验证码图片位置'),timeout=3)
    # 出现极端情况的OCR识别工具
    if ele:
        page.ele(rpacapture('location','验证码图片位置')).get_screenshot('thescreen.png')
        # OCR识别模块
        with open("thescreen.png", 'rb') as f:
            img_bytes = f.read()
        ocr = AOSCCOCR.AosccOcr()
        poses = ocr.classification(img_bytes)
        logger.info(poses)
        page.ele(rpacapture('location','验证码文字输入框')).input(poses)
        page.wait(2)
        page.ele(rpacapture('location','验证码确认')).click()
        ele2 = page.ele(rpacapture('location','验证码通过标识'),timeout=3)
        while ele2:
            ele2 = page.ele(rpacapture('location','验证码通过标识'), timeout=3)
            ele2.click()
            page.ele(rpacapture('location','验证码图片位置')).get_screenshot('thescreen.png')
            randomSleep()
            # OCR识别模块
            with open("thescreen.png", 'rb') as f:
                img_bytes = f.read()
            ocr = SmartebaoRPA.AOSCCOCR.AosccOcr()
            poses = ocr.classification(img_bytes)
            logger.info(poses)
            page.ele(rpacapture('location','验证码文字输入框')).input(poses)
            page.wait(2)
            page.ele(rpacapture('location','验证码确认')).click()
            randomSleep()
            ele2 = page.ele(rpacapture('location','验证码通过标识'), timeout=3)

    cookie_str = "; ".join([f"{key}={value}" for key, value in cookieb.items()])
    print(cookie_str)
    return page,cookie_str

"""
一号指令逻辑 获取理货异常信息
"""
def orderone(page,msg,cookie_str,channel):

    try:
        logger.info("开始处理理货异常信息")
        workOrderNo = json.loads(msg).get('workOrderNo')
        headers = {"Cookie": cookie_str}
        payload = {"referenceId": workOrderNo}
        # payload = {"referenceId": "AL2411150053"}
        response = requests.get("https://xb-node.amazon.cn/glenn/pr/ajax/getPRHeaderByCheckInCode", params=payload,
                                headers=headers)
        thejson = json.loads(response.text)
        status = thejson.get('status')
        data = thejson.get('data')
        # {"status": "SUCCESS", "data": null}
        prIds = None
        if (status == "SUCCESS" and data is not None):
            logger.info("数据不为空,进行处理")
            logger.info(data)
            prIds = data['prId']
            logger.info(prIds)
        else:
            logger.info("数据为空,不进行处理")
        dataerror = None
        # 通过PR时间是否为空也可以判断是否需要进行修复  这样就可以在客户要求和页面上进行双重保险了 然后任务之间要设置不要的延时设置
        if (prIds is not None):
            headers = {"Cookie": cookie_str}
            payload = {"resourceId": prIds}
            response = requests.get("https://xb-node.amazon.cn/glenn/ajax/event/getRecords", params=payload,
                                    headers=headers)
            thejson = json.loads(response.text)
            status = thejson.get('status')
            dataerror = thejson.get('data')

            if (status == "SUCCESS" and dataerror is not None):
                # 进行一下时间戳转换
                thesize = len(dataerror)
                text_detail = ""
                if(thesize>=1):
                    creationTime = dataerror[thesize-1].get('creationTime')
                    # 异常描述时间
                    if (creationTime is not None):
                        creationTime = timestampTool(creationTime)
                    contentRecordList = dataerror[thesize-1].get('contentRecordList')
                    logger.info(contentRecordList)
                    for record in contentRecordList:
                        if record['contentType'] == 'TEXT':
                            text_detail = record['detail']
                            logger.info(text_detail)
                            break
                main_card_msg ={
                        "abnormalDesc": text_detail,
                        "abnormalTime": creationTime,
                        "msgId": json.loads(msg).get('msgId'),
                        "msgType": 1,
                        "resultCode": 0,
                        "resultMsg": "成功",
                        "timestamp":   json.loads(msg).get('timestamp'),
                        "workOrderNo":  json.loads(msg).get('workOrderNo')
                    }

                # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
                # logger.info("输出异常事件回传消息")

                logger.info(main_card_msg)

                channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
                channel.basic_publish(
                    exchange='',
                    routing_key="q_rpa_to_ebao_yagi",
                    body=json.dumps(main_card_msg, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 使消息持久化
                    ))
            else:
                # logger.info("错误数据为空,不进行处理")
                main_card_msg = {
                    "abnormalDesc": '',
                    "abnormalTime": '',
                    "msgId": json.loads(msg).get('msgId'),
                    "msgType": 1,
                    "resultCode": 1,
                    "resultMsg": "失败",
                    "timestamp": json.loads(msg).get('timestamp'),
                    "workOrderNo": json.loads(msg).get('workOrderNo')
                }

                # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
                logger.info(main_card_msg)

                channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
                channel.basic_publish(
                    exchange='',
                    routing_key="q_rpa_to_ebao_yagi",
                    body=json.dumps(main_card_msg, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 使消息持久化
                    ))
    except Exception as e:
        # send_alarm_msg("获取理货信息异常，编号为"+str(json.loads(msg).get('workOrderNo')))
        pass


    pass

"""
二号指令逻辑 修复PR

下发指令

{
    "msgId": "875eef4a-b3bf-4f1e-93f3-88f954b43197",
    "msgType": 1,
    "timestamp": 1731048898362,
    "workOrderNo": "AL2411060074"
}

"""
def ordertwo(page,msg,cookie_str,channel):

    try:
        logger.info("开始处理修复PR异常")

        headers = {"Cookie": cookie_str}
        workOrderNo = json.loads(msg).get('workOrderNo')
        payload = {"referenceId": workOrderNo}
        response = requests.get("https://xb-node.amazon.cn/glenn/pr/ajax/getPRHeaderByCheckInCode", params=payload,
                                headers=headers)
        thejson = json.loads(response.text)
        status = thejson.get('status')
        data = thejson.get('data')
        # {"status": "SUCCESS", "data": null}
        prIds = None
        if (status == "SUCCESS" and data is not None):
            logger.info("数据不为空,进行处理")
            logger.info(data)
            prIds = data['prId']
            logger.info(prIds)
        else:
            logger.info("数据为空,不进行处理")

        dataerror = None
        # 通过PR时间是否为空也可以判断是否需要进行修复  这样就可以在客户要求和页面上进行双重保险了 然后任务之间要设置不要的延时设置
        if (prIds is not None):
            headers = {"Cookie": cookie_str}
            payload = {"resourceId": prIds}
            response = requests.get("https://xb-node.amazon.cn/glenn/ajax/event/getRecords", params=payload,
                                    headers=headers)
            thejson = json.loads(response.text)
            status = thejson.get('status')
            dataerror = thejson.get('data')
            if (status == "SUCCESS" and dataerror is not None):
                logger.info("错误数据不为空,进行处理")
                logger.info(data)
            else:
                logger.info("错误数据为空,不进行处理")

        # makeErroe按钮的点击
        # /html/body/div[3]/div/main/div/div[1]/div[3]/div/div[1]/div[4]/div[2]/span[1]/span/span/input
        if (prIds is not None and dataerror is not None):
            payload = {
                "clientReferenceId": prIds,
                "eventType": "FIX_PR"
            }
            # markError
            response = requests.post("https://xb-node.amazon.cn/glenn/problemSolving/ajax/markError", json=payload,
                                     headers=headers)
            thejson = json.loads(response.text)
            status = thejson.get('status')
            data = thejson.get('data')
            if (status == "SUCCESS" and data is not None):
                logger.info("makeError接口触发成功 执行后续步骤 ")
                logger.info(data)
            else:
                logger.info("makeError接口触发失败")

        if (prIds is not None and dataerror is not None):
            payload = {
                "prId": prIds,
                "properties": {
                    "problematic": "false"
                }
            }
            # markError
            response = requests.post("https://xb-node.amazon.cn/glenn/pr/ajax/updatePR", json=payload,
                                     headers=headers)
            thejson = json.loads(response.text)
            status = thejson.get('status')
            data = thejson.get('data')

            if (status == "SUCCESS" and data is not None):
                logger.info("updatePR接口触发成功 执行后续步骤 ")
                logger.info(data)

                main_card_msg = {
                    "msgId": json.loads(msg).get('msgId'),
                    "msgType": 2,
                    "resultCode": 0,
                    "resultMsg": "成功",
                    "timestamp": json.loads(msg).get('timestamp'),
                    "workOrderNo": json.loads(msg).get('workOrderNo')
                }

                # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
                logger.info(main_card_msg)
                channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
                channel.basic_publish(
                    exchange='',
                    routing_key="q_rpa_to_ebao_yagi",
                    body=json.dumps(main_card_msg, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 使消息持久化
                    ))


            else:
                logger.info("updatePR接口触发失败")

                main_card_msg = {
                    "msgId": json.loads(msg).get('msgId'),
                    "msgType": 2,
                    "resultCode": 1,
                    "resultMsg": "失败",
                    "timestamp": json.loads(msg).get('timestamp'),
                    "workOrderNo": json.loads(msg).get('workOrderNo')
                }

                # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
                logger.info(main_card_msg)
                channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
                channel.basic_publish(
                    exchange='',
                    routing_key="q_rpa_to_ebao_yagi",
                    body=json.dumps(main_card_msg, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 使消息持久化
                    ))
    except Exception as e:
        send_alarm_msg("处理理货异常信息异常，编号为"+str(json.loads(msg).get('workOrderNo')))
        pass



"""
三号指令逻辑  卸货完成 
"""
def orderthree(page,msg,cookie_str,channel):

    try:
        logger.info("开始处理卸货完成信息")
        headers = {"Cookie": cookie_str}
        workOrderNo = json.loads(msg).get('workOrderNo')
        payload = {"referenceId": workOrderNo}
        response = requests.get("https://xb-node.amazon.cn/glenn/pr/ajax/getPRHeaderByCheckInCode", params=payload,
                                headers=headers)
        # logger.info(response.status_code)
        # logger.info(response.encoding)
        # logger.info(response.url)
        # logger.info(response.text)
        thejson = json.loads(response.text)
        status = thejson.get('status')
        data = thejson.get('data')
        if(data is not None):
            unloadCompletedDate = data.get('unloadCompletedDate')
            if (unloadCompletedDate is not None):
                unloadCompletedDate = timestampTool(unloadCompletedDate)
        # {"status": "SUCCESS", "data": null}
        prIds = None
        if (status == "SUCCESS" and data is not None):
            logger.info("数据不为空,进行处理")
            logger.info(data)
            prIds = data['prId']
            logger.info(prIds)

            main_card_msg = {
                "msgId": json.loads(msg).get('msgId'),
                "msgType": 3,
                "resultCode": 0,
                "resultMsg": "成功",
                "timestamp": json.loads(msg).get('timestamp'),
                "workOrderNo": json.loads(msg).get('workOrderNo'),
                "unloadingTime": unloadCompletedDate
            }
            # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
            logger.info(main_card_msg)

            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key="q_rpa_to_ebao_yagi",
                body=json.dumps(main_card_msg, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 使消息持久化
                ))
        else:
            logger.info("数据为空,不进行处理")

            main_card_msg = {
                "msgId": json.loads(msg).get('msgId'),
                "unloadingTime":"",
                "msgType": 3,
                "resultCode": 1,
                "resultMsg": "失败",
                "timestamp": json.loads(msg).get('timestamp'),
                "workOrderNo": json.loads(msg).get('workOrderNo')
            }

            # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
            logger.info(main_card_msg)

            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key="q_rpa_to_ebao_yagi",
                body=json.dumps(main_card_msg, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 使消息持久化
                ))
    except Exception as e:
        # send_alarm_msg("获取卸货完成指令异常，编号为"+str(json.loads(msg).get('workOrderNo')))
        pass



"""
四号指令逻辑  ALO 完成 最终的  ALO  确认只会确认最后一笔 但是pr确认是列表中的每一都要处理
"""
def orderfour(page,msg,cookie_str,channel):
    try:
        logger.info("开始处理ALO完成信息")
        workOrderNos = json.loads(msg).get('workOrderNos')
        if(len(workOrderNos) > 0):
            # workOrderNositem = workOrderNos[0]
            # print(workOrderNositem)
            for i in range(0,len(workOrderNos)):
                workOrderNositem = workOrderNos[i]
                print(workOrderNositem)
                headers = {"Cookie": cookie_str}
                # payload = {"referenceId": "AL2411200055"}
                payload = {"referenceId": workOrderNositem}
                response = requests.get("https://xb-node.amazon.cn/glenn/pr/ajax/getPRHeaderByCheckInCode", params=payload,
                                        headers=headers)

                thejson = json.loads(response.text)
                status = thejson.get('status')
                data = thejson.get('data')
                # {"status": "SUCCESS", "data": null}
                prIds = None
                if (status == "SUCCESS" and data is not None):
                    logger.info("数据不为空,进行处理")
                    logger.info(data)
                    prIds = data['prId']
                    logger.info(prIds)
                else:
                    logger.info("数据为空,不进行处理")
                    # 关于票据详情的获取  保证获取内部PrID 号才是后续逻辑执行的前提
                if (prIds is not None):
                    headers = {"Cookie": cookie_str}
                    payload = {
                        "filter": {
                            "prIds": [
                                prIds
                            ]
                        }
                    }
                    response = requests.post(
                        "https://xb-node.amazon.cn/glenn/booking/ajax/searchBookingDetailsByFilter",
                        json=payload,
                        headers=headers)

                    thejson = json.loads(response.text)
                    status = thejson.get('status')
                    data = thejson.get('data')
                    bookingDetails = data.get('bookingDetails')[0]
                    bookingHeader = bookingDetails.get('bookingHeader')
                    bookingReference = bookingHeader.get('bookingReference')
                    bookingReference_id = bookingReference.get('id')
                    logger.info("输出内层的特殊id")
                    logger.info(bookingReference_id)
                    # 完成PR点击动作
                    if (prIds is not None):
                        headers = {"Cookie": cookie_str}
                        payload = {"prId": prIds}
                        response = requests.post("https://xb-node.amazon.cn/glenn/pr/ajax/completePR", json=payload,
                                                 headers=headers)


                        thejson = json.loads(response.text)
                        status = thejson.get('status')
                        data = thejson.get('data')

                        if (status == "SUCCESS" and data is not None):
                            logger.info("完成PR 按钮点击成功 执行后续步骤 ")
                            logger.info(data)
                            prIds = data['prId']
                            logger.info(prIds)
                        else:
                            logger.info("点击失败")

                    # 完成预定点击动作  这个只有字符串的最后一个编号才会执行确认
                    if (prIds is not None and i == len(workOrderNos)-1):
                        headers = {"Cookie": cookie_str}
                        payload = {
                            "id": bookingReference_id,
                            "type": "FBA_BOOKING"}
                        response = requests.post("https://xb-node.amazon.cn/glenn/booking/ajax/completeBooking",
                                                 json=payload,
                                                 headers=headers)


                        thejson = json.loads(response.text)
                        status = thejson.get('status')
                        data = thejson.get('data')

                        if (status == "SUCCESS" and data is not None):
                            logger.info("完成PR 按钮点击成功 执行后续步骤 ")
                            logger.info(data)
                            logger.info("错误数据为空,不进行处理")
                            main_card_msg = {
                                "msgId": json.loads(msg).get('msgId'),
                                "msgType": 4,
                                "resultCode": 0,
                                "resultMsg": "成功",
                                "timestamp": json.loads(msg).get('timestamp'),
                                "workOrderNos": workOrderNos
                            # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
                            }
                            logger.info(main_card_msg)
                            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
                            channel.basic_publish(
                                exchange='',
                                routing_key="q_rpa_to_ebao_yagi",
                                body=json.dumps(main_card_msg, ensure_ascii=False),
                                properties=pika.BasicProperties(
                                    delivery_mode=2,  # 使消息持久化
                                ))
                        else:
                            logger.info("点击失败")
                            logger.info("错误数据为空,不进行处理")
                            main_card_msg = {
                                "msgId": json.loads(msg).get('msgId'),
                                "msgType": 4,
                                "resultCode": 0,
                                "resultMsg": "成功",
                                "timestamp": json.loads(msg).get('timestamp'),
                                "workOrderNos": workOrderNos
                            }

                            # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
                            logger.info(main_card_msg)
                            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
                            channel.basic_publish(
                                exchange='',
                                routing_key="q_rpa_to_ebao_yagi",
                                body=json.dumps(main_card_msg, ensure_ascii=False),
                                properties=pika.BasicProperties(
                                    delivery_mode=2,  # 使消息持久化
                                ))

                pass

        else:

            logger.info("错误数据为空,不进行处理")
            main_card_msg = {
                "msgId": json.loads(msg).get('msgId'),
                "msgType": 4,
                "resultCode": 1,
                "resultMsg": "失败",
                "timestamp": json.loads(msg).get('timestamp')
            }

            # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
            logger.info(main_card_msg)
            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key="q_rpa_to_ebao_yagi",
                body=json.dumps(main_card_msg, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 使消息持久化
                ))
            print("回传消息队列失败的消息")
            pass
    except Exception as e:
        send_alarm_msg("ALO 完成 最终的指令异常，编号为"+str(json.loads(msg).get('workOrderNo')))
        pass



"""
五号指令逻辑       获取alo详情的逻辑   
{
    "al0No": "AL0-RYNRX6F52AA4W",
    "msgId": "91c9bbd0-c600-47dd-af0f-903ae87d7a9d",
    "msgType": 5,
    "resultCode": 0,
    "resultMsg": "成功",
"timestamp": 1731049467981,
"packNo": 366,
    "volume": 30.423,
    "weight": 3807.16
}

"""
def orderfive(page,msg,cookie_str,channel):


    try:
        logger.info("开始处理获取alo详情信息")


        al0No = json.loads(msg).get('al0No')
        headers = {"Cookie": cookie_str}
        payload = {
            "filter": {
                "bookingReferences": [
                    {
                        "id": al0No,
                        "type": "FBA_BOOKING"
                    }
                ]
            }
        }
        # searchBookingDetailsByFilter   指令5的数据状态接口
        response = requests.post("https://xb-node.amazon.cn/glenn/booking/ajax/searchBookingDetailsByFilter", json=payload,
                                 headers=headers)

        thejson = json.loads(response.text)
        status = thejson.get('status')
        data = thejson.get('data')
        if (status == "SUCCESS" and data is not None and len(data.get('bookingDetails')) != 0):
            logger.info("指令5的数据状态接口触发成功 执行后续步骤 ")
            logger.info(data)

            print("输出综合数据")
            print(data.get('bookingDetails')[0].get('bookingHeader').get('receivedTotalContainers'),data.get('bookingDetails')[0].get('bookingHeader').get('receivedTotalVolume'),data.get('bookingDetails')[0].get('bookingHeader').get('receivedTotalWeight'))
            main_card_msg = {
                "al0No": json.loads(msg).get('al0No'),
                "msgId": json.loads(msg).get('msgId'),
                "msgType": 5,
                "resultCode": 0,
                "resultMsg": "成功",
                "timestamp": json.loads(msg).get('timestamp'),
                "packNo": str(data.get('bookingDetails')[0].get('bookingHeader').get('receivedTotalContainers')),
                "volume": str(data.get('bookingDetails')[0].get('bookingHeader').get('receivedTotalVolume')),
                "weight": str(data.get('bookingDetails')[0].get('bookingHeader').get('receivedTotalWeight'))
            }
            # 消息队列回推消息 json.dumps(main_card_msg, ensure_ascii=False)
            logger.info(main_card_msg)
            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key="q_rpa_to_ebao_yagi",
                body=json.dumps(main_card_msg, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 使消息持久化
                ))
        else:
            main_card_msg = {
                "al0No": json.loads(msg).get('al0No'),
                "msgId": json.loads(msg).get('msgId'),
                "msgType": 5,
                "resultCode": 1,
                "resultMsg": "失败",
                "timestamp": json.loads(msg).get('timestamp'),
                "packNo": '',
                "volume": '',
                "weight": ''
            }
            logger.info(main_card_msg)

            channel.queue_declare(queue='q_rpa_to_ebao_yagi', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key="q_rpa_to_ebao_yagi",
                body=json.dumps(main_card_msg, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 使消息持久化
                ))
    except Exception as e:
        # send_alarm_msg("获取alo详情的逻辑异常 编号为"+str(json.loads(msg).get('al0No')))
        pass

    pass

if __name__ == '__main__':
    import datetime
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    logger.add("亚集-logs/" + f'{today}.log', rotation="1000 MB")
    logger.info("开始执行RPA机器人")
    while True:
        try:
            establish_connection()
            logger.complete()
        except Exception as e:
            send_alarm_msg("出现了规划之外的异常，请人工检测"+str(e))
            # 这里增加一个邮件提示模块
            logger.error(e)
            logger.complete()
            pass
        time.sleep(4)


    # logger.info(response.status_code)
    # logger.info(response.encoding)
    # logger.info(response.url)
    # logger.info(response.text)