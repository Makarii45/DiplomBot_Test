from vk_api.longpoll import VkEventType, VkLongPoll
from bot import *
from db import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id
        if request == 'старт' or request == 'f':
            bot.get_age_of_user(user_id)
            bot.get_city(user_id)
            bot.get_persons(user_id)
            bot.show_person(user_id)  # выводит в чат инфо одного человека из базы данных.
        elif request == 'смотреть' or request == 's':
            if bot.get_found_person_id() != 0:
                bot.show_found_person(user_id)
            else:
                bot.msg(user_id, f' В начале наберите старт или f.  ')
        else:
            bot.msg(user_id, f'{bot.name(user_id)} Бот готов к поиску, наберите: \n '
                                      f' "старт или F" - Поиск людей. \n'
                                      f' "смотреть или S" - просмотр следующей анкеты. (Не набирайте, если не было поиска!)')