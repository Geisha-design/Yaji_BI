
from DrissionPage import WebPage, ChromiumOptions, SessionOptions
# from xuanniaoMysql import*
import pika
import json
import time
import requests
import configparser
from loguru import logger
import random
import hashlib
import re
from datetime import datetime
from sshtunnel import SSHTunnelForwarder

# configFile =r'D:/XUANNIAORPA/RPA/config/config-xuanniao.ini'
configFile =r'C:/RPA/config/config-xuanniao.ini'
config = configparser.RawConfigParser()
config.read(configFile, 'utf-8-sig')
company_name = config.get('config', 'company_name')
ebao_mq_ip = config.get('config','xuanniao_mq_ip')
ebao_mq_vhost = config.get('config','xuanniao_mq_vhost')
ebao_mq_port = config.get('config','xuanniao_mq_port')
mq_queue_name = config.get('config','xuanniao_queue_name')
ebao_mq_user = config.get('config','xuanniao_mq_user')
ebao_mq_password = config.get('config','xuanniao_mq_password')
theheadless = config.get('config','headless')


ssh_host = config.get('config','ssh_host')
ssh_port = config.get('config','ssh_port')
ssh_user = config.get('config','ssh_user')
ssh_password = config.get('config','ssh_password')
mysql_host = config.get('config','mysql_host')
mysql_port = config.get('config','mysql_port')


mysql_user = config.get('config','mysql_user')  # MySQL用户名
mysql_password = config.get('config','mysql_password') # MySQL密码
mysql_db = config.get('config','mysql_db')  # 数据库名


# SSH服务器和数据库的配置信息
ssh_host = '47.103.153.134'  # SSH服务器地址
ssh_port = 22  # SSH服务器端口，默认为22
ssh_user = 'yunjia'  # SSH用户名
ssh_password = 'Yunjia@smartebao123'  # SSH密码
mysql_host = 'rm-uf6n8d7is444fyc1b.mysql.rds.aliyuncs.com'  # MySQL数据库地址
mysql_port = 3306  # MySQL数据库端口，默认为3306

mysql_user = 'yunjia'
mysql_password = 'Yj@smartebao123'
mysql_db = 'ttseecrm'
# 创建SSH隧道
# server = SSHTunnelForwarder(
#     (ssh_host, ssh_port),
#     ssh_username=ssh_user,
#     ssh_password=ssh_password,
#     remote_bind_address=(mysql_host, mysql_port),
#     local_bind_address=('127.0.0.1', 33062)  # 将远程MySQL端口映射到本地的10000端口
# )
# # 启动隧道
# server.start()
# print(f"SSH tunnel started on local port: {server.local_bind_port}")
import pymysql
# MySQL数据库的配置信息

# 通过本地映射端口连接到MySQL数据库
# connection = pymysql.connect(
#     host='127.0.0.1',
#     port= 33062,
#     user= mysql_user,
#     password= mysql_password ,
#     db= mysql_db
# )

connection = pymysql.connect(
    host='rm-uf6n8d7is444fyc1b.mysql.rds.aliyuncs.com',
    port= 3306,
    user= 'yunjia',
    password= 'Yj@smartebao123' ,
    db= 'ttseecrm'
)
def dateTool(date_str):
    from datetime import datetime
    if date_str != '' and date_str != None:
        date_obj = datetime.strptime(date_str, "%Y/%m/%d")
        formatted_date_str = date_obj.strftime("%Y-%m-%d")
        print(formatted_date_str)
        return formatted_date_str

def get_day_of_week(date_str):
    # 将字符串转换为 datetime 对象
    from datetime import datetime
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    # 获取周几的数字表示（0-6），Monday=0, Sunday=6
    day_of_week_num = date_obj.weekday()
    # 获取周几的文字表示
    days_of_week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    day_of_week_text = days_of_week[day_of_week_num]
    return day_of_week_text, day_of_week_num + 1  # 返回文字和数字表示，数字表示从1开始
# 生成并打印19位唯一字符串
def generate_unique_string():
    # 获取当前时间戳，转换为整数
    timestamp = int(time.time() * 1000)
    # 生成一个随机数
    random_num = random.randint(100000, 999999)
    # 组合时间戳和随机数，确保总长度为19位
    unique_str = f"{timestamp:.0f}{random_num:04d}"
    print(unique_str)
    return unique_str

