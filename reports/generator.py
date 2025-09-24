"""
报表生成器
"""
from datetime import datetime, date
from database.connection import get_mysql_connection
from config.database_config import MYSQL_CONFIG
from utils.helpers import thread_safe_print


def query_alo_and_booking_mapping():
    """
    查询yaji_email_records中当天记录的alo字段，
    并在yaji_main中查找对应的cds_booking_no
    """
    connection = get_mysql_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # 使用数据库
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 获取今天的日期
            today = date.today()

            # 查询yaji_email_records中当天的记录，获取alo字段
            select_email_sql = '''
            SELECT DISTINCT alo 
            FROM yaji_email_records 
            WHERE DATE(received_time) = %s 
            AND alo IS NOT NULL 
            AND alo != '无al0信息'
            AND status_str ='未处理'

            '''

            cursor.execute(select_email_sql, (today,))
            email_records = cursor.fetchall()

            if not email_records:
                thread_safe_print("今天没有找到任何邮件记录")
                return []

            thread_safe_print(f"找到 {len(email_records)} 个不同的ALO编号")

            # 提取所有alo值
            alo_list = [record['alo'] for record in email_records]

            # 在yaji_main中查找对应的cds_booking_no
            # 使用IN查询提高效率
            placeholders = ','.join(['%s'] * len(alo_list))
            select_main_sql = f'''
            SELECT er.id, er.booking_key, er.cds_booking_no, er.ffc_no, er.submit_status_str, er.create_date,m.subject
            FROM yaji_main er
            INNER JOIN yaji_email_records m ON m.alo = er.booking_key
            WHERE booking_key IN ({placeholders})
            '''

            cursor.execute(select_main_sql, alo_list)
            main_records = cursor.fetchall()

            thread_safe_print(f"找到 {len(main_records)} 条匹配的主要记录:")
            return main_records

    except Exception as e:
        thread_safe_print(f"查询ALO和Booking映射关系失败: {e}")
        return []
    finally:
        connection.close()


