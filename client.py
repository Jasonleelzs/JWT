import socket
import ssl


def parsed_url(url):
    """
    解析 url 返回 (protocol host port path)
    有的时候有的函数, 它本身就美不起来, 你要做的就是老老实实写
    """
    # 检查协议
    # '://' 定位 然后取第一个 / 的位置来切片
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])
    else:
        # 检查端口
        port_dict = {
            'http': 80,
            'https': 443,
        }
        # 默认端口
        port = port_dict[protocol]

    return protocol, host, port, path


def response_by_socket(s):
    """
    参数是一个 socket 实例
    返回这个 socket 读取的所有数据
    """
    response = b''
    buffer_size = 1024
    # Connection: close 情况下循环收数据
    while True:
        r = s.recv(buffer_size)
        print("receive {} {}".format(len(r), r))
        if len(r) != 0:
            response += r
        else:
            return response
    # Connection: keep-alive （默认） 情况下循环收数据
    # while True:
    #     r = s.recv(buffer_size)
    #     print("receive {} {}".format(len(r), r))
    #     response += r
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
        # if len(r) < buffer_size:
        #     return response


def socket_by_protocol(protocol):
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        s = ssl.wrap_socket(socket.socket())
    return s


def parsed_response(r):
    """
    解析出 状态码 header body
    """
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    # HTTP/1.1 301 Moved Permanently
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        # Content-Type: text/html
        k, v = line.split(': ')
        headers[k] = v

    return status_code, headers, body


# 复杂的逻辑全部封装成函数
def get(url):
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)

    s = socket_by_protocol(protocol)
    s.connect((host, port))

    # Connection 有两个选项 close 和 keep-alive
    # 那么有三种处理方式
    # 1. 一次 recv 所有数据
    # 2. 无线循环加默认 Connection (keep-alive) 
    # request='GET {} HTTP/1.1\r\nhost: {}\r\n\r\n'.format(
    # 3. 无限循环加 Connection: close  （推荐）
    request = 'GET {} HTTP/1.1\r\nhost: {}\r\nCookie: user=shlsshjkahkdahhs\r\nConnection: close\r\n\r\n'.format(
        path, host
    )
    # encode 的 'utf-8' 参数可以省略
    s.send(request.encode())

    response = response_by_socket(s)
    r = response.decode()
    status_code, headers, body = parsed_response(r)

    if status_code == 301:
        # Location: https: // movie.douban.com / top250
        url = headers['Location']
        return get(url)
    else:
        return response


def main():
    url = 'https://vip.cocode.cc'
    response = get(url)
    # decode 的 'utf-8' 参数可以省略
    print(response.decode())


# 以下 test 开头的函数是单元测试
def test_parsed_url():
    """
    parsed_url 函数很容易出错,
    所以我们写测试函数来运行看检测是否正确运行
    """
    http = 'http'
    https = 'https'
    host = 'g.cn'
    path = '/'
    test_items = [
        ('http://g.cn', (http, host, 80, path)),
        ('http://g.cn/', (http, host, 80, path)),
        ('http://g.cn:90', (http, host, 90, path)),
        ('http://g.cn:90/', (http, host, 90, path)),
        #
        ('https://g.cn', (https, host, 443, path)),
        ('https://g.cn:233/', (https, host, 233, path)),
    ]
    for t in test_items:
        url, expected = t
        u = parsed_url(url)
        # assert 是一个语句, 名字叫 断言
        # 如果断言成功, 条件成立,
        # 则通过测试, 否则为测试失败, 中断程序报错
        e = "parsed_url ERROR, ({}) ({}) ({})".format(
            url, u, expected
        )
        assert u == expected, e


def test_get():
    """
    测试是否能正确处理请求
    """
    url = 'localhost:3000/login'
    response = get(url).decode()
    expected = 'gua'
    e = "get ERROR, ({}) ({}) ({})".format(url, response, expected)
    assert expected in response, e


def test():
    """
    用于测试的主函数
    """
    test_parsed_url()
    test_get()


if __name__ == '__main__':
    # test()
    main()
