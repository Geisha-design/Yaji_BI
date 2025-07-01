


class NetworkError(Exception):
    """网络错误基类"""
    pass
class ConnectionError(NetworkError):
    """连接错误"""
    def __init__(self, message="RPA连接失败"):
        super().__init__(message)

class TimeoutError(NetworkError):
    """超时错误"""
    def __init__(self, message="RPA连接超时"):
        super().__init__(message)

