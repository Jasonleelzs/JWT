import hmac
import json
import base64
import hashlib


class JWT(object):

    def __init__(self, key):
        self.key = key

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
        header_json = self.dumps(header)
        payload_json = self.dumps(payload)
        header_byte = str.encode(header_json)
        payload_byte = str.encode(payload_json)
        header_b64_byte = self.base64url_encode(header_byte)
        payload_b64_byte = self.base64url_encode(payload_byte)

        # 开始签名
        sign_input = header_b64_byte + b'.' + payload_b64_byte
        signature_b64_byte = self.signature(sign_input)
        return header_b64_byte + b'.' + payload_b64_byte + b'.' + signature_b64_byte

    def validate(self, header_payload, signature):
        signature_b64_byte = self.signature(header_payload)
        return signature_b64_byte != signature

    def decode(self, jwt_bytes):
        header_b64, payload_b64 = jwt_bytes.split(b'.')[:2]
        header_json = self.base64url_decode(header_b64)
        payload_json = self.base64url_decode(payload_b64)
        return header_json, payload_json


    def signature(self, input):
        # 对前Header.Payload进行签名, 使用Hmac sha256
        sign = hmac.new(self.key, input, digestmod=hashlib.sha256)
        return self.base64url_encode(sign.digest())

    def dumps(self, dt):
        return json.dumps(dt, separators=(',', ':'), ensure_ascii=False)

    def load(self, dt):
        return json.loads(dt)


if __name__ == '__main__':
    pass
