# -*- coding: utf-8 -*-
import time
import pymysql
from loguru import logger
from pymysql.cursors import DictCursor
# from rpacapture import *
from DrissionPage import WebPage, ChromiumOptions, SessionOptions
def fetch_company_names_in_batches_url(batch_size=10, start_offset=0):

    """

    分批查询 company_name

    :param batch_size: 每批查询的记录数，默认为10

    :param start_offset: 从第几行开始读取，默认为0

    :return: 生成器，每次返回一个批次的 company_name 列表

    """

    try:
        connection = pymysql.connect(
            host='127.0.0.1',  # 数据库主机地址
            user='root',  # 数据库用户名
            password='qyzh12260315',  # 数据库密码
            database='rpa',  # 数据库名称
            cursorclass=DictCursor
        )
        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM company_goods_info")

            total_records = cursor.fetchone()['COUNT(*)']

            offset = start_offset  # 从指定的起始偏移量开始



            while offset < total_records:

                cursor.execute(f"SELECT contact_url,id,company_name FROM company_goods_info LIMIT {batch_size} OFFSET {offset}")

                batch = [(row['contact_url'], row['id'],row['company_name']) for row in cursor.fetchall()]


                yield batch

                offset += batch_size

    except Exception as e:

        print(f"发生错误：{e}")

    finally:

        if connection.open:

            connection.close()


def fetch_company_names_in_batches(batch_size=10, start_offset=0):

    """

    分批查询 company_name

    :param batch_size: 每批查询的记录数，默认为10

    :param start_offset: 从第几行开始读取，默认为0

    :return: 生成器，每次返回一个批次的 company_name 列表

    """

    try:

        connection = pymysql.connect(

            host='127.0.0.1',  # 数据库主机地址

            user='root',  # 数据库用户名

            password='qyzh12260315',  # 数据库密码

            database='rpa',  # 数据库名称

            cursorclass=DictCursor

        )



        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM company_info")

            total_records = cursor.fetchone()['COUNT(*)']

            offset = start_offset  # 从指定的起始偏移量开始



            while offset < total_records:

                cursor.execute(f"SELECT company_name FROM company_info LIMIT {batch_size} OFFSET {offset}")

                batch = [row['company_name'] for row in cursor.fetchall()]

                yield batch

                offset += batch_size

    except Exception as e:

        print(f"发生错误：{e}")

    finally:

        if connection.open:

            connection.close()

def update_company_info(company_name, new_data):

    """

    更新指定 company_name 的公司信息记录

    :param company_name: 要更新的公司名称

    :param new_data: 包含要更新字段及其新值的字典

    """

    try:

        connection = pymysql.connect(

            host='127.0.0.1',  # 数据库主机地址

            user='root',  # 数据库用户名

            password='qyzh12260315',  # 数据库密码

            database='rpa',  # 数据库名称

            cursorclass=DictCursor

        )



        with connection.cursor() as cursor:

            # 构建动态更新语句

            update_columns = ', '.join([f"{key} = %s" for key in new_data.keys()])

            update_values = list(new_data.values())

            update_values.append(company_name)  # 添加公司名称作为查询条件



            update_query = f"""

            UPDATE company_info

            SET {update_columns}

            WHERE company_name = %s

            """

            cursor.execute(update_query, update_values)

            connection.commit()

            print(f"更新成功，影响的行数：{cursor.rowcount}")

    except Exception as e:

        print(f"发生错误：{e}")

    finally:

        if connection.open:

            connection.close()



