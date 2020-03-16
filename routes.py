from utils import log
from models.message import Message
from models.user import User
from models.session import Session

import random


def random_str():
    """
    生成一个随机的字符串
    """
    seed = 'bdjsdlkgjsklgelgjelgjsegker234252542342525g'
    s = ''
    for i in range(16):
        # 这里 len(seed) - 2 是因为我懒得去翻文档来确定边界了
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def template(name):
    """
    根据名字读取 templates 文件夹里的一个文件并返回
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# 验证 request 的 Cookie 在 session.txt 里有没有保存
# 有的话就是用户，没有的话就是游客
def current_user(request):
    session_id = request.cookies.get('user', '')
    sessions = Session.all()
    for s in sessions:
        if s.session_id == session_id:
            return s.username
    return '【游客】'


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    username = current_user(request)
    body = body.replace('{{username}}', username)
    r = header + '\r\n' + body
    return r.encode()


def response_with_headers(headers):
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    header = 'HTTP/1.x 210 VERY OK\r\n'
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def route_login(request):
    """
    登录页面的路由函数
    cookie and session 的流程：
    先判断 request 中的 cookie 拿到 username,
    进去是 login 页面, 有 cookie, 你就直接登录，没有就是游客，
    要登陆，request.method 是 POST，就是手动登录，
    验证登录通过了，就设置一个 session_id 来对应 username，把 session_id 发给客户端。
    """
    headers = {
        'Content-Type': 'text/html',
    }
    log('login headers', request.headers)
    log('login cookies', request.cookies)
    username = current_user(request)
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            # session 中文 会话
            # token 中文 令牌
            # 设置一个随机字符串当令牌来使用
            session_id = random_str()
            s = Session.new(dict(
                session_id=session_id,
                username=u.username,
            ))
            log('session', s)
            s.save()
            headers['Set-Cookie'] = 'user={}'.format(session_id)

            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''
    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode()


def route_register(request):
    """
    注册页面的路由函数
    """
    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode()


def route_message(request):
    """
    主页的处理函数, 返回主页的响应
    这个页面只对的路过的用户开放
    GET /messages?message=123&author=gua HTTP/1.1
    Host: localhost:3000
    """
    username = current_user(request)
    if username == '【游客】':
        return error(request)
    else:
        form = request.query
        if len(form) > 0:
            m = Message.new(form)
            m.save()

        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
        body = template('messages.html')
        ms = '<br>'.join([str(m) for m in Message.all()])
        body = body.replace('{{messages}}', ms)
        r = header + '\r\n' + body
        return r.encode()


def route_message_add(request):
    """
    主页的处理函数, 返回主页的响应
    POST /messages HTTP/1.1
    Host: localhost:3000
    Content-Type: application/x-www-form-urlencoded

    message=123&author=gua
    """
    # log('本次请求的 method', request.method)
    form = request.form()
    m = Message.new(form)
    # 应该在这里保存 message_list
    m.save()

    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('messages.html')
    ms = '<br>'.join([str(m) for m in Message.all()])

    body = body.replace('{{messages}}', ms)
    r = header + '\r\n' + body
    return r.encode()


def route_profile(request):
    username = current_user(request)
    if username == '【游客】':
        header = 'HTTP/1.1 302 Found\r\nlocation: http://localhost:3000/\r\nContent-Type: text/html'
        r = header
        return r.encode()
    else:
        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
        body = template('profile.html')
        user = User.find_by(username=username)
        result = str(user)
        body = body.replace('{{xxx}}', result)
        r = header + '\r\n' + body
        return r.encode()


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename = request.query.get('file', 'doge.gif')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.x 200 OK\r\nContent-Type: image/gif\r\n\r\n'
        img = header + f.read()
        return img


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/': route_index,
        '/login': route_login,
        '/register': route_register,
        '/messages': route_message,
        '/messages/add': route_message_add,
        '/profile': route_profile,
    }
    return d


def error(request, code=404):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    # 之前上课我说过不要用数字来作为字典的 key
    # 但是在 HTTP 协议中 code 都是数字似乎更方便所以打破了这个原则
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')

