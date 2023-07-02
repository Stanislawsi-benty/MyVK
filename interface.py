# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine

from config import comunity_token, acces_token, db_url_object
from core import VkTools
from database import add_user, check_user


class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
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

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}!')
                    print(self.params["id"])  # Дописать запрос данны
                elif command == 'поиск':
                    users = self.api.search_users(self.params)
                    user = users.pop()
                    # здесь логика дял проверки бд

                    self.res = check_user(engine=create_engine(db_url_object), profile_id=self.params["id"],
                                          worksheet_id=user["id"])

                    # while self.res is True:
                    #     print(1)
                    # else:
                    #     print(2)
                    if self.res == True:
                        # VkTools.get_profile_info(self=self, user_id=264654654)
                        VkTools.search_users(params=VkTools.get_profile_info(self, user_id=264654654))
                        bot.event_handler()
                    else:
                        pass

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
                    # здесь логика для добавленяи в бд
                    add_user(engine=create_engine(db_url_object), profile_id=self.params["id"], worksheet_id=user["id"])
                elif command == 'пока':
                    self.message_send(event.user_id, 'Пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
