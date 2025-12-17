from anon_messages_bot import AnonMessagesBot
from message import MessagesStorage
from users import UsersStorage

TOKEN = open('token.txt').read().strip()

users = UsersStorage("users.txt")
users.load()

messages = MessagesStorage('messages.txt')
messages.load()

bot = AnonMessagesBot(TOKEN, users, messages)

bot.run()