def factory_info_get(url,name):
    co = ChromiumOptions().auto_port()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)
    logger.info(
        "进入目标网址(有头模式)" + "https://cn.made-in-china.com/companysearch.do?subaction=hunt&mode=and&style=b&code=EEnxEJQbMJmm&comProvince=nolimit&miccnsource=1&word=%C9%CF%BA%A3%C9%EC%B2%C5%BD%F8%B3%F6%BF%DA%D3%D0%CF%DE%B9%AB%CB%BE")
    time.sleep(3)
    # page.get(
    #     'https://sale.1688.com/factory/l6rr893d.html?spm=a262cb.19918180.ljxo5qvc.6.1a142e19H4oiVF&memberId=00chenyou')
    page.get(
        url)
    infos = page.eles('@class=galleyItemLink')
    print(infos)

    for info in infos:
            print(info.attr('href'))
            # update_factory('上海森克电子科技有限公司', info.attr('href'))
            update_factory(name, info.attr('href'))

    # detail = page.ele('xpath://*[@id="app"]/div/div/div[2]/div[5]/div[1]/div/div/div')

    # if (detail != None):
    #     time.sleep(3)
    #     print(detail)
        # page.get(urllink.link)   //*[@id="galleyListContainer"]/div[1]/div/a[5]/div[1]/img


    # else:
    #     logger.info('url 连接为空 商品信息不存在')

        # time.sleep(3)

def update_factory(company_name, url):

    """
    更新指定 company_name 的公司信息记录

    :param company_name: 要更新的公司名称

    :param new_data: 包含要更新字段及其新值的字典
    """

    try:

        connection = pymysql.connect(

            host='127.0.0.1',  # 数据库主机地址

            user='root',  # 数据库用户名

            password='qyzh12260315',  # 数据库密码

            database='rpa',  # 数据库名称

            cursorclass=DictCursor

        )

        with connection.cursor() as cursor:
            # 构建动态插入语句
            insert_query = """
            INSERT INTO company_goods_info (company_name, contact_url)
            VALUES (%s, %s)
            """
            # 假设 insert_values 是一个元组，包含要插入的值
            insert_values = (company_name, url)
            cursor.execute(insert_query, insert_values)
            connection.commit()
            print(f"插入成功，影响的行数：{cursor.rowcount}")
    except Exception as e:
        print(f"发生错误：{e}")

    finally:
        if connection.open:
            connection.close()

# 示例用法

def saika(company_name):
    co = ChromiumOptions()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)

    logger.info("进入目标网址(有头模式)" + "https://xb-node.amazon.cn/")
    page.get(

        'https://www.qcc.com/web/search?key='+company_name)

    urllink = page.ele(".title copy-value").link

    print(urllink)
    if (urllink != None):

        page.get(urllink)

        detailLink = page.ele("#cominfo")

        madetime = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[2]/td[6]/span/span[1]').text

        lianxiren = page.ele(

            'xpath://html/body/div/div[2]/div[1]/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div[2]/span/span[2]/span[1]/span/span/a').text

        lianxifangshi = page.ele(

            'xpath://html/body/div/div[2]/div[1]/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div[1]/span/span[2]/span[1]/span').text

        jingyingzhuangtai = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[2]/td[4]').text

        xingzhengquhua = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[7]/td[2]/span/span[1]').text

        jianjie = page.ele(

            'xpath://html/body/div/div[2]/div[1]/div[1]/div/div[2]/div/div/span/span/span/div/span/span/span[2]').text

        zhucedizhi = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[9]/td[2]/span[1]').text

        canbaobiaoshi = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[6]/td[4]/span')

        if(canbaobiaoshi):
            canbaorenshu = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[6]/td[4]/span').text
        else:
            canbaorenshu = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[6]/td[4]/div[1]/span').text

        zhuceziben = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[3]/td[2]/span').text
        qiyeleixing = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[5]/td[2]').text
        suoshuhangye = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[8]/td[2]/div/div[1]/span').text
        jingyingfanweiflag = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[10]/td[2]/span/span[1]')
        if(jingyingfanweiflag):
            jingyingfanwei = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[10]/td[2]/span/span[1]').text

        else:
            jingyingfanwei = page.ele('xpath://*[@id="cominfo"]/div[2]/div[2]/table/tr[11]/td[2]/span').text

        # //*[@id="cominfo"]/div[2]/div[2]/table/tr[11]/td[2]/span

        zhuying = jingyingfanwei

        print(madetime)

        print(lianxiren)

        print(lianxifangshi)

        print(jingyingzhuangtai)

        print(xingzhengquhua)

        print(zhucedizhi)

        print(canbaorenshu)

        print(zhuceziben)

        print(qiyeleixing)

        print(suoshuhangye)

        print(jingyingfanwei)

        print(jianjie)

        print(zhuying)


        new_data = {

             "business_status": jingyingzhuangtai,

            "establishment_date": madetime,

            "administrative_division":xingzhengquhua,

             "registered_capital": zhuceziben,

            "company_type":qiyeleixing,

            "industry":suoshuhangye,

            "insured_employees":canbaorenshu,

            "registered_address":zhucedizhi,

            "business_scope":jingyingfanwei,

            "introduction":jianjie,

             "contact_person": lianxiren,

              "contact_info": lianxifangshi,

             "main_business": zhuying

        }

        return new_data



    pass


