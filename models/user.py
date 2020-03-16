from models import Model


class User(Model):
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.note = form.get('note', '')

    def validate_login(self):
        # us = User.all()
        # for u in us:
        #     if u.username == self.username and u.password == self.password:
        #         return True
        # return False
        u = User.find_by(username=self.username)
        # 0 None ''
        # return u and u.password == self.password
        return u is not None and u.password == self.password

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2
