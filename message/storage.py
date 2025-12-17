import json
import os

from . import MyMessage


class MessagesStorage:
    def __init__(self, filename):
        self.filename = filename
        self.messages = []

    def save(self):
        with open(self.filename, 'w') as file:
            json.dump(self.messages, file, default=lambda o: o.to_json())

    def load(self):
        if not os.path.exists(self.filename):
            self.save()
        with open(self.filename, 'r') as file:
            self.messages = MessagesStorage.from_json(json.load(file))

    def to_json(self):
        return self.messages

    @staticmethod
    def from_json(obj):
        return [MyMessage.from_json(i) for i in obj]

    def add_message(self, message: MyMessage):
        self.messages.append(message)

    def find_message_by_id_sent(self, id_sent):
        for m in self.messages:
            if m.id_sent == id_sent:
                return m
        return None

    def find_message_by_id_received(self, id_received):
        for m in self.messages:
            if m.id_received == id_received:
                return m
        return None

    def find_messages_by_id(self, reply_id) -> (MyMessage, MyMessage):
        return self.find_message_by_id_sent(reply_id), self.find_message_by_id_received(reply_id)