def rrpp(contact_url,id,company_name):
    co = ChromiumOptions()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)
    logger.info(
        "进入目标网址(有头模式)" + contact_url)
    time.sleep(3)
    page.get(contact_url)

    cc = page.ele('xpath://*[@id="productTitle"]',timeout=1)
    if cc:
        品名 = page.ele('xpath://*[@id="productTitle"]').text  #\37 7450430284092 > div > div.layout-right > div.od-pc-offer-price-contain > div > div > div > div.price-wrapper.wrapper-ver-common > div > div
    else:
        sa = page.ele('xpath://*[@id="13772573015436"]/div/div/div[2]/div[1]/div/div[1]/div',timeout=1)
        if sa:
            品名 = page.ele('xpath://*[@id="13772573015436"]/div/div/div[2]/div[1]/div/div[1]/div').text
        else:
            品名 = page.ele('xpath://*[@id="77450430284092"]/div/div[2]/div[1]/div/div[1]').text
    bb = page.ele('xpath://*[@id="mainPrice"]/div/div/div[1]',timeout=1)


    if bb:
        价格 = page.ele('xpath://*[@id="mainPrice"]/div/div/div[1]').text
    else:
        sa = page.ele('xpath://*[@id="13772573015436"]/div/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div',timeout=1)
        if sa:
            价格 = page.ele('xpath://*[@id="13772573015436"]/div/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div').text
        else:
            价格 = page.ele('xpath://*[@id="77450430284092"]/div/div[2]/div[2]/div/div/div/div[2]/div/div').text

    pp = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[1]/td[1]/span/span',timeout=1)
    if pp:
        尺寸 = page.ele(
            'xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[1]/td[1]/span/span').text
    else:
        vv = page.ele('xpath://*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[1]/span[2]',timeout=2)
        if vv:
            尺寸 = page.ele('xpath://*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[1]/span[2]').text
        else:
            尺寸 = ""


    qq = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[1]/td[2]/span/span',timeout=1)
    if qq:
        货号 = page.ele(
            'xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[1]/td[2]/span/span').text
    else:
        oo = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div/div[4]/span[2]',timeout=1)
        if oo:
            货号 = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div/div[4]/span[2]').text
        else:
            货号 = page.ele('//*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/span[2]').text


    规格 = ''
    加工方式 = ''
    类型 = ''

    # aa = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[2]/td[1]/span/span')
    # if aa:
    #     规格 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[2]/td[1]/span/span').text
    # else:
    #     规格 = page.ele('//*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[3]/span[2]').text
    #
    # zz = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[2]/td[2]/span/span',timeout=3)
    # if zz:
    #     加工方式 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[2]/td[2]/span/span').text
    # else:
    #     加工方式 = page.ele('//*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[4]/span[2]').text
    #
    # ff = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[3]/td[1]/span/span',timeout=3)
    # if ff:
    #     类型 = page.ele(
    #         'xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[3]/td[1]/span/span').text
    # else:
    #     类型 = page.ele(
    #         'xpath://*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[5]/span[2]').text

    ff =page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[3]/td[2]/span/span',timeout=3)
    if ff:
        品牌 = page.ele(
            'xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[3]/td[2]/span/span').text
    else:
        bb = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div/div[1]/span[2]',timeout=2)
        if bb:
            品牌 = page.ele(
                'xpath://*[@id="13772573013169"]/div/div[2]/div/div/div[1]/span[2]').text
        else:
            品牌 = page.ele(
            'xpath://*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[6]/span[2]').text

    使用范围 = ''

    # ff =page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[4]/td[1]/span/span',timeout=3)
    # if ff:
    #     使用范围 = page.ele(
    #         'xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[4]/td[1]/span/span').text
    # else:
    #     使用范围 = page.ele(
    #         'xpath://*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[7]/span[2]').text


    性能 = ''
    作用 = ''


    # ff =page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[4]/td[2]/span/span',timeout=3)
    # if ff:
    #     性能 = page.ele(
    #         'xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[4]/td[2]/span/span').text
    # else:
    #     性能 = page.ele(
    #         'xpath://*[@id="7745043012801"]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[8]/span[2]').text
    #
    # ff =page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[1]/span/span',timeout=3)
    # if ff:
    #     作用 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[1]/span/span').text
    # else:
    #     作用 = ""



    ff =page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[2]/span/span',timeout=3)
    if ff:

        是否跨境出口 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[2]/span/span').text
    else:
        tt = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div/div[3]/span[2]',timeout=2)
        if tt:
            是否跨境出口 = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div/div[3]/span[2]').text

    # ff =page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[6]/td/span/span',timeout=3)
    # if ff:
    #     风格 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[6]/td/span/span').text
    # else:
    #     风格 = ""
    风格 = ''

    rr = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div',timeout=2)
    if  rr:
        完整信息 = page.ele('xpath://*[@id="13772573013169"]/div/div[2]/div/div').text
    else:
        完整信息 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div').text
    print(完整信息)

    # detail - gallery - img
    pho = '';

    cccpj = page.eles('@class=detail-gallery-img')
    if cccpj:
        infos = page.eles('@class=detail-gallery-img')
    else:
        infos = page.eles('@class=od-gallery-img')




    # 所有属性标签的获取操作

    cc = page.eles('@class=ant-descriptions-item-label',timeout=1)
    if cc:
        attriName = page.eles('@class=ant-descriptions-item-label')
        attrivalue = page.eles('@class=ant-descriptions-item-content')


    else:

        attriName = page.eles('@class=offer-attr-item-name')
        attrivalue = page.eles('@class=offer-attr-item-value')






    # print(infos)
    #
    # for info in infos: detail-gallery-img
    #     print(info.attr('src'))

    # 初始化一个列表来存储图片 URL
    photo_urls = []

    # 遍历每个图片元素
    for info in infos:
        # 获取图片的 src 属性
        src = info.attr('src')
        if src:  # 确保 src 不为空
            print(src)
            photo_urls.append(src)  # 将图片 URL 添加到列表中

    # 打印所有图片 URL
    print("所有图片 URL：", photo_urls)
    # 将所有图片 URL 拼接成一个字符串，每个 URL 之间用逗号分隔
    photo_urls_str = ','.join(photo_urls)
        # update_factory('上海森克电子科技有限公司', info.attr('href'))


    # 是否跨境出口 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[2]/span/span').text
    # 风格 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[6]/td/span/span').text
    # 作用 = 1
    # 是否跨境出口 = 1
    # 风格 = 1
    # https: // sell.easyya.com / category?categoryId = 973 & thirdCate = 花洒 & secondCate = 卫浴 & firstCate = 家居家具 & desc = false & sortBy = 0 & current = 1 & size = 20
    #
    # 品牌 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[3]/td[2]/span/span').text
    # 使用范围 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[4]/td[1]/span/span').text
    # 性能 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[4]/td[2]/span/span').text
    # 作用 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[1]/span/span').text
    # 是否跨境出口 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[5]/td[2]/span/span').text
    # 风格 = page.ele('xpath://*[@id="productAttributes"]/div/div/div[3]/div/div/div/table/tbody/tr[6]/td/span/span').text

    print(品名,价格,尺寸,货号,规格,加工方式,类型,品牌,使用范围,性能,作用,是否跨境出口,风格,完整信息)
    # 假设你有一个包含所有字段值的元组

    data = (
        id,
        company_name,  # company_name
        contact_url,  # contact_url
        品名,  # goods_name
        价格,  # goods_price
        尺寸,  # size
        货号,  # goods_numbers
        规格,  # goods_guige
        加工方式,  # made_way
        类型,  # type
        品牌,  # pinpai
        使用范围,  # shiyongfanwei
        性能,  # xingneng
        作用,  # zuoyong
        是否跨境出口,  # shifoukuajing
        风格,  # style
        photo_urls_str,  # photo
        完整信息
    )


    return  data,attriName ,attrivalue,品名,photo_urls_str,价格


