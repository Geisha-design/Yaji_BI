# coding = utf-8
import os
import time
from playwright.sync_api import Playwright, sync_playwright, expect
import datetime
# from utiles.inireader import *
import pika
import json
import hashlib
from bs4 import BeautifulSoup
import json
import requests
from loguru import logger


def dd_robot(msg):
    HEADERS = {"Content-Type": "application/json;charset=utf-8"}
    key = "45f87c71daf0eca030f299595fd0a80378c2d6dfdf7cc5777fc360fe1b6bfc00"
    url = f" https://oapi.dingtalk.com/robot/send?access_token={key}"
    # content里面要设置关键字 我机器人设置的关键字为'接口测试结果：'
    data_info = {
        "msgtype": "text",
        "text": {
            "content": "木牛接口测试结果：" + msg
            # f'\n总共运行{api_run_count}条用例'
            #    + f'\n成功{api_passed_count}条用例'
            #    + f'\n失败{api_failed_count}条用例'
            #    + f'\n失败用例名称{str(failed_case_name)}'
            #    + f'\n失败用例地址{str(failed_case_path)}'
        },
        "isAtAll": False
        # 这个注解的意思是说明是否要@所有人
        # 这是配置需要@的人
        #  ,"at": {"atMobiles": ["15xxxxxx06",'18xxxxxx1']}
        , "at": {"atMobiles": ['13396808752', '15990100149']}

    }
    value = json.dumps(data_info)
    response = requests.post(url, data=value, headers=HEADERS)
    if response.json()['errmsg'] != 'ok':
        logger.info(response.text)


# 还要花时间处理浏览器卡住的refresh处理
# 必要的话需要准备一个ip代理池 ， 这个代理池用来防止被页面干掉  如果 浏览器搜索量过大 ，需要执行些重定向的逻辑
# alert-info

class RabbitMQ:
    def __init__(self, host, port, username, password, virtual_host, exchange_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, queue_name, message):
        self.connect()
        self.channel.basic_publish(exchange=self.exchange_name, routing_key=queue_name, body=message,
                                   properties=pika.BasicProperties(delivery_mode=2))
        self.close()

    def consume(self, queue_name):
        self.connect()
        messages = []
        # 消费队列中的消息并注册回调函数
        for method_frame, properties, body in self.channel.consume(queue_name, inactivity_timeout=1):
            if method_frame is None:
                break
            messages.append(body.decode())
            # 告知RabbitMQ消息已被处理
            self.channel.basic_ack(method_frame.delivery_tag)
        self.close()
        return messages

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()


js = """
Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
"""


def login(context, page):
    # context = browser.new_context()
    # page = context.new_page()
    page.add_init_script(js);
    page.goto("https://pss.txffp.com/pss/app/login/manage")
    page.get_by_placeholder("手机号").fill("13456925659")
    page.get_by_placeholder("密码").fill("Wang804733994")
    # page.get_by_placeholder("手机号").fill("13584497552")
    # page.get_by_placeholder("密码").fill("Jjyy58939101")
    # 目前这个使用weak 标签 一旦出现了weak 定位失败的问题，需要在一段时间的测试中做一下自动位置调试，从pom树进行顶层扫描
    page.locator("#Shape3").click()
    # page.locator("#rectBottom").click()
    # background - color: grey;
    thebeta = 'background-color: grey;'
    while (thebeta == 'background-color: grey;'):
        logger.info(thebeta)
        thebeta = page.locator('#submitButton').get_attribute('style')
        logger.info(thebeta)
        time.sleep(3)
    page.get_by_role("link", name="授权登录").click()
    logger.info("验证通过,机器人已成功进入登录状态")
    # 同时这个登录状态文件还要查看是否依然有效
    context.storage_state(path='login_data.json')
    return page


