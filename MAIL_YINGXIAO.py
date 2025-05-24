import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header

# 邮件服务器配置
smtp_server = "smtp.em.dingtalk.com"  # 替换为你的SMTP服务器地址
smtp_port = 25  # SMTP端口
smtp_username = "zhangyc@smartebao.com"  # 替换为你的邮箱地址
smtp_password = "Demondemon33"  # 替换为你的邮箱密码

# 邮件内容
html_content = """
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>易豹国际贸易数字化平台</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .banner {
            width: 100%;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
            text-align: center;
        }
        .banner img {
            width: 100%;
            border-radius: 8px 8px 0 0;
        }
        .banner-title {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            white-space: nowrap;
            background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), rgba(0, 0, 0, 0.2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeIn 2s ease-in-out;
            z-index: 10;
            width: 100%;
            padding: 10px 0;
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header img {
            width: 80px;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 14px;
            color: #555;
        }
        .click-animation {
            display: inline-block;
            margin-left: 10px;
            color: #007bff;
            cursor: pointer;
            animation: blink 1s steps(5) infinite;
        }
        @keyframes blink {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        .price-animation {
            display: inline-block;
            color: #007bff;
            cursor: pointer;
            animation: blink 1s steps(5) infinite;
        }
        .content {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .content h2 {
            margin-bottom: 10px;
            color: #333;
        }
        .content p {
            margin: 5px 0;
            line-height: 1.6;
            color: #444;
        }
        .footer {
            text-align: center;
            color: #888;
            font-size: 12px;
        }
        .product-image {
            margin-top: 20px;
        }
        .product-image img {
            width: 100%;
            max-width: 600px;
        }
        .wechat-image {
            margin-top: 20px;
            text-align: center;
        }
        .wechat-image img {
            width: 100px;
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <img src="https://smartebao-opt-ifsbucket.oss-cn-shanghai.aliyuncs.com/1747291883-1747291883983_15611747291860.pichd.jpg" alt="Banner Image">
            <p>易豹国际贸易数字化平台</p>
        </div>
        <div class="header">
            <a href="https://www.smartebao.com/" target="_blank">
                <img src="https://smartebao-opt-ifsbucket.oss-cn-shanghai.aliyuncs.com/1746502342-1746502342819_13011746244255.pic.jpg" alt="Logo">
                <span class="click-animation">请点击</span>
            </a>
            <p>感谢相遇 - 易豹网络科技有限公司</p>
        </div>
        <div class="content">
            <div class="thank-you">
                <p>尊敬的客户：您好，</p>
            </div>
            <p>易豹公司可提供一站式报关（<span class="price-animation">40元/票</span>）、拖车、ISF/AMS（<span class="price-animation">35元/票</span>）、换单（<span class="price-animation">25美金/票</span>）等产品，烦请您了解，若有意向，请添加下方专属客服微信或者点击易豹图标，访问易豹官网获取相关支持。<br>
            易豹数字报关-<a href="https://mp.weixin.qq.com/s/FObQTTE7tS0FZQBhS2-44g" target="_blank">易豹“数字化报关引擎”  助力企业高效通关全球</a><br>
            易豹海外舱单<a href="https://mp.weixin.qq.com/s/Lu-6v7sln7BAYDMCnTDIXw" target="_blank">35元/票！钜惠来袭！易豹ISF/AMS海外舱单发送助您跨境无忧！</a></p>
            <div class="product-image">
                <img src="https://smartebao-opt-ifsbucket.oss-cn-shanghai.aliyuncs.com/1747799074-1747799074812_101747793156.pichd.jpg" alt="舱单平台产品图片">
            </div>
        </div>
        <div class="wechat-image">
            <img src="https://smartebao-opt-ifsbucket.oss-cn-shanghai.aliyuncs.com/1747623402-1747623402562_16181747623389.pic.jpg" alt="微信客服">
            <p>添加微信客服，了解更多详情</p>
        </div>
        <div class="footer">
            <p>如需获取有关易豹产品的帮助，请访问易豹官网获取相关支持。</p>
            <p>Copyright © 2017-2025 易豹网络科技有限公司 版权所有 浙ICP备19000709号</p>
        </div>
    </div>
</body>
</html>
"""

# 创建邮件对象
msg = MIMEMultipart()
msg['From'] = Header("易豹网络科技有限公司", 'utf-8')
msg['To'] = Header("客户", 'utf-8')
msg['Subject'] = Header("易豹国际贸易数字化平台", 'utf-8')

# 添加HTML内容
msg.attach(MIMEText(html_content, 'html', 'utf-8'))

# 发送邮件
# try:
#     # 连接SMTP服务器
#     server = smtplib.SMTP(smtp_server, smtp_port)
#     server.starttls()  # 启用TLS
#     server.login(smtp_username, smtp_password)  # 登录邮箱
#     server.sendmail(smtp_username
def send_email(smtp_server, port, sender_email, sender_password, recipient_emails, subject, body):
    # 创建邮件对象
    message = MIMEMultipart()
    message['From'] = Header("易豹网络科技有限公司", 'utf-8')  # 发件人显示名称
    message['To'] = Header("客户", 'utf-8')  # 收件人显示名称
    message['Subject'] = Header(subject, 'utf-8')  # 邮件主题

    # 邮件正文内容
    message.attach(MIMEText(body, 'html', 'utf-8'))

    try:
        # 连接到SMTP服务器
        with smtplib.SMTP(smtp_server, port) as server:
            # server.starttls()  # 启用TLS加密
            server.login(sender_email, sender_password)  # 登录邮箱
            server.sendmail(sender_email, recipient_emails, message.as_string())  # 发送邮件
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败：{e}")
if __name__ == '__main__':
    # 配置邮件参数
    smtp_server = 'smtp.em.dingtalk.com'  # SMTP服务器地址
    port = 25  # SMTP端口（通常587用于TLS）
    sender_email = 'zhangyc@smartebao.com'  # 发件人邮箱
    sender_password = 'Demondemon33'  # 发件人邮箱密码
    recipient_emails = ['zhangyc@smartebao.com', 'qiyz@smartebao.com']  # 收件人邮箱列表
    subject = '易豹舱单平台生态产品'  # 邮件主题
    body = '这是一封测试邮件'


    # 调用发送邮件函数
    send_email(smtp_server, port, sender_email, sender_password, recipient_emails, subject,body)
