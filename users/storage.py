import json
import os
from .user import User

class UsersStorage:
    ADMIN_USERNAME = "dprofe"

    def __init__(self, filename):
        self.users = []
        self.filename = filename

    def find_user_by_codename(self, codename):
        for u in self.users:
            if u.codename == codename:
                return u
        return None

    def find_user_by_chat_id(self, chat_id):
        for u in self.users:
            if u.chat_id == chat_id:
                return u
        return None

    def admin(self):
        return self.find_user_by_codename(UsersStorage.ADMIN_USERNAME)

    def notify_admin(self, bot, message):
        admin = self.admin()
        if admin:
            bot.send_message(admin.chat_id, message)


    def add_user(self, user):
        self.users.append(user)

    def remove_user_by_chat_id(self, chat_id):
        for u in self.users:
            if u.chat_id == chat_id:
                self.users.remove(u)

    def save(self):
        with open(self.filename, 'w') as file:
            json.dump(self.users, file, default=lambda o: o.to_json())

    def load(self):
        if not os.path.exists(self.filename):
            self.save()
        with open(self.filename, 'r') as file:
            self.users = UsersStorage.from_json(json.load(file))

    def to_json(self):
        return self.users

    @staticmethod
    def from_json(obj):
        return [User.from_json(i) for i in obj]
