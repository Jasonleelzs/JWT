import _thread
import socket
import urllib.parse

from routes import route_dict
from routes import route_static
from utils import log
from routes import error


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.raw_data = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        # log('cookie111', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        """
        Cookie: user=gua
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        # 清空 cookies
        self.cookies = {}
        self.add_cookies()

    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


def parsed_path(path):
    """
    输入: /gua?message=hello&author=gua
    返回
    (gua, {
        'message': 'hello',
        'author': 'gua',
    })
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    path, query = parsed_path(request.path)
    request.path = path
    request.query = query
    # log('path 和 query', path, query)
    r = {
        '/static': route_static,
    }
    r.update(route_dict())
    response = r.get(path, error)
    return response(request)


def process_request(connection):
    r = connection.recv(1024)
    r = r.decode()
    # log('request {}'.format(r))

    # 把 body 放入 request 中
    request = Request()
    request.raw_data = r
    # 只能 split 一次，因为 body 中可能有换行
    xx = r.split('\r\n\r\n', 1)
    if len(xx) > 1:
        header, request.body = xx
    else:
        header = str(xx)
    h = header.split('\r\n')
    parts = h[0].split()
    request.path = parts[1]
    # 设置 request 的 method
    request.method = parts[0]
    request.add_headers(h[1:])

    # 用 response_for_path 函数来得到 path 对应的响应内容
    response = response_for_path(request)
    # 把响应发送给客户端
    connection.sendall(response)
    # 处理完请求, 关闭连接
    connection.close()


def run(host='', port=3000):
    """
    启动服务器
    """
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        while True:
            # 监听 接受 读取请求数据 解码成字符串
            s.listen(5)
            connection, address = s.accept()
            # log('ip {}'.format(address))
            _thread.start_new_thread(process_request, (connection,))


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='127.0.0.1',
        port=3000,
    )
    # 如果不了解 **kwargs 的用法, 上过基础课的请复习函数, 新同学自行搜索
    run(**config)