def insert_true(company, name,value,id,品名,photo_urls_str,价格):
    data2 = (
        id,
        company,
        name    ,
        value,
        品名 , # goods_name
        photo_urls_str,
        价格
    )
    """
    更新指定 company_name 的公司信息记录

    :param company_name: 要更新的公司名称

    :param new_data: 包含要更新字段及其新值的字典
    """

    try:

        connection = pymysql.connect(

            host='127.0.0.1',  # 数据库主机地址

            user='root',  # 数据库用户名

            password='qyzh12260315',  # 数据库密码

            database='rpa',  # 数据库名称

            cursorclass=DictCursor

        )

        with connection.cursor() as cursor:
            # 构建动态插入语句
            insert_query = """
            INSERT INTO attri (
    id,
    company, 
    name, 
    value, 
    pinming,
    photo_urls_str,
    jiage
) VALUES (
    %s,%s, %s, %s,%s,%s,%s
)
            """
            # 假设 insert_values 是一个元组，包含要插入的值
            # insert_values = (company_name, url)
            cursor.execute(insert_query, data2)
            connection.commit()
            print(f"插入成功，影响的行数：{cursor.rowcount}")
    except Exception as e:
        print(f"发生错误：{e}")

    finally:
        if connection.open:
            connection.close()






def insert_detail(company_name, url,data):

    """
    更新指定 company_name 的公司信息记录

    :param company_name: 要更新的公司名称

    :param new_data: 包含要更新字段及其新值的字典
    """

    try:

        connection = pymysql.connect(

            host='127.0.0.1',  # 数据库主机地址

            user='root',  # 数据库用户名

            password='qyzh12260315',  # 数据库密码

            database='rpa',  # 数据库名称

            cursorclass=DictCursor

        )

        with connection.cursor() as cursor:
            # 构建动态插入语句
            insert_query = """
            INSERT INTO company_goods_detail_info_1 (
    contact_id,
    company_name, 
    contact_url, 
    goods_name, 
    goods_price, 
    size, 
    goods_numbers, 
    goods_guige, 
    made_way, 
    type, 
    pinpai, 
    shiyongfanwei, 
    xingneng, 
    zuoyong, 
    shifoukuajing, 
    style, 
    photo,
    origin
) VALUES (
    %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
            """
            # 假设 insert_values 是一个元组，包含要插入的值
            # insert_values = (company_name, url)

            cursor.execute(insert_query, data)
            connection.commit()
            print(f"插入成功，影响的行数：{cursor.rowcount}")
    except Exception as e:
        print(f"发生错误：{e}")

    finally:
        if connection.open:
            connection.close()

