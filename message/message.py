import json
import os


class MyMessage:
    def __init__(self, id_sent, id_received, to_chat_id=None, from_chat_id=None):
        if to_chat_id is None and from_chat_id is None:
            raise ValueError('to_chat_id and from_chat_id cannot be None')
        self.id_sent = id_sent
        self.id_received = id_received
        self.to_chat_id = to_chat_id
        self.from_chat_id = from_chat_id

    @staticmethod
    def from_json(obj):
        return MyMessage(
            obj['id-sent'],
            obj['id-received'],
            obj['from-chat-id'],
            obj['to-chat-id'],
        )

    def to_json(self):
        return {
            'id-sent': self.id_sent,
            'id-received': self.id_received,
            'from-chat-id': self.from_chat_id,
            'to-chat-id': self.to_chat_id,
        }

