import telebot
import json
import vk_api

from datetime import date
from datetime import datetime
import pytz
import time


class FriendsBirths:
    def __init__(
            self,
            vk_client,
            user_id,
            count,
            bot
    ):
        self._vk_client = vk_client
        self._user_id = user_id
        self._count = count
        self._bot = bot

    @staticmethod
    def from_config(
            json_path: str,
            user_id: int,
            count: int,
            bot: telebot
    ):
        with open(json_path, 'r') as json_file:
            client_credentials = json.load(json_file)

        vk_session = vk_api.VkApi(
            client_credentials['email_or_phone_number'],
            client_credentials['password'],
        )
        vk_session.auth()
        vk_client = vk_session.get_api()
        return FriendsBirths(
            vk_client,
            user_id,
            count,
            bot
        )

    def _births(self):
        error = 0
        try:
            vk_friends = self._vk_client.friends.get(
                user_id=self._user_id,
                fields=['bdate'],
                order='name'
            )
        except BaseException:
            error = 1
        if error == 1:
            return -1
        months = [
            "Января",
            "Февраля",
            "Марта",
            "Апреля",
            "Мая",
            "Июня",
            "Июля",
            "Августа",
            "Сентября",
            "Октября",
            "Ноября",
            "Декабря"]
        tz = pytz.timezone('Europe/Moscow')
        now_date = datetime.now(tz)
        near_births = dict()
        y, m, d = str(now_date)[:10].split('-')
        for friend in vk_friends['items']:
            if not (not friend.get('deactivated')
                    is None and friend.get('deactivated') == 'deleted'):
                date_of_birth = friend.get('bdate')
                if date_of_birth is not None:
                    fir_name, sec_name = friend.get(
                        'first_name'), friend.get('last_name')
                    day, mon = date_of_birth.split(
                        '.')[0], date_of_birth.split('.')[1]
                    date_b = str(datetime.now().year) + ' ' + \
                        str(mon) + ' ' + str(day)
                    d1 = date(int(y), int(mon), int(day))
                    d2 = date(int(y), int(m), int(d))
                    diff = (d1 - d2).days
                    if diff < 0:
                        if ((int(y) + 1) %
                            4 == 0 and (int(y) + 1) %
                            100 != 0) or ((int(y) + 1) %
                                          400 == 0):
                            diff += 366
                        else:
                            diff += 365
                    if diff <= self._count:
                        fir_name, sec_name = friend.get(
                            'first_name'), friend.get('last_name')
                        full_name = ''
                        if fir_name is not None:
                            full_name += fir_name
                        if sec_name is not None:
                            full_name += ' '
                            full_name += sec_name
                        near_births[full_name] = [diff, day,
                                                  months[int(mon) - 1], str(friend['id'])]
        sorted_births = sorted(near_births.items(), key=lambda val: val[1][0])
        return sorted_births


changed_id = 0
changed_days = 0
was_id = 0
was_count = 0
id = 0
kol = 0
command = 0
token = open("bot_token", 'r')
bot = telebot.TeleBot(token.read().strip())
token.close()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    global command
    if command == 1:
        bot.send_message(
            chat_id,
            "Сначала закончите выполнение предыдущей команды")
    else:
        bot.send_message(
            chat_id,
            f'Здравствуйте, {message.from_user.first_name}\nДля ознакомления с ботом напишите команду /help')


@bot.message_handler(commands=['help'])
def get_help(message):
    global command
    chat_id = message.chat.id
    if command == 1:
        bot.send_message(
            chat_id,
            "Сначала закончите выполнение предыдущей команды")
    else:
        bot.send_message(chat_id, 'Данный бот помогает узнать у каких друзей пользователя вконтакте дни рождения в ближайшие дни.\nНужно ввести vk id пользователя, предварительно удостоверившись, что его страница не является приватной.\n\nИспользуйте следующие функции для взаимодействия с ботом:\n1) /go - начать работу\n2) /change_days - сменить количество дней, оставив vk id прежним\n3)  /change_id - сменить vk id, оставив количество дней прежним\n\nОбратите внимание, что в самом начале нужно использовать команду /go')


@bot.message_handler(commands=['go'])
def launch(message):
    global command
    chat_id = message.chat.id
    if (command == 1):
        bot.send_message(
            chat_id,
            "Сначала закончите выполнение предыдущей команды")
    else:
        global changed_id
        global was_id
        global was_count
        global changed_days
        global id
        global kol
        bot.send_message(
            chat_id,
            'Введити vk id в формате 173349671\nПо данной ссылке вы можете найти нужный vk id: https://regvk.com/id/')
        command = 1
        changed_days = 0
        changed_id = 0
        was_id = 0
        was_count = 0
        id = 0
        kol = 0