def insert_data(data3):

    """
    更新指定 company_name 的公司信息记录

    :param company_name: 要更新的公司名称

    :param new_data: 包含要更新字段及其新值的字典
    """

    try:

        connection = pymysql.connect(

            host='127.0.0.1',  # 数据库主机地址

            user='root',  # 数据库用户名

            password='qyzh12260315',  # 数据库密码

            database='rpa',  # 数据库名称

            cursorclass=DictCursor

        )

        with connection.cursor() as cursor:
            # 构建动态插入语句
            insert_query = """
            INSERT INTO data (
    url,
    name, 
    value,
    guige,
    guigexinxi,babyId
) VALUES (
    %s,%s, %s, %s, %s,%s
)
            """
            cursor.execute(insert_query, data3)
            connection.commit()
            print(f"插入成功，影响的行数：{cursor.rowcount}")
    except Exception as e:
        print(f"发生错误：{e}")

    finally:
        if connection.open:
            connection.close()
def yoxi(url,babyId):
    # URL = 'https://detail.1688.com/offer/693721337941.html?fromkv=cbuPcPlugin:selectionRecommend&amug_biz=oneself&amug_fl_src=awakeId_984'
    co = ChromiumOptions().auto_port()
    so = SessionOptions()
    page = WebPage(chromium_options=co, session_or_options=so)
    logger.info(
        "进入目标网址(有头模式)" + url)
    time.sleep(1)
    page.get(url)


    cc = page.ele('@class=feature-item-label',timeout=1)
    if cc:
        name = page.ele('@class=feature-item-label',timeout=1).text
        guige = ''
        pps = ''


    names = page.eles('@class=sku-prop-module-name',timeout=1)
    if names:

        if len(names)>1:
            print(123123)
            print(names[0].text)
            print(names[1].text)
            name = names[0].text
            guige = names[1].text


            guigexinxi = page.eles('@class=sku-item-name',timeout=1)

            pp = []
            for info in guigexinxi:
                # 获取图片的 src 属性
                src = info.text
                if src:  # 确保 src 不为空
                    print(src)
                    pp.append(src)  # 将图片 URL 添加到列表中

            # 打印所有图片 URL
            print("guige所有信息：", pp)
            # 将所有图片 URL 拼接成一个字符串，每个 URL 之间用逗号分隔
            pps = ','.join(pp)



        else:

            name = page.ele('@class=sku-prop-module-name',timeout=1).text
            guige = ""
            pps = ''
            print(name)

    # cc = page.ele('sku-item-wrapper')
    cc = page.ele('@class=prop-name',timeout=1)
    if cc:

        values = page.eles('@class=prop-name',timeout=1)
    else:

        values = page.eles('@class=sku-item-wrapper',timeout=1)
        if values:
            values = page.eles('@class=sku-item-wrapper', timeout=1)
        else:
            values = page.eles('@class=item-label',timeout=1)

    vv= []
    for info in values:
        # 获取图片的 src 属性
        src = info.text
        if src:  # 确保 src 不为空
            print(src)
            vv.append(src)  # 将图片 URL 添加到列表中


    # 打印所有图片 URL
    print("所有信息：", vv)
    # 将所有图片 URL 拼接成一个字符串，每个 URL 之间用逗号分隔
    vvs = ','.join(vv)
    print(vvs)

    data3 = (
        url,
        name,
        vvs,
        guige,
        pps,babyId

    )
    insert_data(data3)