def generate_html_report(data):
    """
    生成HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['booking_key']}</strong></td>
            <td><span class="icon">📄</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">🔢</span> {record['ffc_no'] or 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
            <td><span class="icon">📅</span> {record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集即时未处理邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            min-height: 100vh;
        }}

        @keyframes gradientBG {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: rgba(248, 249, 250, 0.85);
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 200px;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
            font-weight: 500;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 18px 15px;
            font-weight: 500;
            font-size: 1.05em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e9f7fe;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            font-weight: 500;
        }}

        .icon {{
            margin-right: 8px;
            font-size: 1.1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: rgba(248, 249, 250, 0.6);
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}

        .pulse {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ff6b6b;
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            animation: pulse 2s infinite;
            margin-right: 8px;
        }}

        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(255, 107, 107, 0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> 亚集统计数据表</h1>
            <p>基于当天邮件记录与主数据的关联分析</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-database"></i> 匹配记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number"><span class="pulse"></span></div>
                <div class="stat-label"><i class="fas fa-sync-alt"></i> 实时数据</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-fingerprint"></i> ID</th>
                        <th><i class="fas fa-key"></i> Booking Key (ALO)</th>
                        <th><i class="fas fa-file-contract"></i> CDS Booking No</th>
                        <th><i class="fas fa-hashtag"></i> FFC No</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                        <th><i class="far fa-calendar-plus"></i> 创建日期</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def save_html_report(html_content, filename=None):
    """
    保存HTML报表到文件
    """
    if filename is None:
        filename = f"alo_booking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        thread_safe_print(f"HTML报表已保存至: {os.path.abspath(filename)}")
        return filename
    except Exception as e:
        thread_safe_print(f"保存HTML报表失败: {e}")
        return None


def generate_html_report2(data):
    """
    生成现代化 HTML 报表（带搜索、主题切换、详情弹窗）
    """
    from datetime import datetime, date
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr onclick="showDetails('{record['id']}','{record['booking_key']}','{record['cds_booking_no'] or 'N/A'}','{record['ffc_no'] or 'N/A'}','{record['submit_status_str'] or '未知'}','{record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}','{record['subject'] or 'N/A'}')">
            <td>{record['id']}</td>
            <td>{record['booking_key']}</td>
            <td>{record['cds_booking_no'] or 'N/A'}</td>
            <td>{record['ffc_no'] or 'N/A'}</td>
            <td><span class="{status_class}">{status_icon} {record['submit_status_str'] or '未知'}</span></td>
            <td>{record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
            <td>{record['subject'] or 'N/A'}</td>
        </tr>
        '''

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>亚集即时未处理邮件统计</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<style>
:root {{
  --bg-light: #f6f8fb;
  --bg-dark: #121826;
  --card-light: rgba(255,255,255,0.92);
  --card-dark: rgba(24,28,36,0.92);
  --text-light: #222;
  --text-dark: #eee;
}}
body {{
  margin:0; font-family:"Segoe UI",sans-serif;
  background: var(--bg-light);
  color: var(--text-light);
  transition: background .3s,color .3s;
}}
[data-theme="dark"] body {{
  background: var(--bg-dark);
  color: var(--text-dark);
}}
.container {{
  max-width:1200px; margin:20px auto;
  background: var(--card-light);
  border-radius:12px; padding:20px;
  box-shadow:0 8px 20px rgba(0,0,0,0.1);
  transition: background .3s;
}}
[data-theme="dark"] .container {{
  background: var(--card-dark);
}}
.header {{
  display:flex;justify-content:space-between;align-items:center;
}}
.theme-toggle {{
  cursor:pointer; border:none; background:#667eea;color:white;
  padding:8px 14px;border-radius:8px;font-size:14px;
}}
.stats {{
  display:flex;justify-content:space-around;flex-wrap:wrap;margin:20px 0;
}}
.stat-item {{
  padding:10px;text-align:center;min-width:160px;
}}
.stat-number {{font-size:1.8em;font-weight:700;color:#667eea;}}
table {{
  width:100%;border-collapse:collapse;margin-top:15px;
}}
th,td {{
  padding:12px;text-align:left;border-bottom:1px solid #ddd;
}}
tr:hover {{
  background:#f1f5ff;cursor:pointer;
}}
.status-active {{color:#155724;background:#d4edda;padding:4px 10px;border-radius:12px;}}
.status-pending {{color:#856404;background:#fff3cd;padding:4px 10px;border-radius:12px;}}
.status-other {{color:#0c5460;background:#d1ecf1;padding:4px 10px;border-radius:12px;}}
/* 弹窗 */
.modal {{
  display:none;position:fixed;top:0;left:0;width:100%;height:100%;
  background:rgba(0,0,0,0.6);align-items:center;justify-content:center;
}}
.modal-content {{
  background:white;padding:20px;border-radius:10px;max-width:500px;width:90%;
}}
[data-theme="dark"] .modal-content {{
  background:#1f2533;color:#fff;
}}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2><i class="fas fa-chart-line"></i> 亚集统计报表</h2>
      <button class="theme-toggle" onclick="toggleTheme()">切换主题</button>
    </div>

    <div class="stats">
      <div class="stat-item">
        <div class="stat-number">{len(data)}</div>
        <div>匹配记录数</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{current_time}</div>
        <div>生成时间</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
        <div>报告日期</div>
      </div>
    </div>

    <input type="text" id="search" placeholder="🔍 搜索 Booking Key..." style="width:100%;padding:10px;margin:10px 0;border-radius:8px;border:1px solid #ccc;">

    <table id="report-table">
      <thead>
        <tr>
          <th>ID</th><th>Booking Key</th><th>CDS No</th><th>FFC No</th><th>状态</th><th>创建日期</th><th>主题</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>

  <!-- 详情弹窗 -->
  <div class="modal" id="detailModal">
    <div class="modal-content">
      <h3>记录详情</h3>
      <p id="detailBody"></p>
      <button onclick="closeModal()">关闭</button>
    </div>
  </div>

<script>
function toggleTheme(){{
  const html=document.documentElement;
  const theme=html.getAttribute("data-theme")==="dark"?"light":"dark";
  html.setAttribute("data-theme",theme);
}}

document.getElementById("search").addEventListener("keyup",function(){{
  let filter=this.value.toLowerCase();
  let rows=document.querySelectorAll("#report-table tbody tr");
  rows.forEach(r=>{{
    r.style.display=r.innerText.toLowerCase().includes(filter)?"":"none";
  }});
}});

function showDetails(id, bookingKey, cdsNo, ffcNo, status, createDate, subject) {{
  const detailBody = document.getElementById('detailBody');
  detailBody.innerHTML = `
    <strong>ID:</strong> ${{id}}<br>
    <strong>Booking Key:</strong> ${{bookingKey}}<br>
    <strong>CDS No:</strong> ${{cdsNo}}<br>
    <strong>FFC No:</strong> ${{ffcNo}}<br>
    <strong>状态:</strong> ${{status}}<br>
    <strong>创建日期:</strong> ${{createDate}}<br>
    <strong>主题:</strong> ${{subject}}<br>
  `;
  document.getElementById("detailModal").style.display="flex";
}}

function closeModal(){{
  document.getElementById("detailModal").style.display="none";
}}
</script>
</body>
</html>
"""
    return html_content


