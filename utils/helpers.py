"""
通用工具函数
"""
import random
import time
import html
from threading import Lock

# 用于线程安全的打印
print_lock = Lock()


def thread_safe_print(*args, **kwargs):
    """
    线程安全的打印函数
    """
    with print_lock:
        print(*args, **kwargs)


def random_sleep(min_seconds=1, max_seconds=3):
    """
    随机休眠函数
    """
    sleep_time = random.randint(min_seconds, max_seconds)
    thread_safe_print(f"Randomly selected sleep time: {sleep_time} seconds")
    time.sleep(sleep_time)


def escape_html_content(data):
    """
    安全转义HTML内容，防止特殊字符导致的错误
    """
    if isinstance(data, str):
        return html.escape(data)
    elif isinstance(data, (int, float)):
        return str(data)
    elif data is None:
        return ""
    else:
        return html.escape(str(data))