def fetch_company_names_in_batches_url2(batch_size=10, start_offset=0):

    """

    分批查询 company_name

    :param batch_size: 每批查询的记录数，默认为10

    :param start_offset: 从第几行开始读取，默认为0

    :return: 生成器，每次返回一个批次的 company_name 列表

    """

    try:
        connection = pymysql.connect(
            host='127.0.0.1',  # 数据库主机地址
            user='root',  # 数据库用户名
            password='qyzh12260315',  # 数据库密码
            database='rpa',  # 数据库名称
            cursorclass=DictCursor
        )
        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM product_info")

            total_records = cursor.fetchone()['COUNT(*)']

            offset = start_offset  # 从指定的起始偏移量开始



            while offset < total_records:

                cursor.execute(f"SELECT babyId,contact_url,id,company_name FROM product_info LIMIT {batch_size} OFFSET {offset}")

                batch = [(row['babyId'],row['contact_url'], row['id'],row['company_name']) for row in cursor.fetchall()]


                yield batch

                offset += batch_size

    except Exception as e:

        print(f"发生错误：{e}")

    finally:

        if connection.open:

            connection.close()


def convert():

    import pandas as pd
    # 读取Excel文件
    df = pd.read_excel('./1688商品数据.xlsx', dtype={'宝贝ID': str, '宝贝链接': str})

    # 过滤掉宝贝ID或宝贝链接为空的行
    df = df.dropna(subset=['宝贝ID', '宝贝链接'])

    # 生成SQL插入语句列表
    sql_statements = []
    for index, row in df.iterrows():
        baby_id = row['宝贝ID']
        contact_url = row['宝贝链接'].replace("'", "''")  # 转义单引号
        sql = f"INSERT INTO your_table_name (babyId, contact_url) VALUES ('{baby_id}', '{contact_url}');"
        sql_statements.append(sql)

    # 输出结果到控制台（也可写入文件）
    for sql in sql_statements:
        print(sql)
