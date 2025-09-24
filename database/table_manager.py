"""
数据库表管理
"""
from config.database_config import MYSQL_CONFIG
from database.connection import get_mysql_connection
from utils.helpers import thread_safe_print


def create_main_table():
    """
    在MySQL中创建主数据表
    """
    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 创建主数据表
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS yaji_main (
                   id INT PRIMARY KEY,
                    rel_company_id INT,
                    booking_key VARCHAR(255),
                    cds_booking_no VARCHAR(255),
                    ffc_no VARCHAR(255) NULL,
                    submit_channel VARCHAR(50),
                    phone VARCHAR(100),
                    mail_addr VARCHAR(255),
                    status VARCHAR(100),
                    remark VARCHAR(100),
                    creater VARCHAR(100),
                    create_date DATETIME,
                    submit_time DATETIME NULL,
                    submit_status_str varchar(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            cursor.execute(create_table_sql)

        connection.commit()
        thread_safe_print("MySQL核验主表创建成功")

    except Exception as e:
        thread_safe_print(f"MySQL表创建失败: {e}")
    finally:
        connection.close()


def create_main_table_fba():
    """
    在MySQL中创建FBA主数据表
    """
    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 创建FBA主数据表
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS yaji_main_fba (
                   id INT PRIMARY KEY,
                    rel_company_id INT,
                    booking_key VARCHAR(255),
                    cds_booking_no VARCHAR(255),
                    ffc_no VARCHAR(255) NULL,
                    submit_channel VARCHAR(50),
                    phone VARCHAR(100),
                    mail_addr VARCHAR(255),
                    status VARCHAR(100),
                    remark VARCHAR(100),
                    creater VARCHAR(100),
                    create_date DATETIME,
                    submit_time DATETIME NULL,
                    submit_status_str varchar(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            cursor.execute(create_table_sql)

        connection.commit()
        thread_safe_print("MySQL核验主表创建成功")

    except Exception as e:
        thread_safe_print(f"MySQL表创建失败: {e}")
    finally:
        connection.close()


def create_email_table():
    """
    在MySQL中创建邮件表
    """
    connection = get_mysql_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")

            # 创建邮件表
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS yaji_email_records (
                id INT PRIMARY KEY,
                message_id TEXT,
                from_addresses TEXT,
                content LONGTEXT,
                content_text LONGTEXT,
                received_time DATETIME,
                status VARCHAR(50),
                mail_addr VARCHAR(255),
                rel_fba_apply_id INT,
                subject TEXT,
                status_str VARCHAR(100),
                alo VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            cursor.execute(create_table_sql)

        connection.commit()
        thread_safe_print("MySQL邮件表创建成功")

    except Exception as e:
        thread_safe_print(f"MySQL表创建失败: {e}")
    finally:
        connection.close()