def runweikaipiao(playwright: Playwright, username, password, beginTime, ssoOrgId) -> None:
    # username = '13456925659'
    # 目前cookie存活周期未知，为了更好得保活，需要定时更新cookie 记录的状态
    # 用于防止被监测出来，目前只需要添加此规则即可推动流程
    js = """
    Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
    """
    # browser = playwright.chromium.launch(headless=headmode)
    browser = playwright.chromium.launch(headless=False)
    browser = playwright.chromium.launch(headless=True)
    # context = browser.new_context()
    # page = context.new_page()
    # page.add_init_script(js);
    # ss_file = 'login_data.json'
    # # 判断是否存在状态文件，有的话就加载
    # if os.path.isfile(ss_file):
    context = browser.new_context()
    page = context.new_page()
    page.add_init_script(js);
    page.goto("https://pss.txffp.com/pss/app/login/manage")
    # page.get_by_placeholder("手机号").fill('13456925659')
    # page.get_by_placeholder("密码").fill('Wang804733994')
    page.get_by_placeholder("手机号").fill(username)
    page.get_by_placeholder("密码").fill(password)
    # 目前这个使用weak 标签 一旦出现了weak 定位失败的问题，需要在一段时间的测试中做一下自动位置调试，从pom树进行顶层扫描
    page.locator("#Shape3").click()
    # page.locator("#rectBottom").click()
    # background - color: grey;
    thebeta = 'background-color: grey;'
    while (thebeta == 'background-color: grey;'):
        logger.info(thebeta)
        thebeta = page.locator('#submitButton').get_attribute('style')
        logger.info(thebeta)
        time.sleep(2)
    page.get_by_role("link", name="授权登录").click()
    logger.info("验证通过,机器人已成功进入登录状态")

    time.sleep(4)
    # page.locator('#myInvoice > a').click()
    # 这里需要增加一个对页面是否展示的分页判断
    logger.info("输出标识")

    # 以接口的形式获取所有的http请求 避免前端翻页出问题挂掉
    listurlc = []
    listnamec = []
    listthenotecardc = []
    listthecarnnotec = []
    listzardc = []
    dream = 1
    pageNo = 1
    while (dream != 0):

        resp = page.request.post(
            url="https://pss.txffp.com/pss/app/login/invoice/query/card",
            params={
                'pageNo': pageNo,
                'changeView': 'card',
                # 'cardId':listzard[io],
                # 'a1eb4e3c1804464da55d07e37e99eb97',
                'userType': 'COMPANY',
                # 'month': 202311
                # 'month': beginTime
            },
            headers={
                'Content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                              ' x64) AppleWebKit/537.36 (KHTML, like'
                              ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }
        )
        rqg = resp.body().decode()
        logger.info(resp.body().decode())
        time.sleep(1)
        html = rqg
        soup = BeautifulSoup(html, 'lxml')
        thecount = len(soup.select(".etc_card_dl"))
        logger.info(thecount)

        if (thecount == 0):
            dream -= 1
        # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置
        for i in range(1, thecount + 1):
            thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

            thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                0].text.replace('记账卡：', '').replace(' ', '').strip()

            thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

            thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
            thedetailurl = 'https://pss.txffp.com/' + thedetailurla
            thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace('/COMPANY',
                                                                                                          '')
            logger.info(thename, thenotecard, thecarnote, thedetailurla)
            listurlc.append(thedetailurl)
            listnamec.append(thename)
            listthenotecardc.append(thenotecard)
            listthecarnnotec.append(thecarnote)
            listzardc.append(thedetailurla)
        # thecount = len(soup.find_all('a',class_='etc_card_dl'))
        pageNo += 1
        logger.info(pageNo)

    logger.info("finish")
    logger.info(listzardc)
    logger.info(listthecarnnotec)

    logger.info(len(listzardc))
    logger.info(len(listthecarnnotec))

    time.sleep(1.5)
    # 这是二次请求，以防万一单词请求不通过导致挂掉
    if (len(listzardc) == 0):
        # 以接口的形式获取所有的http请求 避免前端翻页出问题挂掉
        listurlc = []
        listnamec = []
        listthenotecardc = []
        listthecarnnotec = []
        listzardc = []
        dream = 1
        pageNo = 1
        while (dream != 0):

            resp = page.request.post(
                url="https://pss.txffp.com/pss/app/login/invoice/query/card",
                params={
                    'pageNo': pageNo,
                    'changeView': 'card',
                    # 'cardId':listzard[io],
                    # 'a1eb4e3c1804464da55d07e37e99eb97',
                    'userType': 'COMPANY',
                    # 'month': 202311
                    # 'month': beginTime
                },
                headers={
                    'Content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                  ' x64) AppleWebKit/537.36 (KHTML, like'
                                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                }
            )
            rqg = resp.body().decode()
            logger.info(resp.body().decode())
            time.sleep(1)
            html = rqg
            soup = BeautifulSoup(html, 'lxml')

            thecount = len(soup.select(".etc_card_dl"))
            logger.info(thecount)

            if (thecount == 0):
                dream -= 1
            # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置
            for i in range(1, thecount + 1):
                thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()
                thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                    0].text.replace('记账卡：', '').replace(' ', '').strip()
                thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                    0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()
                thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                    '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
                thedetailurl = 'https://pss.txffp.com/' + thedetailurla
                thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace(
                    '/COMPANY', '')
                logger.info(thename, thenotecard, thecarnote, thedetailurla)
                listurlc.append(thedetailurl)
                listnamec.append(thename)
                listthenotecardc.append(thenotecard)
                listthecarnnotec.append(thecarnote)
                listzardc.append(thedetailurla)
            # thecount = len(soup.find_all('a',class_='etc_card_dl'))
            pageNo += 1
            logger.info(pageNo)
        logger.info("finish")
        logger.info(listzardc)
        logger.info(listthecarnnotec)
        logger.info(len(listzardc))
        logger.info(len(listthecarnnotec))
    # 以公司形式
    # 以接口的形式获取所有的http请求 避免前端翻页出问题挂掉
    listurl = []
    listname = []
    listthenotecard = []
    listthecarnnote = []
    listzard = []
    dream = 1
    pageNo = 1
    while (dream != 0):

        resp = page.request.post(
            url="https://pss.txffp.com/pss/app/login/invoice/query/card",
            params={
                'pageNo': pageNo,
                'changeView': 'card',
                'userType': 'PERSONAL',
            },
            headers={
                'Content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                              ' x64) AppleWebKit/537.36 (KHTML, like'
                              ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }
        )
        rqg = resp.body().decode()
        logger.info(resp.body().decode())
        time.sleep(1)
        html = rqg
        soup = BeautifulSoup(html, 'lxml')
        thecount = len(soup.select(".etc_card_dl"))
        logger.info(thecount)
        if (thecount == 0):
            dream -= 1
        # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置
        for i in range(1, thecount + 1):
            thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

            thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                0].text.replace('记账卡：', '').replace(' ', '').strip()

            thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

            thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
            thedetailurl = 'https://pss.txffp.com/' + thedetailurla
            thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace('/PERSONAL',
                                                                                                          '')
            logger.info(thename, thenotecard, thecarnote, thedetailurla)
            listurl.append(thedetailurl)
            listname.append(thename)
            listthenotecard.append(thenotecard)
            listthecarnnote.append(thecarnote)
            listzard.append(thedetailurla)
        # thecount = len(soup.find_all('a',class_='etc_card_dl'))
        pageNo += 1
        logger.info(pageNo)

    logger.info("finish")
    logger.info(listzard)
    logger.info(listthecarnnote)

    logger.info(len(listzard))
    logger.info(len(listthecarnnote))

    if (len(listzard) == 0):

        listurl = []
        listname = []
        listthenotecard = []
        listthecarnnote = []
        listzard = []
        dream = 1
        pageNo = 1
        while (dream != 0):

            resp = page.request.post(
                url="https://pss.txffp.com/pss/app/login/invoice/query/card",
                params={
                    'pageNo': pageNo,
                    'changeView': 'card',
                    # 'cardId':listzard[io],
                    # 'a1eb4e3c1804464da55d07e37e99eb97',
                    'userType': 'PERSONAL',
                    # 'month': 202311
                    # 'month': beginTime
                },
                headers={
                    'Content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                  ' x64) AppleWebKit/537.36 (KHTML, like'
                                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                }
            )
            rqg = resp.body().decode()
            logger.info(resp.body().decode())
            time.sleep(1)
            html = rqg
            soup = BeautifulSoup(html, 'lxml')
            thecount = len(soup.select(".etc_card_dl"))
            logger.info(thecount)

            if (thecount == 0):
                dream -= 1
            # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置

            for i in range(1, thecount + 1):
                thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

                thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                    0].text.replace('记账卡：', '').replace(' ', '').strip()

                thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                    0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

                thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                    '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
                thedetailurl = 'https://pss.txffp.com/' + thedetailurla
                thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace(
                    '/PERSONAL', '')
                logger.info(thename, thenotecard, thecarnote, thedetailurla)
                listurl.append(thedetailurl)
                listname.append(thename)
                listthenotecard.append(thenotecard)
                listthecarnnote.append(thecarnote)
                listzard.append(thedetailurla)
            # thecount = len(soup.find_all('a',class_='etc_card_dl'))
            pageNo += 1
            logger.info(pageNo)

        logger.info("finish")
        logger.info(listzard)
        logger.info(listthecarnnote)

        logger.info(len(listzard))
        logger.info(len(listthecarnnote))

    logger.info('开始执行未开票部分个人卡')
    page.goto('https://pss.txffp.com/pss/app/login/cardList/manage/invoiceApply/PERSONAL')
    time.sleep(4)
    # global saikas
    try:

        for io in range(0, len(listzard)):

            carflagname = listthecarnnote[io]

            pagesizeflag = 0
            saikas = 1
            while (saikas != 0):
                pagesizeflag += 1
                resp = page.request.post(
                    url="https://pss.txffp.com/pss/app/login/invoice/consumeTrans/manage",
                    params={
                        # 'pageSize':100,
                        'id': listzard[io],
                        # 'a1eb4e3c1804464da55d07e37e99eb97',
                        # 'userType':'PERSONAL',
                        'month': beginTime,
                        # '202312',
                        'pageNo': str(pagesizeflag),
                        'startMoth': beginTime
                        # '202312',
                        # 'month': beginTime
                    },
                    headers={
                        'Content-type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                      ' x64) AppleWebKit/537.36 (KHTML, like'
                                      ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                    }

                )
                rqg = resp.body().decode()
                logger.info(resp.body().decode())
                html = rqg
                soup = BeautifulSoup(html, 'lxml')  # 生成BeautifulSoup对象
                logger.info('输出格式化的BeautifulSoup对象：', soup.prettify())
                thecountss = int(len(soup.select(".tab_tr_td10")) / 4)
                logger.info(thecountss)
                if (thecountss == 0):
                    saikas -= 1
                logger.info(saikas)
                theall = []
                # 分析捕获页签的交易时间
                for i in range(1, thecountss + 1):
                    tradetime = \
                        soup.select(
                            '#taiji_search_data > table > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(4)')[
                            0].text.replace('交易时间：', '')
                    trademoney = \
                        soup.select(
                            '#taiji_search_data > table > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(3)')[
                            0].text.replace('￥', '').replace('\n', '').replace('\t', '')
                    trademoney = trademoney.replace(',', '').replace('，', '')
                    tradestartprovince = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(2)')[0].text

                    tradeendprovince = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(4)')[0].text

                    # taiji_search_data > table > tbody > tr:nth-child(1) > td.tab_tr_td30 > div:nth-child(7)
                    tradestart = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(6)')[0].text
                    tradeend = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(8)')[0].text
                    logger.info(tradetime, trademoney, tradestartprovince, tradeendprovince, tradestart, tradeend)
                    # 生成的唯一识别串
                    # 待加密信息
                    saika = username + carflagname + tradetime + trademoney + tradestart + tradeend
                    # 创建md5对象
                    hl = hashlib.md5()
                    # 更新hash对象的值，如果不使用update方法也可以直接md5构造函数内填写
                    # md5_obj=hashlib.md5("123456".encode("utf-8")) 效果一样
                    hl.update(saika.encode("utf-8"))
                    logger.info('MD5加密前为 ：' + saika)
                    theencrypt = hl.hexdigest()
                    logger.info('MD5加密后为 ：' + theencrypt)

                    themessdetail = {
                        # "etcCardNo": "ETC记账卡号",
                        "etcAccount": username,
                        "driverLicensePlateNo": listthecarnnote[io],
                        "etcDataId": theencrypt,
                        "etcCardType": 1,
                        # //ETC卡类型（1：个人卡，2：单位卡）
                        "etcCardNo": listthenotecard[io],
                        "paymentAmount": trademoney,
                        # //交易金额（元）
                        "paymentTime": tradetime,
                        # //交易时间
                        "inboundProvince": tradestartprovince,
                        "inboundAddress": tradestart,
                        "outboundProvince": tradeendprovince,
                        "outboundAddress": tradeend
                    }
                    theall.append(themessdetail)

                if (theall == []):
                    theall = None
                main_card_msg = {
                    "etcAccount": username,
                    "ssoOrgId": ssoOrgId,
                    # "driverLicensePlateNo":pp,
                    "data": theall
                }
                logger.info("输出本次json的信息")
                logger.info(main_card_msg)
                my_mq.publish('TXFFP_SEND_TO_WOX_QUE', json.dumps(main_card_msg, ensure_ascii=False))
                time.sleep(1)

            # 每次访问设置下间隔，不要太过分
            time.sleep(3)
    except Exception as e:
        logger.info(e)

    logger.info("输出公司级别的内容")

    logger.info("开始执行开票部分")

    logger.info("开始执行未开票部分")
    logger.info('开始执行未开票部分公司卡')

    try:
        page.goto('https://pss.txffp.com/pss/app/login/cardList/manage/invoiceApply/PERSONAL')
        time.sleep(4)
        for io in range(0, len(listzardc)):
            carflagname = listthecarnnotec[io]
            pagesizeflagss = 0
            saikass = 1
            while (saikass != 0):
                pagesizeflagss += 1
                resp = page.request.post(
                    url="https://pss.txffp.com/pss/app/login/invoice/consumeTrans/manage",
                    params={
                        # 'pageSize':100,
                        'id': listzardc[io],
                        # 'a1eb4e3c1804464da55d07e37e99eb97',
                        # 'userType':'PERSONAL',
                        'month': beginTime,
                        # '202312',
                        'pageNo': str(pagesizeflagss),
                        'startMoth': beginTime
                        # '202312',
                        # 'month': beginTime
                    },
                    headers={
                        'Content-type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                      ' x64) AppleWebKit/537.36 (KHTML, like'
                                      ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                    }
                )
                rqg = resp.body().decode()
                logger.info(resp.body().decode())

                html = rqg
                soup = BeautifulSoup(html, 'lxml')  # 生成BeautifulSoup对象
                logger.info('输出格式化的BeautifulSoup对象：', soup.prettify())
                thecountss = int(len(soup.select(".tab_tr_td10")) / 4)
                logger.info(thecountss)
                if (thecountss == 0):
                    saikass -= 1
                theall = []
                # 分析捕获页签的交易时间
                for i in range(1, thecountss + 1):
                    tradetime = \
                        soup.select(
                            '#taiji_search_data > table > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(4)')[
                            0].text.replace('交易时间：', '')
                    trademoney = \
                        soup.select(
                            '#taiji_search_data > table > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(3)')[
                            0].text.replace('￥', '').replace('\n', '').replace('\t', '')
                    trademoney = trademoney.replace(',', '').replace('，', '')

                    tradestartprovince = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(2)')[0].text

                    # taiji_search_data > table > tbody > tr:nth-child(1) > td.tab_tr_td30 > div:nth-child(4)
                    tradeendprovince = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(4)')[0].text

                    # taiji_search_data > table > tbody > tr:nth-child(1) > td.tab_tr_td30 > div:nth-child(7)
                    tradestart = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(6)')[0].text
                    # taiji_search_data > table > tbody > tr:nth-child(3) > td.tab_tr_td30 > div:nth-child(6)
                    # taiji_search_data > table > tbody > tr:nth-child(1) > td.tab_tr_td30 > div:nth-child(9)
                    tradeend = soup.select('#taiji_search_data > table > tbody > tr:nth-child(' + str(
                        i) + ') > td.tab_tr_td30 > div:nth-child(8)')[0].text

                    logger.info(tradetime, trademoney, tradestartprovince, tradeendprovince, tradestart, tradeend)

                    # 生成的唯一识别串
                    # 待加密信息
                    saika = username + carflagname + tradetime + trademoney + tradestart + tradeend
                    # 创建md5对象
                    hl = hashlib.md5()
                    # 更新hash对象的值，如果不使用update方法也可以直接md5构造函数内填写
                    # md5_obj=hashlib.md5("123456".encode("utf-8")) 效果一样
                    hl.update(saika.encode("utf-8"))
                    logger.info('MD5加密前为 ：' + saika)
                    theencrypt = hl.hexdigest()
                    logger.info('MD5加密后为 ：' + theencrypt)

                    themessdetail = {
                        # "etcCardNo": "ETC记账卡号",
                        "etcAccount": username,
                        "driverLicensePlateNo": listthecarnnotec[io],
                        "etcDataId": theencrypt,
                        "etcCardType": 2,
                        # //ETC卡类型（1：个人卡，2：单位卡）
                        "etcCardNo": listthenotecardc[io],
                        "paymentAmount": trademoney,
                        # //交易金额（元）
                        "paymentTime": tradetime,
                        # //交易时间
                        "inboundProvince": tradestartprovince,
                        "inboundAddress": tradestart,
                        "outboundProvince": tradeendprovince,
                        "outboundAddress": tradeend
                    }
                    theall.append(themessdetail)

                if (theall == []):
                    theall = None

                main_card_msg = {
                    "etcAccount": username,
                    "ssoOrgId": ssoOrgId,
                    # "driverLicensePlateNo":pp,
                    "data": theall
                }
                logger.info("输出本次json的信息")
                logger.info(main_card_msg)
                my_mq.publish('TXFFP_SEND_TO_WOX_QUE', json.dumps(main_card_msg, ensure_ascii=False))
                time.sleep(1.8)

            # 每次访问设置下间隔，不要太过分
            time.sleep(3.5)
    except Exception as e:
        logger.info(e)