@bot.message_handler(commands=['change_id'])
def change_vk_id(message):
    global command
    chat_id = message.chat.id
    global changed_id
    if command == 1:
        bot.send_message(
            chat_id,
            "Сначала закончите выполнение предыдущей команды")
    else:
        changed_id = 1
        command = 1
        bot.send_message(
            chat_id,
            'Введите новый vk id в формате 173349671\nПо данной ссылке вы можете найти vk id: https://regvk.com/id/')


@bot.message_handler(commands=['change_days'])
def change_number_of_days(message):
    global command
    chat_id = message.chat.id
    global changed_days
    if command == 1:
        bot.send_message(
            chat_id,
            "Сначала закончите выполнение предыдущей команды")
    else:
        changed_days = 1
        command = 1
        bot.send_message(chat_id, 'Введите новое количество дней')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id
    global command
    global changed_id
    global changed_days
    global was_id
    global was_count
    global id
    global kol
    if (command == 0):
        bot.reply_to(message, 'Неопознанная команда')
        return
    mess = message.text
    if changed_id == 1:
        if not mess.isdigit():
            was_id = 0
            bot.reply_to(
                message,
                'Неправильный формат vk id, попробуйте снова')
        else:
            was_id = 1
            id = int(mess)
    elif changed_days == 1:
        if not mess.isdigit():
            bot.reply_to(message, 'Неправильный формат, попробуйте снова')
            was_count = 0
        else:
            kol = int(mess)
            was_count = 1
            changed_days = 0
    else:
        if was_id == 0:
            if not mess.isdigit():
                bot.reply_to(
                    message, 'Неправильный формат vk id, попробуйте снова')
                was_id = 0
            else:
                id = int(mess)
                was_id = 1
                bot.send_message(
                    chat_id,
                    'Введите количество дней насколько дней вперед вы хотите узнать дни рождения')
        else:
            if not mess.isdigit():
                bot.reply_to(
                    message, 'Неправильный формат количества дней, попробуйте снова')
            else:
                kol = int(mess)
                was_count = 1
    if was_id == 1 and was_count == 1:
        friends_births = FriendsBirths.from_config(
            json_path='vk_api_credentials.json',
            user_id=id,
            count=kol,
            bot=bot
        )
        sort_births = friends_births._births()
        if (sort_births == -1):
            bot.send_message(
                chat_id,
                'Данный профиль закрыт или не существует.\nДля использования бота удостоверьтесь, что профиль существует или сделайте профиль не приватным и вызовите команду /change_id')
        else:
            changed_id = 0
            if (len(sort_births) == 0):
                bot.send_message(
                    chat_id, "В ближайшее указанное количество дней нет дней рождения")
            else:
                days_count = ''
                for person in sort_births:
                    if (person[1][0] == 0):
                        bot.send_message(chat_id, "У пользователя: " +
                                         person[0] +
                                         '\n' +
                                         'https://vk.com/id' +
                                         str(person[1][3]) +
                                         '\n' +
                                         'Cегодня день рождения' +
                                         ' ' +
                                         '(' +
                                         person[1][1] +
                                         ' ' +
                                         person[1][2] +
                                         ')')
                        continue
                    if (str(person[1][0])[-1] == '1' and person[1][0] != 11):
                        days_count = 'день'
                    elif ((str(person[1][0])[-1] == '2' or str(person[1][0])[-1] == '3' or str(person[1][0])[-1] == '4') and person[1][0] != 12 and person[1][0] != 13 and person[1][0] != 14):
                        days_count = 'дня'
                    else:
                        days_count = 'дней'
                    bot.send_message(chat_id, "У пользователя: " +
                                     person[0] +
                                     '\n' +
                                     'https://vk.com/id' +
                                     str(person[1][3]) +
                                     '\n' +
                                     'День рождения через ' +
                                     str(person[1][0]) +
                                     ' ' +
                                     days_count +
                                     ' ' +
                                     '(' +
                                     person[1][1] +
                                     ' ' +
                                     person[1][2] +
                                     ')')
                    time.sleep(0.05)
        command = 0
        bot.send_message(chat_id, text="Введите следующую команду для бота")


bot.polling(none_stop=True)