def generate_all_alo_html_report(data):
    """
    生成包含当天所有ALO号的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        # 转义邮件内容中的特殊字符，避免破坏HTML结构
        escaped_content = (record['content_text'] or '').replace('"', '&quot;').replace("'", "&#39;") if record[
            'content_text'] else ''

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
            <td><span class="icon">📄</span> {record['subject'] or 'N/A'}</td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天所有ALO邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.2em;
            font-weight: bold;
            color: #11998e;
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background-color: #11998e;
            color: white;
            text-align: left;
            padding: 16px 15px;
        }}

        td {{
            padding: 14px 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        tr:hover {{
            background-color: #e8f5e9;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .icon {{
            margin-right: 6px;
            font-size: 1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
            margin-top: 20px;
            background-color: #f8f9fa;
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-list"></i> 亚集当天所有ALO邮件统计报表</h1>
            <p>基于邮件系统数据的完整分析</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-envelope"></i> 邮件总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-fingerprint"></i> ID</th>
                        <th><i class="fas fa-key"></i> ALO编号</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                        <th><i class="fas fa-envelope"></i> 邮件主题</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def generate_alo_with_fbe_html_report(data):
    """
    生成包含当天有FBE单子的ALO记录的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天有FBE单子的ALO邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: #333;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ffa8a8 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: #fff9f9;
            padding: 25px;
            border-bottom: 1px solid #fddddd;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.2em;
            font-weight: bold;
            color: #ff6b6b;
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background-color: #ff6b6b;
            color: white;
            text-align: left;
            padding: 16px 15px;
        }}

        td {{
            padding: 14px 15px;
            border-bottom: 1px solid #fddddd;
        }}

        tr:nth-child(even) {{
            background-color: #fff9f9;
        }}

        tr:hover {{
            background-color: #ffecec;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .icon {{
            margin-right: 6px;
            font-size: 1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #fddddd;
            margin-top: 20px;
            background-color: #fff9f9;
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-check-circle"></i> 亚集当天有FBE单子的ALO邮件统计报表</h1>
            <p>已关联到FBE主数据的ALO编号分析</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-link"></i> 关联记录数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-envelope"></i> 邮件ID</th>
                        <th><i class="fas fa-key"></i> ALO编号</th>
                        <th><i class="fas fa-file-invoice"></i> FBE编号</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def generate_no_alo_html_report(data):
    """
    生成包含当天无ALO信息邮件记录的HTML报表
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成表格行
    table_rows = ""
    for record in data:
        # 根据状态设置样式
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        # 转义邮件内容中的特殊字符，避免破坏HTML结构
        escaped_content = (record['content_text'] or '').replace('"', '&quot;').replace("'", "&#39;") if record[
            'content_text'] else ''

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><span class="icon">📧</span> {record['message_id'] or 'N/A'}</td>
            <td><span class="icon">📄</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
        </tr>
        '''

    # HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集当天无ALO信息邮件统计</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
            color: #333;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #3494e6 0%, #ec6ead 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: #f5f9ff;
            padding: 25px;
            border-bottom: 1px solid #d1e7ff;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.2em;
            font-weight: bold;
            color: #3494e6;
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 1em;
            margin-top: 8px;
        }}

        .content {{
            padding: 25px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background-color: #3494e6;
            color: white;
            text-align: left;
            padding: 16px 15px;
        }}

        td {{
            padding: 14px 15px;
            border-bottom: 1px solid #d1e7ff;
        }}

        tr:nth-child(even) {{
            background-color: #f5f9ff;
        }}

        tr:hover {{
            background-color: #e1f0ff;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .icon {{
            margin-right: 6px;
            font-size: 1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #d1e7ff;
            margin-top: 20px;
            background-color: #f5f9ff;
        }}

        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-question-circle"></i> 亚集当天无ALO信息邮件统计报表</h1>
            <p>无法提取ALO编号的邮件记录分析</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(data)}</div>
                <div class="stat-label"><i class="fas fa-envelope"></i> 邮件总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{current_time}</div>
                <div class="stat-label"><i class="far fa-clock"></i> 生成时间</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{date.today().strftime("%Y-%m-%d")}</div>
                <div class="stat-label"><i class="far fa-calendar-alt"></i> 报告日期</div>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-fingerprint"></i> ID</th>
                        <th><i class="fas fa-id-card"></i> 消息ID</th>
                        <th><i class="fas fa-envelope"></i> 主题</th>
                        <th><i class="fas fa-download"></i> 接收时间</th>
                        <th><i class="fas fa-tasks"></i> 状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''

    return html_content


def generate_combined_html_report(data_dict):
    """
    生成包含所有报表的综合HTML报表

    Args:
        data_dict (dict): 包含各类报表数据的字典

    Returns:
        str: HTML内容
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成各部分的内容
    alo_booking_content = _generate_alo_booking_section(data_dict.get('alo_booking', []))
    all_alo_content = _generate_all_alo_section(data_dict.get('all_alo', []))
    alo_with_fbe_content = _generate_alo_with_fbe_section(data_dict.get('alo_with_fbe', []))
    no_alo_content = _generate_no_alo_section(data_dict.get('no_alo', []))
    alo_not_in_main_content = _generate_alo_not_in_main_section(data_dict.get('alo_not_in_main', []))
    alo_without_fbe_content = _generate_alo_without_fbe_section(data_dict.get('alo_without_fbe', []))

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚集RPA数字化综合报表</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}

        .report-time {{
            font-size: 1.2em;
            opacity: 0.95;
        }}

        .summary-stats {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            flex: 1;
            min-width: 200px;
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card h3 {{
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #555;
        }}

        .stat-number {{
            font-size: 2.2em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .card-alo-booking {{ border-top: 5px solid #4e73df; }}
        .card-all-alo {{ border-top: 5px solid #1cc88a; }}
        .card-with-fbe {{ border-top: 5px solid #36b9cc; }}
        .card-without-fbe {{ border-top: 5px solid #6f42c1; }}
        .card-no-alo {{ border-top: 5px solid #f6c23e; }}
        .card-not-in-main {{ border-top: 5px solid #e74a3b; }}

        .card-alo-booking .stat-number {{ color: #4e73df; }}
        .card-all-alo .stat-number {{ color: #1cc88a; }}
        .card-with-fbe .stat-number {{ color: #36b9cc; }}
        .card-without-fbe .stat-number {{ color: #6f42c1; }}
        .card-no-alo .stat-number {{ color: #f6c23e; }}
        .card-not-in-main .stat-number {{ color: #e74a3b; }}

        .section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }}

        .section-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            font-size: 1.4em;
            font-weight: 500;
        }}

        .section-content {{
            padding: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            padding: 15px;
            font-weight: 500;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fc;
        }}

        tr:hover {{
            background-color: #e3f2fd;
        }}

        .status-active {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
        }}

        .status-pending {{
            background-color: #fff3cd;
            color: #856404;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
        }}

        .status-other {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
        }}

        .icon {{
            margin-right: 6px;
            font-size: 1em;
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 0.95em;
            background: white;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }}

        @media (max-width: 768px) {{
            .summary-stats {{
                flex-direction: column;
            }}

            th, td {{
                padding: 10px 12px;
            }}

            .stat-card {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-bar"></i> 亚集RPA数字化综合报表</h1>
            <div class="report-time">生成时间: {current_time} | 报告日期: {date.today().strftime("%Y-%m-%d")}</div>
        </div>

        <div class="summary-stats">
            <div class="stat-card card-alo-booking">
                <h3><i class="fas fa-link"></i> ALO-Booking映射</h3>
                <div class="stat-number">{len(data_dict.get('alo_booking', []))}</div>
                <div>关联记录数</div>
            </div>

            <div class="stat-card card-all-alo">
                <h3><i class="fas fa-list"></i> 所有ALO记录</h3>
                <div class="stat-number">{len(data_dict.get('all_alo', []))}</div>
                <div>ALO邮件数</div>
            </div>

            <div class="stat-card card-with-fbe">
                <h3><i class="fas fa-check-circle"></i> 有FBE单子</h3>
                <div class="stat-number">{len(data_dict.get('alo_with_fbe', []))}</div>
                <div>已关联记录</div>
            </div>

            <div class="stat-card card-without-fbe">
                <h3><i class="fas fa-times-circle"></i> 无FBE单子</h3>
                <div class="stat-number">{len(data_dict.get('alo_without_fbe', []))}</div>
                <div>未关联记录</div>
            </div>

            <div class="stat-card card-no-alo">
                <h3><i class="fas fa-question-circle"></i> 无ALO信息</h3>
                <div class="stat-number">{len(data_dict.get('no_alo', []))}</div>
                <div>无法提取记录</div>
            </div>

            <div class="stat-card card-not-in-main">
                <h3><i class="fas fa-exclamation-triangle"></i> 主表不存在</h3>
                <div class="stat-number">{len(data_dict.get('alo_not_in_main', []))}</div>
                <div>未匹配记录</div>
            </div>
        </div>

        <!-- ALO与Booking映射部分 -->
        <div class="section">
            <div class="section-header">
                <i class="fas fa-link"></i> ALO与Booking映射关系
            </div>
            <div class="section-content">
                {alo_booking_content}
            </div>
        </div>

        <!-- 所有ALO记录部分 -->
        <div class="section">
            <div class="section-header">
                <i class="fas fa-list"></i> 所有ALO记录
            </div>
            <div class="section-content">
                {all_alo_content}
            </div>
        </div>

        <!-- 有FBE单子的ALO记录部分 -->
        <div class="section">
            <div class="section-header">
                <i class="fas fa-check-circle"></i> 有FBE单子的ALO记录
            </div>
            <div class="section-content">
                {alo_with_fbe_content}
            </div>
        </div>

        <!-- 没有FBE单子的ALO记录部分 -->
        <div class="section">
            <div class="section-header">
                <i class="fas fa-times-circle"></i> 没有FBE单子的ALO记录
            </div>
            <div class="section-content">
                {alo_without_fbe_content}
            </div>
        </div>

        <!-- 无ALO信息的邮件记录部分 -->
        <div class="section">
            <div class="section-header">
                <i class="fas fa-question-circle"></i> 无ALO信息的邮件记录
            </div>
            <div class="section-content">
                {no_alo_content}
            </div>
        </div>

        <!-- 在主表中都不存在的ALO记录部分 -->
        <div class="section">
            <div class="section-header">
                <i class="fas fa-exclamation-triangle"></i> 主表中都不存在的ALO记录
            </div>
            <div class="section-content">
                {alo_not_in_main_content}
            </div>
        </div>

        <div class="footer">
            <p><i class="fas fa-robot"></i> 报表由易豹系统自动生成 | 数据来源：易豹网络科技RPA数字化执行平台</p>
        </div>
    </div>
</body>
</html>
'''
    return html_content


def _generate_alo_booking_section(data):
    """生成ALO与Booking映射部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['booking_key']}</strong></td>
            <td><span class="icon">📄</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">🔢</span> {record['ffc_no'] or 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
            <td><span class="icon">📅</span> {record['create_date'].strftime('%Y-%m-%d %H:%M:%S') if record['create_date'] else 'N/A'}</td>
            <td><span class="icon">✉️</span> {record['subject'] or 'N/A'}</td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-key"></i> Booking Key</th>
                <th><i class="fas fa-file-contract"></i> CDS Booking No</th>
                <th><i class="fas fa-hashtag"></i> FFC No</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
                <th><i class="far fa-calendar-plus"></i> 创建日期</th>
                <th><i class="fas fa-envelope"></i> 主题</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_all_alo_section(data):
    """生成所有ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
            <td><span class="icon">📄</span> {record['subject'] or 'N/A'}</td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
                <th><i class="fas fa-envelope"></i> 邮件主题</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_alo_with_fbe_section(data):
    """生成有FBE单子的ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-envelope"></i> 邮件ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-file-invoice"></i> FBE编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_alo_without_fbe_section(data):
    """生成没有FBE单子的ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['submit_status_str'] and '完成' in record['submit_status_str']:
            status_class = "status-active"
            status_icon = "✅"
        elif record['submit_status_str'] and (
                '处理' in record['submit_status_str'] or '进行' in record['submit_status_str']):
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">📧</span> {record['email_id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📦</span> {record['cds_booking_no'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['submit_status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-envelope"></i> 邮件ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-file-invoice"></i> FBE编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_no_alo_section(data):
    """生成无ALO信息的邮件记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><span class="icon">📧</span> {record['message_id'] or 'N/A'}</td>
            <td><span class="icon">📄</span> {record['subject'] or 'N/A'}</td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-id-card"></i> 消息ID</th>
                <th><i class="fas fa-envelope"></i> 主题</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''


def _generate_alo_not_in_main_section(data):
    """生成在主表中都不存在的ALO记录部分"""
    if not data:
        return '<p style="text-align: center; padding: 20px;">暂无数据</p>'

    table_rows = ""
    for record in data:
        status_class = "status-other"
        status_icon = "🔹"
        if record['status_str'] == '已处理':
            status_class = "status-active"
            status_icon = "✅"
        elif record['status_str'] == '未处理':
            status_class = "status-pending"
            status_icon = "⏳"

        table_rows += f'''
        <tr>
            <td><span class="icon">🆔</span> {record['id']}</td>
            <td><strong><span class="icon">🔑</span> {record['alo']}</strong></td>
            <td><span class="icon">📥</span> {record['received_time'].strftime('%Y-%m-%d %H:%M:%S') if record['received_time'] else 'N/A'}</td>
            <td><span class="icon">{status_icon}</span> <span class="{status_class}">{record['status_str'] or '未知'}</span></td>
            <td><span class="icon">📄</span> {record['subject'] or 'N/A'}</td>
        </tr>
        '''

    return f'''
    <table>
        <thead>
            <tr>
                <th><i class="fas fa-fingerprint"></i> ID</th>
                <th><i class="fas fa-key"></i> ALO编号</th>
                <th><i class="fas fa-download"></i> 接收时间</th>
                <th><i class="fas fa-tasks"></i> 状态</th>
                <th><i class="fas fa-envelope"></i> 邮件主题</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''