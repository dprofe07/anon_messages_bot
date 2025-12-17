import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from message import MessagesStorage, MyMessage
from users import User


class AnonMessagesBot:
    def __init__(self, token, users, messages: MessagesStorage):
        self.messages = messages
        self.bot = telebot.TeleBot(token)
        self.users = users

        self.bot.message_handler(commands=['start'])(self.handle_cmd_start)
        self.bot.message_handler()(self.handle_any_message)

        users.notify_admin(self, 'bot started')


    def message_sender_to(self, chat_id):
        return lambda text, **kw: self.send_message(chat_id, text, **kw)

    def handle_receiver_name(self, getter_name, sender_message):
        msg_to_sender = self.message_sender_to(sender_message.chat.id)
        getter = self.users.find_user_by_codename(getter_name)
        if getter is None:
            msg_to_sender("Пользователя с выбранным кодом не существует, проверьте код")
            return

        msg_to_sender("Напишите ваше сообщение, оно отправится собеседнику:")
        self.bot.register_next_step_handler(sender_message, lambda m: self.handle_sending_message(m, getter))

    def handle_sending_message(self, forwarding_message: Message, getter):
        self.send_message(getter.chat_id, "Вам отправлено анонимное сообщение:")
        reply_to = None
        if forwarding_message.reply_to_message is not None:
            reply_id = forwarding_message.reply_to_message.message_id
            sent, received = self.messages.find_messages_by_id(reply_id)
            if sent is not None:
                reply_to = sent.id_received
            if received is not None:
                reply_to = received.id_sent
            if sent is not None and received is not None:
                print("really strange...")

        self.forwarding_message(
            forwarding_message.chat.id,
            getter.chat_id,
            forwarding_message,
            reply_to_message_id=reply_to,
        )
        self.send_message(forwarding_message.chat.id, "Сообщение отправлено!")

    def handle_cmd_start(self, message):
        print(self.users.to_json())
        send_msg = self.message_sender_to(message.chat.id)
        if message.text == '/start':
            if self.users.find_user_by_chat_id(message.chat.id) is not None:
                send_msg(
                    "У вас уже задано имя пользователя. Вы хотите его сменить?",
                    reply_markup=self.get_yes_no_reply_markup()
                )
                self.bot.register_next_step_handler(message, self.handle_yes_no_message(self.change_username, lambda m: None))
                return
            send_msg('Добро пожаловать! Это - бот, позволяющий обмениваться анонимными сообщениями. В отличие от аналогов он не скидывает случайные сообщения и реально анонимен (он вообще не имеет возможности просмотра отправителей). Чтобы написать кому-то просто введите его код или используйте его ссылку.')
            send_msg('А теперь выберите ваш код, по которому вам можно будет написать (русские или латинские буквы, цифры, дефис и нижнее подчеркивание).')
            self.bot.register_next_step_handler(message, self.handle_cmd_set_username)
        else:
            if not self.users.find_user_by_chat_id(message.chat.id):
                self.create_default_username(message)
            getter_name = message.text[7:]
            self.handle_receiver_name(getter_name, message)


    def handle_any_message(self, message):
        if message.text.startswith('/'):
            self.send_message(message.chat.id, "Данная команда неизвестна")
        else:
            if not self.users.find_user_by_chat_id(message.chat.id):
                self.create_default_username(message)
            if message.reply_to_message is not None:
                sent, received = self.messages.find_messages_by_id(message.reply_to_message.message_id)
                getter = None
                if sent is not None:
                    getter = self.users.find_user_by_chat_id(sent.to_chat_id)
                if received is not None:
                    getter = self.users.find_user_by_chat_id(received.from_chat_id)

                if getter is not None:
                    self.handle_sending_message(message, getter)
                else:
                    self.send_message(message.chat.id, "Не удалось распознать пользователя по ответу, попробуйте указать его username")
            else:
                self.handle_receiver_name(message.text, message)

    def handle_cmd_set_username(self, message):
        name = message.text
        send_msg = self.message_sender_to(message.chat.id)
        if not User.check_username(name):
            send_msg("Не используйте спец символы (в том числе пробел) и русские буквы в имени. Введите корректное имя:")
            self.bot.register_next_step_handler(message, self.handle_cmd_set_username)
        elif self.users.find_user_by_codename(name) is not None:
            send_msg( "Данное имя пользователя занято. Введите другое",)
            self.bot.register_next_step_handler(message, self.handle_cmd_set_username)
        else:
            self.users.remove_user_by_chat_id(message.chat.id)
            self.users.add_user(User(name, message.chat.id))
            self.users.save()

            send_msg(f"Теперь вам могут писать по имени: {name}, ссылка: https://t.me/anontextdbot?start={name}")

    def change_username(self, message):
        send_msg = self.message_sender_to(message.chat.id)
        send_msg('Выберите код, по которому вам можно будет написать.')
        self.bot.register_next_step_handler(message, self.handle_cmd_set_username)


    def run(self):
        try:
           self.bot.polling()
        except:
            self.users.notify_admin("Bot falt with an exception, check logs")
            raise

    @staticmethod
    def get_yes_no_reply_markup():
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = KeyboardButton("Да")
        item2 = KeyboardButton("Нет")
        markup.add(item1, item2)
        return markup

    def handle_yes_no_message(self, yes_callback, no_callback):
        def handler(message):
            if message.text == "Да":
                yes_callback(message)
                return
            elif message.text == "Нет":
                no_callback(message)
                return
            else:
                self.send_message(message.chat.id, "Нажмите кнопку или введите \"Да\" или \"Нет\" (без кавычек)")
                self.bot.register_next_step_handler(message, handler)
        return handler


    def send_message(self, chat_id, message, reply_markup=None, **kw):
        if reply_markup is None:
            reply_markup = ReplyKeyboardRemove()

        return self.bot.send_message(chat_id, message, reply_markup=reply_markup, **kw)

    def forwarding_message(self, from_chat_id, to_chat_id, message: Message, **kw):
        received_id = self.send_message(to_chat_id, message.text, **kw)
        self.messages.add_message(MyMessage(
            message.id, received_id.message_id,
            to_chat_id, from_chat_id
        ))
        self.messages.save()

    def create_default_username(self, message):
        user = User(str(message.chat.id), message.chat.id)
        self.users.add_user(user)
        self.users.save()
        self.send_message(
            message.chat.id,
            f"Вы не были зарегистрированы, вам выдан стандартный код, "
            f"по которому вам могут писать: {message.chat.id} (ссылка: https://t.me/anontextdbot?start={message.chat.id}). Вы можете его сменить с помощью команды /start")

