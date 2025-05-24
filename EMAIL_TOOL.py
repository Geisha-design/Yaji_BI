import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 假设这些是你的物流信息
class LitManifestTransEmailSo:
    def __init__(self, mbl, hbl, etd, eta, carrier_code, mbl_link, hbl_link, box_number):
        self.mbl = mbl
        self.hbl = hbl
        self.etd = etd
        self.eta = eta
        self.carrier_code = carrier_code
        self.mbl_link = mbl_link
        self.hbl_link = hbl_link
        self.box_number = box_number

# 示例数据
litManifestTransEmailSo = LitManifestTransEmailSo(
    mbl="MBL123456",
    hbl="HBL789012",
    etd="2025-05-20",
    eta="2025-06-10",
    carrier_code="CARRIER123",
    mbl_link="https://example.com/mbl123456",
    hbl_link="https://example.com/hbl789012",
    box_number="BOX123456"
)

# 时间格式化工具
def toABCFormat(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")

# 构建HTML内容
html_content = f"""
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SWITCH B/L确认邮件</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .banner {{
            width: 100%;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
            text-align: center;
        }}
        .banner img {{
            width: 100%;
            border-radius: 8px 8px 0 0;
        }}
        .banner-title {{
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
        }}
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .header img {{
            width: 80px;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 14px;
            color: #555;
        }}
        .content {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}
        .content h2 {{
            margin-bottom: 10px;
            color: #333;
        }}
        .content p {{
            margin: 5px 0;
            line-height: 1.6;
            color: #444;
        }}
        .footer {{
            text-align: center;
            color: #888;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <img src="https://smartebao-opt-ifsbucket.oss-cn-shanghai.aliyuncs.com/1746502311-1746502311795_13061746272766.pic.jpg" alt="Banner Image">
            <p>SWITCH B/L Pre-alert</p>
        </div>
        <div class="header">
            <a href="https://www.smartebao.com/" target="_blank"><img src="https://smartebao-opt-ifsbucket.oss-cn-shanghai.aliyuncs.com/1746502342-1746502342819_13011746244255.pic.jpg" alt="Logo"></a>
            <p>感谢您的下单 - 易豹网络科技有限公司</p>
        </div>
        <div class="content">
            <div class="thank-you">
                <p>Dear Customer,<br>
                Thank you for your business. We appreciate your trust and support.</p>
            </div>
            <p>mbl: {litManifestTransEmailSo.mbl}</p>
            <p>hbl: {litManifestTransEmailSo.hbl}</p>
            <p>etd: {litManifestTransEmailSo.etd}</p>
            <p>eta: {litManifestTransEmailSo.eta}</p>
            <p>carrier code: {litManifestTransEmailSo.carrier_code}</p>
            <p>mbl提单链接: {litManifestTransEmailSo.mbl_link}</p>
            <p>hbl提单链接: {litManifestTransEmailSo.hbl_link}</p>
            <p>柜号: {litManifestTransEmailSo.box_number}</p>
            <p>append time: {toABCFormat(datetime.now().strftime("%Y-%m-%d"))}</p>
        </div>
        <div class="footer">
            <p>如需获取有关易豹产品的帮助，请访问易豹官网获取相关支持。</p>
            <p>Copyright © 2017-2025 易豹网络科技有限公司 版权所有 浙ICP备19000709号</p>
        </div>
    </div>
</body>
</html>
"""

# 邮件发送函数
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
            server.starttls()  # 启用TLS加密
            server.login(sender_email, sender_password)  # 登录邮箱
            server.sendmail(sender_email, recipient_emails, message.as_string())  # 发送邮件
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败：{e}")


if __name__ == '__main__':
    # 配置邮件参数
    smtp_server = 'smtp.em.dingtalk.com'  # SMTP服务器地址
    port = 587  # SMTP端口（通常587用于TLS）
    sender_email = 'zhangyc@smartebao.com'  # 发件人邮箱
    sender_password = 'Demondemon33'  # 发件人邮箱密码
    recipient_emails = ['zhangyc@smartebao.com', 'qiyz@smartebao.com']  # 收件人邮箱列表
    subject = '易豹舱单平台生态产品'  # 邮件主题
    body = '这是一封测试邮件'


    # 调用发送邮件函数
    send_email(smtp_server, port, sender_email, sender_password, recipient_emails, subject,body)
