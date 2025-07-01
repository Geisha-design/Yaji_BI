import json
import time

import requests
from DrissionPage._configs.chromium_options import ChromiumOptions
from DrissionPage._configs.session_options import SessionOptions
from DrissionPage._pages.session_page import SessionPage
from DrissionPage._pages.web_page import WebPage
from loguru import logger

def rpapage():
    # theheadless = str(baseConfig('config','headless'))
    # if theheadless == 'false' or theheadless=='False':
    #     co = ChromiumOptions()
    # else:
    #     co = ChromiumOptions().headless()
    co = ChromiumOptions()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)

    # cookies ={'CNZZDATA1254842228': '312209262-1748338472-%7C1748339174', 'qcc_did': '9a6150d3-d156-41e8-b955-53993f4ed4a9', 'tfstk': 'gY1nwdDgVhibKRE9B1OQ3L4kjm299BOWQghJ2QKzQh-svDhdzQ-l4hCpvwdE4bjlbHIdpa3CCiQq96eBwbABNQrYDSFYdwOWaSBxJaxC7NTzWerz5lnpNQrYXpfVhPO5Yv7g5g7aSUL-TbSyUFRwfEMeaHJrbA82bQRyLeJw7ELr8v8ELPbwfURy4gRzSC-6zUbxLnCP31r9TI3brhvGsevH0N2jabXIMpxV8hcz01Y34n7ejblkmCy9_aSzqbdVhGfk3iFo1BQcQC8hIzkwYKXFvFsuiX-Fsw5ev6rt9H5C7tCRbzlyqOW2Ut7UXAYGQwCMBsrmZp6NAt9lwlFX9tQANK5Utmt9hUjDTOqZtiSzSAk4f-hW7zCZFY9e5FxA1FP3TynbExagSxQWLFTXDP4iF2pe5FxYSPDYsp86lnC..', 'QCCSESSID': '19f86e3d84173885e00e42504f', 'UM_distinctid': '1971117f584135-067f0ce6af65de-19525636-384000-1971117f585395d', 'acw_tc': '1a0c384e17483384716828797e00826216c22dd9f060c339b4eecb68f5f23d'}


    # 设置cookies
    # session_page.set_cookies(cookies)
    # if theheadless == 'false' or theheadless=='False' :
    #     logger.info("进入目标网址(有头模式)"+"https://xb-node.amazon.cn/")。          https://www.tianyancha.com/nsearch?key=%E4%B8%AD%E5%9B%BD%E7%A6%8F%E9%A9%AC%E6%9C%BA%E6%A2%B0%E9%9B%86%E5%9B%A2%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8
    # else:
    #     logger.info("进入目标网址(无头模式)"+"https://xb-node.amazon.cn/")


    # page.get('https://www.tianyancha.com/nsearch?key=%E4%B8%AD%E9%92%A2%E8%AE%BE%E5%A4%87%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8')

    # page.get("https://www.qcc.com/web/search?key=中建材国际贸易有限公司")
    # page.ele("xpath://html/body/div/div[2]/div[2]/div[3]/div/div[2]/div/table/tr[1]/td[3]/div[2]/span/span[1]/a/span").click()
    #
    # print(page.url)

    # page.get("https://www.qcc.com/api/search/searchOther?searchKey=%E6%98%93%E8%B1%B9%E7%BD%91%E7%BB%9C%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8")
    # page2 = SessionPage(session_or_options=so)
    # page2.get("https://www.qcc.com/web/search?key=易豹网络科技有限公司")
    # 获取内置的 Session 对象
    # session = page.session
    # # 以 head 方式发送请求
    # response = session.head('https://www.qcc.com/api/search/searchOther?searchKey=%E6%98%93%E8%B1%B9%E7%BD%91%E7%BB%9C%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8')
    # print(response.headers)
    # print(response.text)


    page.get(url='https://www.tianyancha.com/company/16609165')
    manageStatus = page.ele(
        "xpath://html/body/div/div[2]/div[4]/div[1]/div/div[2]/section[2]/div[2]/div[2]/table/tr[2]/td[4]").text
    print(manageStatus)

    # page.ele("#page-header > div > div.tyc-header-middle > div > div > div.tyc-header-suggest-input.tyc-header-suggest-input-reset._e3f88._44c65 > input").input("中钢设备有限公司")
    # page.ele("天眼一下").click()



    # time.sleep(15)
    # logger.info('第一次cookie状态检测')
    # #cookiea = page.cookies(as_dict=True)
    # cookiea = page.cookies()
    # cookieas = cookiea
    # dictionary = {cookie['name']: cookie['value'] for cookie in cookiea}
    # cookiea = dictionary
    # logger.info(cookiea)
    # logger.info('登录标识状态A')
    # logger.info(cookiea.get('sess-at-main'))
    # if cookiea.get('sess-at-main') is None:
    #     page.ele(rpacapture('location','账号')).input(baseConfig('config','username'))
    #     randomSleep()
    #     page.ele(rpacapture('location','密码')).input(baseConfig('config','password'))
    #     randomSleep()
    #     # 这个按钮标签为了稳定安全考虑 后续更换为点控式按钮
    #     page.ele(rpacapture('location','登录')).click()
    #     randomSleep()
    # logger.info('第二次cookie状态检测')
    # cookieb = page.cookies()
    # dictionary = {cookie['name']: cookie['value'] for cookie in cookieb}
    # cookieb = dictionary
    # logger.info(cookieb)
    # logger.info('登录标识状态B  ')
    # logger.info(cookieb.get('sess-at-main'))
    # 此段逻辑针对特殊验证码 ， 在一些极端情况会出现 要予以解决
    # 极端情况下的验证码情况需要处理的逻辑
    # ele = page.ele(rpacapture('location','验证码图片位置'),timeout=3)
    # 出现极端情况的OCR识别工具
    # if ele:
    #     page.ele(rpacapture('location','验证码图片位置')).get_screenshot('thescreen.png')
    #     # OCR识别模块
    #     with open("thescreen.png", 'rb') as f:
    #         img_bytes = f.read()
    #     ocr = AOSCCOCR.AosccOcr()
    #     poses = ocr.classification(img_bytes)
    #     logger.info(poses)
    #     page.ele(rpacapture('location','验证码文字输入框')).input(poses)
    #     page.wait(2)
    #     page.ele(rpacapture('location','验证码确认')).click()
    #     ele2 = page.ele(rpacapture('location','验证码通过标识'),timeout=3)
    #     while ele2:
    #         ele2 = page.ele(rpacapture('location','验证码通过标识'), timeout=3)
    #         ele2.click()
    #         page.ele(rpacapture('location','验证码图片位置')).get_screenshot('thescreen.png')
    #         randomSleep()
    #         # OCR识别模块
    #         with open("thescreen.png", 'rb') as f:
    #             img_bytes = f.read()
    #         ocr = SmartebaoRPA.AOSCCOCR.AosccOcr()
    #         poses = ocr.classification(img_bytes)
    #         logger.info(poses)
    #         page.ele(rpacapture('location','验证码文字输入框')).input(poses)
    #         page.wait(2)
    #         page.ele(rpacapture('location','验证码确认')).click()
    #         randomSleep()
    #         ele2 = page.ele(rpacapture('location','验证码通过标识'), timeout=3)

    # cookie_str = "; ".join([f"{key}={value}" for key, value in cookieb.items()])
    # print(cookie_str)
    # 定义URL和查询参数
    # payload ={
    #     'mindType': 9,
    #     'pageSize': 5,
    #     'person': 'true',
    #     'searchKey': '易豹网络科技有限公司',
    #     'suggest': 'true'
    # }
    # response = page.session.get('https://www.qcc.com/api/search/searchMind',cookies=cookiea,params=payload)
    # logger.info(response.status_code)
    # logger.info(response.encoding)
    # logger.info(response.url)
    # logger.info(response.text)

    # headers = {"Cookie": cookiea}
    # payload ={
    #     'mindType': 9,
    #     'pageSize': 5,
    #     'person': 'true',
    #     'searchKey': '易豹网络科技有限公司',
    #     'suggest': 'true'
    # }
    #
    # # payload = {"referenceId": "AL2411150053"}
    # response = requests.get("https://www.qcc.com/api/search/searchMind", params=payload,cookies=cookiea)
    #
    # logger.info(response.status_code)
    # logger.info(response.encoding)
    # logger.info(response.url)
    # logger.info(response.text)
    # thejson = json.loads(response.text)
    # print(thejson)
    # logger.info(thejson)




    # url = 'https://www.qcc.com/api/search/searchMind'
    # params = {
    #     'mindType': 9,
    #     'pageSize': 5,
    #     'person': 'true',
    #     'searchKey': '易豹网络科技有限公司',
    #     'suggest': 'true'
    # }
    #
    # # 发送GET请求
    # response = requests.get(url, params=params,cookies=cookiea)
    #
    # # 检查响应状态码
    # if response.status_code == 200:
    #     # 解析响应内容（假设响应内容为JSON格式）
    #     data = response.json()
    #     print(data)
    # else:
    #     print(f'请求失败，状态码：{response.status_code}')
    return page

if __name__ == '__main__':
    rpapage()

    # https: // www.qcc.com / api / user / getUserCompanyInfo
    # https: // www.qcc.com / firm / f2e88bddabe8a375ac3e195bc56df106.html