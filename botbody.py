from commutator import transmitter
from botfunctions import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        transmitter(user_id, msg.lower())
        if request == 'Искать':
            creating_database()
            bot.write_message(user_id, f'Приветствую, {bot.name(user_id)}')
            bot.search_user(user_id)
            bot.write_message(event.user_id, f'Нашел подходящего человека, жми на кнопку "Вперёд"')
            bot.find_users(user_id, offset)

        elif request == 'Далее':
            for q in line:
                offset += 1
                bot.find_users(user_id, offset)
                break

        else:
            bot.write_message(event.user_id, 'Введены неверные данные')