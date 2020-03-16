import hmac
import json
import base64
import hashlib
import time
from models import Model


class JWT(Model):
    # JWT 只需要存 key，然后再验证 session
    #
    def __init__(self, form):
        super().__init__(form)
        self.key = form.get("key", "")
        self.username = form.get('username', '')


    @staticmethod
    def base64url_encode(input: bytes):
        r = base64.urlsafe_b64encode(input)
        # 返回时要把base64编码结尾的=号去除掉
        return r.replace(b'=', b'')

    @staticmethod
    def base64url_decode(input: bytes):
        # 解码时要把base64的结尾=号补齐, base64以4为一个单元
        l = len(input)
        y = (l % 4) * b'='
        input += y
        return base64.urlsafe_b64decode(input)

    def encode(self, header, payload):
        pass

    def validate(self, header_payload, signature):
        pass

    def decode(self, jwt_bytes):
        pass

    def signature(self):
        # 包装 Header，Payload 信息，加密，进行签名，使用 Hmac sha256

        header = json.dumps({
            "alg": "HS256",
            "typ": "JWT"
        })

        payload = json.dumps({
            "iss": "pika",  # 签发人
            "exp": time.time()+886400,  # 过期时间
            "iat": time.time(),  # 签发时间
            "name": self.username,
            "admin": True
        })

        header_encode = self.base64url_encode(header)
        header_payload = self.base64url_encode(payload)

        # todo
        # 自己写个签名，在用官方的 jwt 库签下名




        sign = hmac.new(self.key, input, digestmod=hashlib.sha256)
        return self.base64url_encode(sign.digest())

    def dumps(self, dt):
        return json.dumps(dt, separators=(',', ':'), ensure_ascii=False)

    def load(self, dt):
        return json.loads(dt)
