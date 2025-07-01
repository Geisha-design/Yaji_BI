import os
import anyconfig
import random
import time
import requests
from loguru import logger
import json
import pika


# 到时候专门存一个配置文件 地址
def baseConfig(divide,key):
    yaml_config = anyconfig.load('./element.yaml', ac_parser="yaml", encodings='gbk')
    return yaml_config.get(divide).get(key)


company_name = baseConfig('config','company_name')
ebao_mq_ip = baseConfig('config','xuanniao_mq_ip')
ebao_mq_vhost = baseConfig('config','xuanniao_mq_vhost')
ebao_mq_port = baseConfig('config','xuanniao_mq_port')
mq_queue_name = baseConfig('config','xuanniao_queue_name')
ebao_mq_user = baseConfig('config','xuanniao_mq_user')
ebao_mq_password = baseConfig('config','xuanniao_mq_password')
theheadless = baseConfig('config','headless')
ebao_url_ip = baseConfig('config','oit_url_ip')
def randomSleep():
    # 设置随机休眠时间，范围从min_seconds到max_seconds，整数秒
    min_seconds = 1
    max_seconds = 3
    # 生成一个随机整数，表示休眠的时间（秒）
    sleep_time = random.randint(min_seconds, max_seconds)
    print(f"Randomly selected sleep time: {sleep_time} seconds")
    # 让程序休眠这个随机时间
    time.sleep(sleep_time)


def get_release_messages(channel):
    mq_queue_name =  baseConfig('config', 'queue_name')
    msg = ''
    msg_count = 0
    method_frame, header_frame, body = channel.basic_get(mq_queue_name)
    if method_frame:
        # logger.info(method_frame+header_frame+body)
        # 本次请求编号
        delivery_tag = method_frame.delivery_tag
        # 本次获取完毕剩余的个数(不包含本条)
        msg_count = method_frame.message_count
        logger.info('剩余未执行指令数量：',msg_count)
        # 获得的数据
        msg = body.decode()
        logger.info('获取的指令：' + msg)
        # 提交本次响应结果
        channel.basic_ack(delivery_tag)
    else:
        # logger.info('暂无未执行的指令')
        msg_count = -1
    return msg,msg_count

def callback_error(msg, errorMsg):
    result = json.loads(msg)
    msgType = result["msgType"]
    guid = result["guid"]
    msgBody = result["msgBody"]
    identifyingCode = result["msgBody"]["identifyingCode"]
    orgId = result["msgBody"]["orgId"]
    orderNo = result["msgBody"]["orderNo"]
    executed = result["msgBody"]["executed"]
    payload = {
        "identifyingCode": identifyingCode,
        "orderNo": orderNo
    }
    data = {
        "guid":guid,
        "message":errorMsg,
        "executed":executed,
        "orgId":orgId,
        "payload": payload
    }
    callback(msgType, data)

def callback(msgType, data):
    logger.info("callback-data:{0}".format(data))
    ebao_url_ip = baseConfig('config', 'oit_url_ip')
    if (msgType == 1):
        ebaoUrl = ebao_url_ip+"/openapi/rpa/eport/paystatus"
    elif (msgType == 2):
        ebaoUrl = ebao_url_ip+"/openapi/rpa/eport/detail"
    headers = {'Content-Type': 'application/json', 'Connection':'close'}
    try:
        response = requests.post(url=ebaoUrl, data=json.dumps(data, sort_keys=True), headers=headers)
        logger.info("callback-response:{}".format(response.text))
        result = json.loads(response.text)
        if ('code' in result.keys()):
            code = result['code']
            if(code == 200):
               logger.info('callback-调用回调接口成功')
    except Exception as e:
        logger.info("record_operation_info-调用执行回调接口调用异常：{}".format(e))
        alter_msg = "调用执行回调接口调用异常：{}".format(e)
        # alter_msg += "\n指令信息如下："+msg
        send_alarm_msg(alter_msg)

def rpacapture(divide,key):
    json_config = anyconfig.load('./element.json', encodings='gbk')
    return json_config.get(divide).get(key)

def send_alarm_msg(text):
    user = rpacapture('alarmmsg','user')
    token = rpacapture('alarmmsg','token')
    print("输出token")
    print(user)
    print(token)
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=" + token
    text += "\n 当前机器人：{}".format(os.environ.get("COMPUTERNAME"))
    text += "\n 亚集-亚马逊对接RPA"
    data = {
        "msgtype": "text",
        "text": {"content": text},
        "at": {"atMobiles": [user], "isAtAll": False}
    }
    headers = {'Content-Type': 'application/json'}
    try:
        x = requests.post(url=webhook, data=json.dumps(data), headers=headers)
        if(x):
            logger.info(rpacapture('alarmmsg','success'))
        else:
            logger.info(rpacapture('alarmmsg','failure'))
    except Exception as e:
        logger.info("RPA亚集预警信息发送钉钉失败：{}".format(e))






def send_alarm_msg_urgent(text):
    user = rpacapture('alarmmsg','user')
    token = rpacapture('alarmmsg','token')
    print("输出token")
    print(user)
    print(token)
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=" + token
    text += "\n 当前机器人：{}".format(os.environ.get("COMPUTERNAME"))
    text += "\n 亚集-亚马逊对接RPA"
    data = {
        "msgtype": "text",
        "text": {"content": text},
        "at": {"atMobiles": [user], "isAtAll": False}
    }
    headers = {'Content-Type': 'application/json'}
    try:
        x = requests.post(url=webhook, data=json.dumps(data), headers=headers)
        if(x):
            logger.info(rpacapture('alarmmsg','success'))
        else:
            logger.info(rpacapture('alarmmsg','failure'))
    except Exception as e:
        logger.info("RPA亚集预警信息发送钉钉失败：{}".format(e))



class rpa(object):
    def __init__(self, ocr: bool = True, det: bool = False, old: bool = False, beta: bool = False,
                 use_gpu: bool = False,
                 device_id: int = 0, show_ad=True, import_onnx_path: str = "", charsets_path: str = ""):
        if show_ad:
            print("欢迎使用易豹RPA工具")

if __name__ == '__main__':
    send_alarm_msg("预警测试")

