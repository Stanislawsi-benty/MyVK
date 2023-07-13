# импорты
import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine

from config import community_token, access_token, db_url_object
from core import VkTools
from database import add_user, check_user

element = ()
users = []


class BotInterface():

    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.res = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def add_element(self, element):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command2 = event.text.lower()

                if element == 'bdate':
                    self.params["bdate"] = command2
                elif element == 'home_town':
                    self.params["home_town"] = command2
                elif element == 'sex':
                    self.params["sex"] = command2
                elif element == 'city':
                    self.params["city"] = command2
                else:
                    self.message_send(event.user_id, 'ААА')
            bot.event_handler()

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        global element, users

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}!')
                    users = self.api.search_users(self.params, 10)
                    # print(self.params["id"])  # Дописать запрос данны
                    for i in self.params.items():
                        if i[1] == '' or i[1] is None:
                            self.message_send(event.user_id, f'Введите параметр {i[0]}')
                            element = i[0]
                            bot.add_element(element)
                elif command == 'поиск':

                    if users:
                        # здесь логика дял проверки бд
                        self.res = True
                        while self.res is True:
                            user = users.pop()
                            self.res = check_user(engine=create_engine(db_url_object), profile_id=self.params["id"],
                                                  worksheet_id=user["id"])

                        else:
                            photos_user = self.api.get_photos(user['id'])

                            attachment = ''
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                                if num == 2:
                                    break
                            self.message_send(event.user_id,
                                              f'Встречайте! {user["name"]}, ссылка: vk.com/id{user["id"]}',
                                              attachment=attachment
                                              )
                            add_user(engine=create_engine(db_url_object), profile_id=self.params["id"],
                                     worksheet_id=user["id"])
                    else:
                        self.message_send(event.user_id, 'Подбираем анкеты, нажмите "поиск" снова')
                        users = self.api.search_users(self.params, 20)
                elif command == 'пока':
                    self.message_send(event.user_id, 'Пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
    bot.add_element()