def get_release_messages(channel):
    msg = ''
    msg_count = 0
    method_frame, header_frame, body = channel.basic_get(mq_queue_name)
    if method_frame:
        # logger.info(method_frame+header_frame+body)
        # 本次请求编号
        delivery_tag = method_frame.delivery_tag
        # 本次获取完毕剩余的个数(不包含本条)
        msg_count = method_frame.message_count
        if msg_count!=None and msg_count != '':
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
def randomSleep():
    # 设置随机休眠时间，范围从min_seconds到max_seconds，整数秒
    min_seconds = 2
    max_seconds = 6
    # 生成一个随机整数，表示休眠的时间（秒）
    sleep_time = random.randint(min_seconds, max_seconds)
    print(f"Randomly selected sleep time: {sleep_time} seconds")
    # 让程序休眠这个随机时间
    time.sleep(sleep_time)
# 容易船期 CRAWLER
def ezOcean(msg):
    result = json.loads(msg)
    polCode = result["msgBody"]["polCode"]
    podCode = result["msgBody"]["podCode"]
    Etd = result["msgBody"]["etd"]
    from datetime import datetime, timedelta
    date_obj = datetime.strptime(Etd, "%Y-%m-%d")
    # 创建一个 timedelta 对象，表示30天
    thirty_days = timedelta(days=30)
    # 将30天加到原始日期上
    EtdEnd = date_obj + thirty_days
    print(Etd,EtdEnd)
    formatted_date_str = str(Etd)
    formatted_date_strb = str(EtdEnd).replace('00:00:00','')
    print(formatted_date_str,formatted_date_strb)
    logger.info("polCode:{},podCode:{},Etd:{}".format(polCode,podCode,Etd))
    if theheadless == 'false':
        co = ChromiumOptions()
    else:
        co = ChromiumOptions().headless()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)
    if theheadless == 'false':
        logger.info("进入目标网址(有头模式)"+"https://ezocean.com/")
    else:
        logger.info("进入目标网址(无头模式)"+"https://ezocean.com/")
    page.get('https://ezocean.com/SCHEDULE/ScheduleSearch/PORTPAIR?originval=CNSHA&destval=BEANT')
    print(page.cookies())
    cookies_dict = {cookie['name']: cookie['value'] for cookie in page.cookies()}

    print(cookies_dict)
    payload = {
               'strorigin':polCode,
               'strdest':podCode,
               'intPageNumber':1,
               'strAsc':'asc',
               'strType':'PORTPAIR',
               'strcarrier':'',
               'strdatefrom':formatted_date_str,
               'strdateto':formatted_date_strb
               }
    response = requests.get("https://ezocean.com/SCHEDULE/FnRetrieveScheduleList", json = payload, cookies=cookies_dict)
    msg = response.text
    print(response.text)

    # 一下字段用来处理回传的结果的
    result = json.loads(msg)
    Pageinfo = result["Pageinfo"]
    PageIndex = Pageinfo["PageIndex"]
    TotalRecords = Pageinfo["TotalRecords"]
    PageSize = Pageinfo["PageSize"]

    logger.info('此次查询结果总数：'+str(TotalRecords)+"此次查询结果总页"+str(PageSize)+'，当前页码：'+str(PageIndex)+'，每页数据量：'+str(PageSize))
    # logger.info("剩余需要进行翻页请求的页码")
    thepageNumCount = (TotalRecords//PageSize)+1
    logger.info("剩余需要进行翻页请求的页码为"+str(thepageNumCount))
    schedulers = result["schedulers"]
    thecount = len(schedulers)
    logger.info("本次组合船期数据量为"+str(thecount))
    # server.start()
    # print(f"SSH tunnel started on local port: {server.local_bind_port}")
    for i in range(0,len(schedulers)):
        POL_CODE = schedulers[i].get('PortFrom')
        POD_CODE = schedulers[i].get('PortTo')
        schedulers[i].get('TransitTime')
        CARRIER_CODE = schedulers[i].get('Operator')
        CARRIER_VESSEL = schedulers[i].get('VesselName')
        CARRIER_VOYAGE = schedulers[i].get('Voyage')
        # 疑似共舱数据
        SHARECAB_LIST = schedulers[i].get('Carriers')
        # schedulers[i].get('FromETA')
        ETA = schedulers[i].get('ToETA')
        ETA = dateTool(ETA)
        ETD = schedulers[i].get('FromETD')
        ETD = dateTool(ETD)
        ETA_WEEK, ROUTE_ETA = get_day_of_week(ETA)
        ETD_WEEK, ROUTE_ETD = get_day_of_week(ETD)

        if CARRIER_CODE !='' and CARRIER_CODE != '---':

            # 使用连接执行数据库操作
            cursor = connection.cursor()
            try:
                # 创建一个cursor对象
                cursor = connection.cursor()

                insert_sql = "INSERT INTO cs_sea_schedule (SEA_SCHEDULE_ID, POL_CODE,POD_CODE,CARRIER_CODE,CARRIER_VESSEL,CARRIER_VOYAGE,SOURCE,SHARECAB_LIST,ETA,ETD,ROUTE_ETD,ETA_WEEK,ETD_WEEK, CREATE_ORGID,CREATE_BYID,CREATE_BYNAME,UPDATE_ORGID,UPDATE_BYID,UPDATE_BYNAME) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # 要插入的数据
                data = (generate_unique_19_digit_hash(
                    POL_CODE + POD_CODE + CARRIER_CODE + CARRIER_VESSEL + CARRIER_VOYAGE + ETA + ETD), POL_CODE,
                        POD_CODE,
                        CARRIER_CODE,
                        CARRIER_VESSEL,
                        CARRIER_VOYAGE,
                        '1',
                        SHARECAB_LIST,
                        ETA,
                        ETD,
                        ROUTE_ETD,
                        ETA_WEEK,
                        ETD_WEEK, 'system', 'system', 'system', 'system', 'system', 'system')
                # 执行插入操作
                cursor.execute(insert_sql, data)
                # 提交事务
                connection.commit()
                # 打印插入结果
                print("插入成功，受影响的行数：", cursor.rowcount)

            except pymysql.MySQLError as e:
                # 发生错误时回滚事务
                connection.rollback()
                print("插入失败：", e)
        # finally:
        #     # 关闭cursor
        #     cursor.close()
        #     # 关闭数据库连接
        #     connection.close()
        # 关闭连接
    #     time.sleep(2)
    # 这部分逻辑只有多次翻页才回去执行
    if thepageNumCount !=0 and thepageNumCount !=1:
        for i in range(2,thepageNumCount+1):
            time.sleep(1.5)
            payload = {
                'strorigin': polCode,
                'strdest': podCode,
                'intPageNumber': i,
                'strAsc': 'asc',
                'strType': 'PORTPAIR',
                'strcarrier': '',
                'strdatefrom': formatted_date_str,
                'strdateto': formatted_date_strb
            }
            response = requests.get("https://ezocean.com/SCHEDULE/FnRetrieveScheduleList", json=payload,
                                    cookies=cookies_dict)
            msg = response.text
            print(response.text)
            # 一下字段用来处理回传的结果的
            result = json.loads(msg)
            Pageinfo = result["Pageinfo"]
            PageIndex = Pageinfo["PageIndex"]
            TotalRecords = Pageinfo["TotalRecords"]
            PageSize = Pageinfo["PageSize"]
            logger.info(
                '此次查询结果总数：' + str(TotalRecords) + "此次查询结果总页" + str(PageSize) + '，当前页码：' + str(
                    PageIndex) + '，每页数据量：' + str(PageSize))
            schedulers = result["schedulers"]
            thecount = len(schedulers)
            logger.info("本次翻页组合船期数据量为" + str(thecount))
            # server.start()
            # print(f"SSH tunnel started on local port: {server.local_bind_port}")
            for i in range(0, len(schedulers)):

                POL_CODE = schedulers[i].get('PortFrom')

                POD_CODE = schedulers[i].get('PortTo')

                schedulers[i].get('TransitTime')

                CARRIER_CODE = schedulers[i].get('Operator')

                CARRIER_VESSEL = schedulers[i].get('VesselName')

                CARRIER_VOYAGE = schedulers[i].get('Voyage')
                # 疑似共舱数据
                SHARECAB_LIST = schedulers[i].get('Carriers')
                # schedulers[i].get('FromETA')
                ETA = schedulers[i].get('ToETA')
                ETA = dateTool(ETA)
                ETD = schedulers[i].get('FromETD')
                ETD = dateTool(ETD)
                ETA_WEEK, ROUTE_ETA = get_day_of_week(ETA)
                ETD_WEEK, ROUTE_ETD = get_day_of_week(ETD)
                # 使用连接执行数据库操作
                if CARRIER_CODE != '' and CARRIER_CODE != '---':

                    try:
                        # 创建一个cursor对象
                        cursor = connection.cursor()

                        insert_sql = "INSERT INTO cs_sea_schedule (SEA_SCHEDULE_ID, POL_CODE,POD_CODE,CARRIER_CODE,CARRIER_VESSEL,CARRIER_VOYAGE,SOURCE,SHARECAB_LIST,ETA,ETD,ROUTE_ETD,ETA_WEEK,ETD_WEEK, CREATE_ORGID,CREATE_BYID,CREATE_BYNAME,UPDATE_ORGID,UPDATE_BYID,UPDATE_BYNAME) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        # 要插入的数据
                        data = (generate_unique_19_digit_hash(POL_CODE+POD_CODE+CARRIER_CODE+CARRIER_VESSEL+CARRIER_VOYAGE+ETA+ETD), POL_CODE,
                                POD_CODE,
                                CARRIER_CODE,
                                CARRIER_VESSEL,
                                CARRIER_VOYAGE,
                                '1',
                                SHARECAB_LIST,
                                ETA,
                                ETD,
                                ROUTE_ETD,
                                ETA_WEEK,
                                ETD_WEEK,'system','system','system','system','system','system')
                        # 执行插入操作
                        cursor.execute(insert_sql, data)
                        # 提交事务
                        connection.commit()
                        # 打印插入结果
                        print("插入成功，受影响的行数：", cursor.rowcount)

                    except pymysql.MySQLError as e:
                        # 发生错误时回滚事务
                        connection.rollback()
                        print("插入失败：", e)
    page.quit()
# connection.close()
    # server.stop()  # 停止SSH隧道
# if __name__ == '__main__':
def saika():
    # 需要控制下浏览器内存爆炸的问题 20次一次重启
    import datetime
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # logger.add("玄鸟-logs/" + f'{today}.log', rotation="10000 MB")
    # ########################## consumer #########################
    # #
    credentials = pika.PlainCredentials(ebao_mq_user, ebao_mq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(ebao_mq_ip, ebao_mq_port, ebao_mq_vhost, credentials))
    channel = connection.channel()
    msg, msg_count = get_release_messages(channel)
    if (msg == '' or msg_count == -1):
        # logger.info("当前状态下玄鸟平台下发的待执行任务为空")
        pass
    while (msg != ''):
        result = json.loads(msg)
        msgBody = result["msgBody"]
        # logger.info('输出测试时期的识别标记')
        if msgBody!=None:

            logger.info(msgBody)
        # logger.info("收到新指令，开始处理")
        ezOcean(msg)
        randomSleep()
        msg, msg_count = get_release_messages(channel)


# {"msgBody":{"etd":"2024-10-16","podCode":"MXMAN","polCode":"CNNGB"}}
#
# {"msgBody":{"etd":"2024-10-16","podCode":"NLROT","polCode":"CNNGB"}}
#
# {"msgBody":{"etd":"2024-10-16","podCode":"GBFEL","polCode":"CNNGB"}}
#
# {"msgBody":{"etd":"2024-10-16","podCode":"BEANT","polCode":"CNNGB"}}



def sha256_to_digits(string):
    # 创建sha256对象
    sha256_obj = hashlib.sha256()
    sha256_obj.update(string.encode('utf-8'))
    # 获取16进制的加密结果
    sha256_hash = sha256_obj.hexdigest()
    # 仅保留数字字符
    digits_only = re.sub(r'[^0-9]', '', sha256_hash)
    return digits_only

    # 使用函数
    original_string = string
    digits_only_hash = sha256_to_digits(original_string)
    print(f'SHA-256全数字: {digits_only_hash}')

# 用于生成unique
import hashlib
def generate_unique_19_digit_hash(input_string):
    # 创建sha256对象
    sha256_obj = hashlib.sha256()
    sha256_obj.update(input_string.encode('utf-8'))
    # 获取16进制的加密结果
    sha256_hash_hex = sha256_obj.hexdigest()
    # 将十六进制字符串转换为十进制
    decimal_value = int(sha256_hash_hex, 16)
    # 转换为字符串并截取前19位数字，如果不足19位则用0填充
    unique_19_digit = str(decimal_value).zfill(19)
    return unique_19_digit[0:19]


if __name__ == '__main__':

    # 先要检查下浏览器的健康状态
    # 如果浏览器不健康 直接重置初始化状态
    import datetime

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    logger.add("D:/xuanniao/玄鸟-logs/" + f'{today}.log', rotation="10000 MB",compression='zip')
    logger.info('start')
    # while True:
    #
    #     saika()
    #     time.sleep(5)
    while True:
        # 在这里加一个暴力的延时即可  比如说休眠多久执行一次
        try:
            saika()
        except Exception as e:
            # 这里增加一个邮件提示模块
            logger.error(e)
            pass
        time.sleep(40)