if __name__ == "__main__":
    # yoxi('https://detail.1688.com/offer/692680573463.html?fromkv=cbuPcPlugin:others&amug_biz=oneself&amug_fl_src=awakeId_984')
    start_offset = 0
    end_offset = 3500
    for batch in fetch_company_names_in_batches_url2(batch_size=10,start_offset=start_offset):
        if start_offset >= end_offset:  # 检查是否超出范围
            print("已达到结束偏移量，停止处理。")
            break
        print(f"正在处理批次：{batch}")
        for babyId,contact_url,id,company_name in batch:
            print(f"正在更新公司：{babyId},{contact_url},{id},{company_name}")
            # 这里插入 RPA自定义的代码，用于获取公司信息并更新
            try:
                time.sleep(2)

                yoxi(contact_url,babyId)


            except:
                print(f"更新失败，错误信息")
        start_offset += len(batch)
# 235  1000

    # for batch in fetch_company_names_in_batches_url(batch_size=10,start_offset=1002):
    #     print(f"正在处理批次：{batch}")
    #     for contact_url,id,company_name in batch:
    #         print(f"正在更新公司：{contact_url},{id},{company_name}")
    #         # 这里插入 RPA自定义的代码，用于获取公司信息并更新
    #         try:
    #             time.sleep(3)
    #             data,name,value,品名 ,photo_urls_str,价格= rrpp(contact_url,id,company_name)
    #             insert_detail(company_name,contact_url,data)
    #
    #             # 初始化一个列表来存储图片 URL
    #             name_urls = []
    #
    #             # 遍历每个图片元素
    #             for info in name:
    #                 # 获取图片的 src 属性
    #                 src = info.text
    #                 if src:  # 确保 src 不为空
    #                     print(src)
    #                     name_urls.append(src)  # 将图片 URL 添加到列表中
    #
    #
    #
    #             name_urls2 = []
    #
    #             # 遍历每个图片元素
    #             for info in value:
    #                 # 获取图片的 src 属性
    #                 src = info.text
    #                 if src:  # 确保 src 不为空
    #                     print(src)
    #                     name_urls2.append(src)  # 将图片 URL 添加到列表中
    #
    #             # 使用 zip() 函数将两个列表的元素一一配对
    #             for src1, src2 in zip(name_urls, name_urls2):
    #                 print(f"URL1: {src1}, URL2: {src2}")
    #                 insert_true(company_name, src1, src2, id, 品名, photo_urls_str,价格)
    #             # insert_true(company_name,name,value,id,品名,photo_urls_str)
    #         except:
    #             print(f"更新失败，错误信息")