def runyikaipiao(playwright: Playwright, username, password, beginTime, ssoOrgId) -> None:
    # username = '13456925659'
    # 目前cookie存活周期未知，为了更好得保活，需要定时更新cookie 记录的状态
    # 用于防止被监测出来，目前只需要添加此规则即可推动流程
    js = """
    Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
    """
    # browser = playwright.chromium.launch(headless=headmode)
    browser = playwright.chromium.launch(headless=False)
    browser = playwright.chromium.launch(headless=True)
    # context = browser.new_context()
    # page = context.new_page()
    # page.add_init_script(js);
    # ss_file = 'login_data.json'
    # # 判断是否存在状态文件，有的话就加载

    # if os.path.isfile(ss_file):
    # context = browser.new_context(storage_state='login_data.json')
    # page = context.new_page()
    # page.goto("https://pss.txffp.com/pss/app/login/manage")
    # logger.info(page.title())
    # 通过title判断是否成功进入系统，如果没有需要进行登录，一般在第一次访问系统，或登录信息过期等原因会触发
    # 这里还要考虑不同账户的不通cookie账户状态留存，防止核对的时候出现不匹配的问题，可以将留存的cookie名用账号的id来命名
    # if '统一登录平台'  in page.title():
    #     page = login(context,page)
    # else:
    context = browser.new_context()
    page = context.new_page()
    page.add_init_script(js);
    page.goto("https://pss.txffp.com/pss/app/login/manage")
    # page.get_by_placeholder("手机号").fill('13456925659')
    # page.get_by_placeholder("密码").fill('Wang804733994')
    page.get_by_placeholder("手机号").fill(username)
    page.get_by_placeholder("密码").fill(password)
    # 目前这个使用weak 标签 一旦出现了weak 定位失败的问题，需要在一段时间的测试中做一下自动位置调试，从pom树进行顶层扫描
    page.locator("#Shape3").click()
    # page.locator("#rectBottom").click()
    # background - color: grey;
    thebeta = 'background-color: grey;'
    while (thebeta == 'background-color: grey;'):
        logger.info(thebeta)
        thebeta = page.locator('#submitButton').get_attribute('style')
        logger.info(thebeta)
        time.sleep(3)
    page.get_by_role("link", name="授权登录").click()
    logger.info("验证通过,机器人已成功进入登录状态")

    time.sleep(3)
    # page.locator('#myInvoice > a').click()
    time.sleep(2)

    # 这里需要增加一个对页面是否展示的分页判断
    logger.info("输出标识")

    # 以接口的形式获取所有的http请求 避免前端翻页出问题挂掉
    listurlc = []
    listnamec = []
    listthenotecardc = []
    listthecarnnotec = []
    listzardc = []
    dream = 1
    pageNo = 1
    while (dream != 0):

        resp = page.request.post(
            url="https://pss.txffp.com/pss/app/login/invoice/query/card",
            params={
                'pageNo': pageNo,
                'changeView': 'card',
                # 'cardId':listzard[io],
                # 'a1eb4e3c1804464da55d07e37e99eb97',
                'userType': 'COMPANY',
                # 'month': 202311
                # 'month': beginTime
            },
            headers={
                'Content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                              ' x64) AppleWebKit/537.36 (KHTML, like'
                              ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }
        )
        rqg = resp.body().decode()
        logger.info(resp.body().decode())
        time.sleep(1)
        html = rqg
        soup = BeautifulSoup(html, 'lxml')

        thecount = len(soup.select(".etc_card_dl"))
        logger.info(thecount)

        if (thecount == 0):
            dream -= 1

        # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置

        for i in range(1, thecount + 1):
            thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

            thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                0].text.replace('记账卡：', '').replace(' ', '').strip()

            thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

            thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
            thedetailurl = 'https://pss.txffp.com/' + thedetailurla
            thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace('/COMPANY',
                                                                                                          '')
            logger.info(thename, thenotecard, thecarnote, thedetailurla)
            listurlc.append(thedetailurl)
            listnamec.append(thename)
            listthenotecardc.append(thenotecard)
            listthecarnnotec.append(thecarnote)
            listzardc.append(thedetailurla)
        # thecount = len(soup.find_all('a',class_='etc_card_dl'))
        pageNo += 1
        logger.info(pageNo)

    logger.info("finish")
    logger.info(listzardc)
    logger.info(listthecarnnotec)

    logger.info(len(listzardc))
    logger.info(len(listthecarnnotec))

    time.sleep(1.5)
    if (len(listzardc) == 0):
        # 以接口的形式获取所有的http请求 避免前端翻页出问题挂掉
        listurlc = []
        listnamec = []
        listthenotecardc = []
        listthecarnnotec = []
        listzardc = []
        dream = 1
        pageNo = 1
        while (dream != 0):

            resp = page.request.post(
                url="https://pss.txffp.com/pss/app/login/invoice/query/card",
                params={
                    'pageNo': pageNo,
                    'changeView': 'card',
                    # 'cardId':listzard[io],
                    # 'a1eb4e3c1804464da55d07e37e99eb97',
                    'userType': 'COMPANY',
                    # 'month': 202311
                    # 'month': beginTime
                },
                headers={
                    'Content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                  ' x64) AppleWebKit/537.36 (KHTML, like'
                                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                }
            )
            rqg = resp.body().decode()
            logger.info(resp.body().decode())
            time.sleep(1)
            html = rqg
            soup = BeautifulSoup(html, 'lxml')

            thecount = len(soup.select(".etc_card_dl"))
            logger.info(thecount)

            if (thecount == 0):
                dream -= 1

            # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置

            for i in range(1, thecount + 1):
                thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

                thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                    0].text.replace('记账卡：', '').replace(' ', '').strip()

                thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                    0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

                thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                    '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
                thedetailurl = 'https://pss.txffp.com/' + thedetailurla
                thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace(
                    '/COMPANY', '')
                logger.info(thename, thenotecard, thecarnote, thedetailurla)
                listurlc.append(thedetailurl)
                listnamec.append(thename)
                listthenotecardc.append(thenotecard)
                listthecarnnotec.append(thecarnote)
                listzardc.append(thedetailurla)
            # thecount = len(soup.find_all('a',class_='etc_card_dl'))
            pageNo += 1
            logger.info(pageNo)

        logger.info("finish")
        logger.info(listzardc)
        logger.info(listthecarnnotec)

        logger.info(len(listzardc))
        logger.info(len(listthecarnnotec))

    # 以公司形式
    # 以接口的形式获取所有的http请求 避免前端翻页出问题挂掉
    listurl = []
    listname = []
    listthenotecard = []
    listthecarnnote = []
    listzard = []
    dream = 1
    pageNo = 1
    while (dream != 0):

        resp = page.request.post(
            url="https://pss.txffp.com/pss/app/login/invoice/query/card",
            params={
                'pageNo': pageNo,
                'changeView': 'card',
                'userType': 'PERSONAL',
            },
            headers={
                'Content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                              ' x64) AppleWebKit/537.36 (KHTML, like'
                              ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }
        )
        rqg = resp.body().decode()
        logger.info(resp.body().decode())
        time.sleep(1)
        html = rqg
        soup = BeautifulSoup(html, 'lxml')

        thecount = len(soup.select(".etc_card_dl"))
        logger.info(thecount)

        if (thecount == 0):
            dream -= 1

        # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置

        for i in range(1, thecount + 1):
            thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

            thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                0].text.replace('记账卡：', '').replace(' ', '').strip()

            thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

            thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
            thedetailurl = 'https://pss.txffp.com/' + thedetailurla
            thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace('/PERSONAL',
                                                                                                          '')
            logger.info(thename, thenotecard, thecarnote, thedetailurla)
            listurl.append(thedetailurl)
            listname.append(thename)
            listthenotecard.append(thenotecard)
            listthecarnnote.append(thecarnote)
            listzard.append(thedetailurla)
        # thecount = len(soup.find_all('a',class_='etc_card_dl'))
        pageNo += 1
        logger.info(pageNo)

    logger.info("finish")
    logger.info(listzard)
    logger.info(listthecarnnote)

    logger.info(len(listzard))
    logger.info(len(listthecarnnote))

    if (len(listzard) == 0):

        listurl = []
        listname = []
        listthenotecard = []
        listthecarnnote = []
        listzard = []
        dream = 1
        pageNo = 1
        while (dream != 0):

            resp = page.request.post(
                url="https://pss.txffp.com/pss/app/login/invoice/query/card",
                params={
                    'pageNo': pageNo,
                    'changeView': 'card',
                    # 'cardId':listzard[io],
                    # 'a1eb4e3c1804464da55d07e37e99eb97',
                    'userType': 'PERSONAL',
                    # 'month': 202311
                    # 'month': beginTime
                },
                headers={
                    'Content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                  ' x64) AppleWebKit/537.36 (KHTML, like'
                                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                }
            )
            rqg = resp.body().decode()
            logger.info(resp.body().decode())
            time.sleep(1)
            html = rqg
            soup = BeautifulSoup(html, 'lxml')
            # thecount = len(soup.select(".div_wdfp"))  实际点位在第二顺位
            # tile > dl:nth-child(2) > div > a > dd:nth-child(3)
            # tile > dl:nth-child(1) > div > a > dd:nth-child(3)

            thecount = len(soup.select(".etc_card_dl"))
            logger.info(thecount)

            if (thecount == 0):
                dream -= 1
            # 如果发现数量是0，就再请求一次，再次设置一个timeout = 5000 的延时设置

            for i in range(1, thecount + 1):
                thename = soup.select('#tile > dl:nth-child(' + str(i) + ') > div > a > dt')[0].text.strip()

                thenotecard = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(2)")[
                    0].text.replace('记账卡：', '').replace(' ', '').strip()

                thecarnote = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a > dd:nth-child(3)")[
                    0].text.replace('车牌号：', '').replace('已注销', '').replace(' ', '').strip()

                thedetailurla = soup.select("#tile > dl:nth-child(" + str(i) + ") > div > a")[0].get('href').replace(
                    '车牌号：', '').replace('已注销', '').replace(' ', '').strip()
                thedetailurl = 'https://pss.txffp.com/' + thedetailurla
                thedetailurla = thedetailurla.replace('/pss/app/login/invoice/query/queryApply/', '').replace(
                    '/PERSONAL', '')
                logger.info(thename, thenotecard, thecarnote, thedetailurla)
                listurl.append(thedetailurl)
                listname.append(thename)
                listthenotecard.append(thenotecard)
                listthecarnnote.append(thecarnote)
                listzard.append(thedetailurla)
            # thecount = len(soup.find_all('a',class_='etc_card_dl'))
            pageNo += 1
            logger.info(pageNo)

        logger.info("finish")
        logger.info(listzard)
        logger.info(listthecarnnote)

        logger.info(len(listzard))
        logger.info(len(listthecarnnote))

    for io in range(0, len(listzard)):
        carflagname = listthecarnnote[io]

        time.sleep(2)

        def convert_cookies_to_string(cookies):
            cookie_string = ""
            for cookie in cookies:
                cookie_name = cookie['name']
                cookie_value = cookie['value']
                cookie_string += f"{cookie_name}={cookie_value}; "
            return cookie_string.rstrip("; ")

        resp = page.request.post(
            url="https://pss.txffp.com/pss/app/login/invoice/query/queryTrade",
            params={
                'pageSize': 150,
                'cardId': listzard[io],
                # 'a1eb4e3c1804464da55d07e37e99eb97',
                'userType': 'PERSONAL',
                # 'month': 202311
                'month': beginTime
            },
            headers={
                'Content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                              ' x64) AppleWebKit/537.36 (KHTML, like'
                              ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                # 'Cookie': 'SPECIAL=0; _uab_collina=170270617822542426136004; JSESSIONID=213C43D82BB6200DC5B45920390A4359-n1.Tomcat1; acw_tc=2f624a5317027061708857043e12c16afef236efe7eb38a6009e425b104a23; ROUTEID=.1; Hm_lvt_ace551531ab621f3c1447c9e7eb97a68=1702706178; u_asec=099%23KAFEFGEKE55EJETLEEEEEpEQz0yFn6VFDryMC6PHScJYW60wSX9oa6PhDcTXE7EFEE1Cb%2FQTEEjtBKlVjYFET%2FdEsyaStqMTEpUEbspT%2FqYWcR4f9BZ4Ds4BcLARxWxpbyXZNdWczQ%2BGcw%2BBaMZaZLXBPwf3LynXbzXQrYPcOMpQrOIVFEp4Dw2dNswu1s21bz8A8q1uQ67yhLpGlluGYKrC80bREcZIq0CyNdMwgPkvKWE8YoCYDw%2BVJ0ftae95HaUdqS%2Fcuz8nPzoQLUss8LYQNa26%2BsniNs7ncQSqPtpBrReCigws8REVqz9hEQymzCXYKNGTEELlluGGgyMCMXQTEEoFluWtA9i7sEFEp3llsiySt3lulllU%2F3iSTwlllu%2Bdt37F3lllWRaStE7llllUO9iS1pwUE7TxEN6zEF2cqLHopDvkcXToRhj2LFDkWhj2qiNB%2BZ%2BtMJ6Ef7z05c7ZB14bkfMu%2BwD4kLpqmC1GkLIDBEro6rqa6iFbvfP%2BbxEGcZKMnhsDqiFWot7TEEilluCV; Hm_lpvt_ace551531ab621f3c1447c9e7eb97a68=1702706253'
                #     'SPECIAL=0; _uab_collina=170270588358086097538161; JSESSIONID=063ACADE5B974F6A627C1938B7B8FC25-n1.Tomcat1; acw_tc=76b20ffa17027058756123930e3c8aeef01c9db16bd85745917abdddad7dd5; ROUTEID=.1; Hm_lvt_ace551531ab621f3c1447c9e7eb97a68=1702705884; u_asec=099%23KAFEnGEKE74EhYTLEEEEEpEQz0yFn6VFDry5Q60wSXLIW6DhScJoa60HlYFETKxqAjJUE7TxEEu1EFyv6i58060q3MYb0HUALmoZeZj2qijB1ZWcqijo3mvkcrKoK8j2iIDkukj2qi0BinkGkLFSBEP05c7SBwDxJ0A%2BrZMr0n3ykS%2BtMJ61ybMTEhs5WG1maquYSpXfNV9cLeXKU6YaqdQtPt%2BVNL%2BVLvZDA2xR6OXRwRem%2FfqsPGCpb0WNSRIVFJZnDey1NCYwjU9I8Pb86ql3z69rG0oQLUsWLeapqaYt%2BO%2FkuQrVrBSpz6isNsXawFnsNOBybRqRYmGTEELStEErvKFyOrQTEE9ZtYYEnInTsEFEpE%2FStGdx7GlFt377luZdt%2ByStTwlsyaZK%2FiSF3lP%2F3M8t37qAcZddsNhE7Eht3alluZdBYFET6i5EEw5E7EFt37EFE%3D%3D; Hm_lpvt_ace551531ab621f3c1447c9e7eb97a68=1702705885'
            }

        )
        rqg = resp.body().decode()
        logger.info(resp.body().decode())
        time.sleep(1)

        # taiji_search_data > div > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(1)
        # rqg.encoding = chardet.detect(rqg.content)['encoding'] #requests请求过程
        # 初始化HTML
        html = rqg
        soup = BeautifulSoup(html, 'lxml')  # 生成BeautifulSoup对象
        logger.info('输出格式化的BeautifulSoup对象：', soup.prettify())
        # logger.info('输出具体数量的节点个数：',soup.find_all("div_wdfp").count)

        # logger.info('输出具体数量的节点个数：',len(soup.select(".div_wdfp")))

        thecount = len(soup.select(".div_wdfp"))
        # logger.info('输出具体数量的节点个数：',soup.select("div_wdfp"))

        theall = []
        # 分析捕获页签的交易时间
        for i in range(1, thecount + 1):
            tradetime = \
                soup.select(
                    '#taiji_search_data > div:nth-child(' + str(i) + ') > div.div_wdfp_t > ul > li:nth-child(1)')[
                    0].text.replace('交易时间：', '')
            trademoney = soup.select(
                '#taiji_search_data > div:nth-child(' + str(i) + ') > div.div_wdfp_t > ul > li:nth-child(2) > span')[
                0].text.replace('￥', '').replace('\n', '').replace('\t', '')
            trademoney = trademoney.replace(',', '').replace('，', '')
            # 转换为浮点数

            tradestartprovince = soup.select('#taiji_search_data > div:nth-child(' + str(
                i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(1)')[0].text
            tradeendprovince = soup.select('#taiji_search_data > div:nth-child(' + str(
                i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(3) > div:nth-child(1)')[0].text
            tradestart = soup.select('#taiji_search_data > div:nth-child(' + str(
                i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(2)')[0].text
            tradeend = soup.select('#taiji_search_data > div:nth-child(' + str(
                i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(3) > div:nth-child(2)')[0].text
            # taiji_search_data > div:nth-child(2) > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(2)
            logger.info(tradetime, trademoney, tradestartprovince, tradeendprovince, tradestart, tradeend)

            # 生成的唯一识别串
            # 待加密信息
            saika = username + carflagname + tradetime + trademoney + tradestart + tradeend
            # 创建md5对象
            hl = hashlib.md5()
            # 更新hash对象的值，如果不使用update方法也可以直接md5构造函数内填写
            # md5_obj=hashlib.md5("123456".encode("utf-8")) 效果一样
            hl.update(saika.encode("utf-8"))
            logger.info('MD5加密前为 ：' + saika)
            theencrypt = hl.hexdigest()
            logger.info('MD5加密后为 ：' + theencrypt)

            themessdetail = {
                # "etcCardNo": "ETC记账卡号",
                "etcAccount": username,
                "driverLicensePlateNo": listthecarnnote[io],
                "etcDataId": theencrypt,
                "etcCardType": 1,
                # //ETC卡类型（1：个人卡，2：单位卡）
                "etcCardNo": listthenotecard[io],
                "paymentAmount": trademoney,
                # //交易金额（元）
                "paymentTime": tradetime,
                # //交易时间
                "inboundProvince": tradestartprovince,
                "inboundAddress": tradestart,
                "outboundProvince": tradeendprovince,
                "outboundAddress": tradeend
            }
            theall.append(themessdetail)

        if (theall == []):
            theall = None

        main_card_msg = {
            "etcAccount": username,
            "ssoOrgId": ssoOrgId,
            # "driverLicensePlateNo":pp,
            "data": theall
        }
        logger.info("输出本次json的信息")
        logger.info(main_card_msg)
        my_mq.publish('TXFFP_SEND_TO_WOX_QUE', json.dumps(main_card_msg, ensure_ascii=False))

        # 每次访问设置下间隔，不要太过分
        time.sleep(3)

    logger.info("输出公司级别的内容")

    logger.info("开始执行开票部分")

    try:

        for io in range(0, len(listzardc)):

            carflagname = listthecarnnotec[io]

            time.sleep(2)

            def convert_cookies_to_string(cookies):
                cookie_string = ""
                for cookie in cookies:
                    cookie_name = cookie['name']
                    cookie_value = cookie['value']
                    cookie_string += f"{cookie_name}={cookie_value}; "
                return cookie_string.rstrip("; ")

            resp = page.request.post(
                url="https://pss.txffp.com/pss/app/login/invoice/query/queryTrade",
                params={
                    'pageSize': 150,
                    'cardId': listzardc[io],
                    # 'a1eb4e3c1804464da55d07e37e99eb97',
                    'userType': 'COMPANY',
                    # 'month': 202311
                    'month': beginTime
                },
                headers={
                    'Content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                                  ' x64) AppleWebKit/537.36 (KHTML, like'
                                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
                }

            )
            rqg = resp.body().decode()
            logger.info(resp.body().decode())

            # taiji_search_data > div > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(1)

            # rqg.encoding = chardet.detect(rqg.content)['encoding'] #requests请求过程
            # 初始化HTML
            html = rqg
            soup = BeautifulSoup(html, 'lxml')  # 生成BeautifulSoup对象
            logger.info('输出格式化的BeautifulSoup对象：', soup.prettify())
            # logger.info('输出具体数量的节点个数：',soup.find_all("div_wdfp").count)

            # logger.info('输出具体数量的节点个数：',len(soup.select(".div_wdfp")))

            thecount = len(soup.select(".div_wdfp"))
            # logger.info('输出具体数量的节点个数：',soup.select("div_wdfp"))

            theall = []
            # 分析捕获页签的交易时间
            for i in range(1, thecount + 1):
                tradetime = soup.select(
                    '#taiji_search_data > div:nth-child(' + str(i) + ') > div.div_wdfp_t > ul > li:nth-child(1)')[
                    0].text.replace('交易时间：', '')
                trademoney = soup.select('#taiji_search_data > div:nth-child(' + str(
                    i) + ') > div.div_wdfp_t > ul > li:nth-child(2) > span')[0].text.replace('￥', '').replace('\n',
                                                                                                              '').replace(
                    '\t', '')
                trademoney = trademoney.replace(',', '').replace('，', '')
                # 转换为浮点数
                tradestartprovince = soup.select('#taiji_search_data > div:nth-child(' + str(
                    i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(1)')[0].text
                tradeendprovince = soup.select('#taiji_search_data > div:nth-child(' + str(
                    i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(3) > div:nth-child(1)')[0].text
                tradestart = soup.select('#taiji_search_data > div:nth-child(' + str(
                    i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(2)')[0].text
                tradeend = soup.select('#taiji_search_data > div:nth-child(' + str(
                    i) + ') > div.div_wdfp_c > ul > li.li2 > div:nth-child(3) > div:nth-child(2)')[0].text
                # taiji_search_data > div:nth-child(2) > div.div_wdfp_c > ul > li.li2 > div:nth-child(1) > div:nth-child(2)
                logger.info(tradetime, trademoney, tradestartprovince, tradeendprovince, tradestart, tradeend)
                # 生成的唯一识别串
                # 待加密信息
                saika = username + carflagname + tradetime + trademoney + tradestart + tradeend
                # 创建md5对象
                hl = hashlib.md5()
                # 更新hash对象的值，如果不使用update方法也可以直接md5构造函数内填写
                # md5_obj=hashlib.md5("123456".encode("utf-8")) 效果一样
                hl.update(saika.encode("utf-8"))
                logger.info('MD5加密前为 ：' + saika)
                theencrypt = hl.hexdigest()
                logger.info('MD5加密后为 ：' + theencrypt)

                themessdetail = {
                    # "etcCardNo": "ETC记账卡号",
                    "etcAccount": username,
                    "driverLicensePlateNo": listthecarnnotec[io],
                    "etcDataId": theencrypt,
                    "etcCardType": 2,
                    # //ETC卡类型（1：个人卡，2：单位卡）
                    "etcCardNo": listthenotecardc[io],
                    "paymentAmount": trademoney,
                    # //交易金额（元）
                    "paymentTime": tradetime,
                    # //交易时间
                    "inboundProvince": tradestartprovince,
                    "inboundAddress": tradestart,
                    "outboundProvince": tradeendprovince,
                    "outboundAddress": tradeend
                }
                theall.append(themessdetail)

            if (theall == []):
                theall = None

            main_card_msg = {
                "etcAccount": username,
                "ssoOrgId": ssoOrgId,
                # "driverLicensePlateNo":pp,
                "data": theall
            }
            logger.info("输出本次json的信息")
            logger.info(main_card_msg)
            my_mq.publish('TXFFP_SEND_TO_WOX_QUE', json.dumps(main_card_msg, ensure_ascii=False))

            # 每次访问设置下间隔，不要太过分
            time.sleep(3)
    except Exception as e:
        logger.info(e)


if __name__ == '__main__':
    # global_config = IniReader('config.ini')
    # mq_ip = global_config.get_value('rabbitMq', 'ip')
    # mq_port = global_config.get_value('rabbitMq', 'port')
    # mq_usr = global_config.get_value('rabbitMq', 'USR')
    # mq_passwd = global_config.get_value('rabbitMq', 'passwd')
    # mq_vhost = global_config.get_value('rabbitMq', 'vhost')
    # mq_exchange = global_config.get_value('rabbitMq', 'exchange')

    mq_ip = '10.200.51.64'
    mq_port = '5672'
    mq_usr = 'rpa'
    mq_passwd = 'rpa'
    mq_vhost = 'wox'
    mq_exchange = 'wox.rpa'

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    logger.add("ETC-logs/" + f'{today}.log', rotation="1 day", retention="7 days")
    # logger.add("my_log_{time}.log", rotation="1 day", retention="7 days")
    logger.info(mq_ip, mq_port, mq_usr, mq_passwd, mq_vhost, mq_exchange)
    my_mq = RabbitMQ(mq_ip, mq_port, mq_usr, mq_passwd, mq_vhost, mq_exchange)
    while True:
        messages = my_mq.consume("WOX_SEND_TO_TXFFP_QUE")
        for i in messages:
            message = json.loads(i)
            logger.info(message)
            username = message["msgBody"]['username']
            password = message["msgBody"]['password']
            beginTime = message["msgBody"]['beginTime']
            ssoOrgId = message["msgBody"]['ssoOrgId']
            logger.info(username, password, beginTime)
            try:

                with sync_playwright() as playwright:

                    runweikaipiao(playwright, username, password, beginTime, ssoOrgId)
                dd_robot(msg=username + '账号的' + str(ssoOrgId) + '组织的' + beginTime + '未开票任务已结束')

                with sync_playwright() as playwright:
                    runyikaipiao(playwright, username, password, beginTime, ssoOrgId)
                dd_robot(msg=username + '账号的' + str(ssoOrgId) + '组织的' + beginTime + '已开票任务已结束')

                # main_card_msg = {
                #         "etcAccount": username,
                #         "data":  'Finish'
                #         }
                # logger.info("作为任务结束的标识输出json的信息")
                # logger.info(main_card_msg)
                # my_mq.publish('TXFFP_SEND_TO_WOX_QUE', json.dumps(main_card_msg, ensure_ascii=False))

            except Exception as e:
                logger.info(e)
                dd_robot(msg=username + '账号的' + beginTime + '任务出现故障，需要人工介入' + str(e))

            # logger.info("目前队列为空，准备下次执行")
            time.sleep(3)

            # 这里有一个点需要注意，车牌号可以直接获取得到的