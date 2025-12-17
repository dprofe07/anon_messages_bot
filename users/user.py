class User:
    ALLOWED_USERNAME_SYMBOLS = (
        'qwertyuiopasdfghjklzxcvbnm'
        'QWERTYUIOPASDFGHJKLZXCVBNM'
        'ёйцукенгшщзхъфывапролджэячсмитьбю'
        'ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
        '1234567890-_+'
    )

    def __init__(self, codename, chat_id):
        self.codename = codename
        self.chat_id = chat_id

    def __repr__(self):
        return f'User({repr(self.codename)}, {self.chat_id})'

    def to_json(self):
        return {
            'codename': self.codename,
            'chat_id': self.chat_id
        }

    @staticmethod
    def from_json(i):
        return User(i.get('codename'), i.get('chat_id'))

    @staticmethod
    def check_username(codename):
        return all([i in User.ALLOWED_USERNAME_SYMBOLS for i in codename])


