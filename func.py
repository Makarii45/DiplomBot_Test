import vk_api
import psycopg2
import datetime
from conf import bot_token, acces_token
from vk_api.longpoll import VkLongPoll, VkEventType
from db import insert_user, insert_result_user, get_user_db_id, check_result_user

vk_bot_token = vk_api.VkApi(token = bot_token)
vk_app_token = vk_api.VkApi(token = acces_token)
long_poll = VkLongPoll(vk_bot_token)


def write_msg(user_id, message):
    vk_bot_token.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0, })


def write_photo_msg(user_id, message, selected_user, photo_list):
    attachment = ''
    for photo_id in photo_list:
        attachment += f"photo{selected_user['id']}_{photo_id},"

    vk_bot_token.method('messages.send', {'user_id': user_id, 'message': message, "attachment": attachment,
                                          'random_id': 0, })


def get_city(city):
    values = {
        'country_id': 1,
        'q': city,
        'count': 1
    }
    response = vk_app_token.method('database.getCities', values=values)
    try:
        city_id = response['items'][0]['id']
    except vk_api.exceptions.VkApiError as _vae:
        print('get_city', _vae, type(_vae))
        return False
    except IndexError:
        return False
    except Exception as _ex:
        print('get_city', _ex, type(_ex))
        return False
    return city_id


def bdate_to_age(bdate):
    age = datetime.datetime.now().year - int(bdate[-4:])
    return age


def get_user_info(user_id):
    user_info_dict = {}
    try:
        response = vk_bot_token.method('users.get', {'user_id': user_id,
                                                     'v': 5.131,
                                                     'fields': 'first_name, last_name, bdate, sex, city'})
    except vk_api.exceptions.VkApiError as _vae:
        print('get_user_info', _vae, type(_vae))
        response = False
    except Exception as _ex:
        print('get_user_info', _ex, type(_ex))
        response = False

    if response is not False:
        for key, values in response[0].items():
            if key == 'is_closed' or key == 'can_access_closed':
                break
            elif key == 'city':
                user_info_dict[key] = values['id']
            else:
                user_info_dict[key] = values
    else:
        return False
    return user_info_dict


def get_additional_information(user_info):
    user_info = user_info
    for event in long_poll.listen():
        if 'bdate' not in user_info or len(user_info['bdate'].split('.')) != 3:
            if 'bdate' in user_info:
                user_info.pop('bdate')
            write_msg(event.user_id, "Введите ваш возраст (только цифры):")
            for event in long_poll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request_age = event.text.lower().strip()
                        try:
                            user_info['age'] = int(request_age)
                            break
                        except ValueError as _ve:
                            print('get_additional_information', _ve, type(_ve))
                            write_msg(event.user_id, "Неверный формат возраста, "
                                                     "вводите только цифры:")
                            continue

        else:
            user_info['age'] = bdate_to_age(user_info['bdate'])
            user_info.pop('bdate')

        if 'city' not in user_info:
            write_msg(event.user_id, "Введите ваш город:")
            for event in long_poll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request_city = event.text.lower().strip()
                        if get_city(request_city) is not False:
                            user_info['city'] = get_city(request_city)
                            break
                        else:
                            write_msg(event.user_id, 'Неверно указан город! Введите правильное полное название:')
                            continue

        return user_info


def get_users_list(user_info):

    if user_info['age'] - 3 < 18:
        start_find_age = 18
    else:
        start_find_age = user_info['age'] - 3
    end_find_age = user_info['age'] + 3

    user_list = []
    try:
        response = vk_app_token.method('users.search', {
                                        'age_from': start_find_age,
                                        'age_to': end_find_age,
                                        'sex': 3 - user_info['sex'],
                                        'city': user_info['city'],
                                        'status': 6,
                                        'has_photo': 1,
                                        'count': 100,
                                        'v': 5.131})
    except vk_api.exceptions.VkApiError as _vae:
        print('get_users_list', _vae, type(_vae))
        return False
    except Exception as _ex:
        print('get_users_list', _ex, type(_ex))
        return False

    if response.get('count') != 0:
        if response.get('items'):
            for items in response.get('items'):
                if items['is_closed']:
                    continue
                else:
                    user_list.append(items)
            return user_list
    else:
        return False
    return False


def get_photos(selected_user):
    try:
        response = vk_app_token.method('photos.get', {'owner_id': selected_user['id'],
                                                      'album_id': f'profile',
                                                      'photo_sizes': 1,
                                                      'count': 1000,
                                                      'extended': 1})
    except vk_api.exceptions.VkApiError as _vae:
        print('get_photos', _vae, type(_vae))
        return False
    except Exception as _ex:
        print(_ex, type(_ex))
        return False

    return response


def get_most_popular_photo(photos_info):
    photo_info_dict = {}
    link_id_list = []
    for items in photos_info.get('items'):
        key = items.get('id')
        photo_info_dict[key] = items.get('likes').get('count') + items.get('comments').get('count')
    photo_info_dict = sorted(photo_info_dict.items(), key=lambda x: x[1], reverse=True)[:3]
    for key, values in photo_info_dict:
        link_id_list.append(key)
    return link_id_list

def loop():

    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower().strip()
                if request == "старт":
                    conn = psycopg2.connect(database="vkdb", user="postgres", password="123")

                    user_info = get_user_info(event.user_id)

                    if user_info is not False:
                        if len(user_info) != 6 or len(user_info['bdate'].split('.')) != 3:
                            write_msg(event.user_id, "Недостаточно информации, пожалуйста, заполните пробелы &#128373;")
                            user_info = get_additional_information(user_info)
                            if user_info is False:
                                continue
                        else:
                            user_age = bdate_to_age(user_info['bdate'])
                            user_info['age'] = user_age
                            if 'bdate' in user_info:
                                user_info.pop('bdate')
                    else:
                        write_msg(event.user_id, "Ошибка...")
                        break

                    user_db_id = get_user_db_id(conn, user_info['id'])

                    if user_db_id is False:
                        user_db_id = insert_user(conn, user_info)

                    users_list = get_users_list(user_info)
                    status = True
                    last_user = users_list[-1]

                    if users_list is not False:
                        write_msg(event.user_id, "Поиск!")
                        for user in users_list:
                            if user == last_user and check_result_user(conn, user.get('id'), user_db_id) is False:
                                write_msg(event.user_id, "Больше никого нет...")
                                users_list = get_users_list(user_info)
                            else:
                                check = check_result_user(conn, user.get('id'), user_db_id)
                                if check:
                                    if status:
                                        photos_info = get_photos(user)
                                        if photos_info is not False:
                                            if photos_info.get('count') < 3:
                                                continue
                                            else:
                                                photos_link = get_most_popular_photo(photos_info)
                                                write_photo_msg(event.user_id,
                                                                f"""Вам подходит {user.get('first_name')} """
                                                                f"""{user.get('last_name')} &#128150;\n"""
                                                                f"""Профиль: https://vk.com/id{user.get('id')}\n"""
                                                                f"""Топ фоторафий:""", user,
                                                                photos_link)

                                                insert_result_user(conn, user_db_id, user)

                                                write_msg(event.user_id, """Продолжить? 
                                                                            Чтобы продолжить, введите "дальше",
                                                                            чтобы закончить, введите "закончить". """)
                                                for event in long_poll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW:
                                                        if event.to_me:
                                                            request = event.text.lower().strip()
                                                            if request == 'дальше':
                                                                write_msg(event.user_id, "Поиск")
                                                                break
                                                            elif request == 'закончить':
                                                                write_msg(event.user_id, "Завершение")
                                                                status = False
                                                                break
                                                            else:
                                                                write_msg(event.user_id, """Чтобы продолжить, введите \
                                                                "дальше",\nчтобы закончить, введите "закончить" """)
                                        else:
                                            continue
                                    else:
                                        break
                                else:
                                    continue
                    else:
                        write_msg(event.user_id, "Ошибка...")
                        break
                    conn.close()

                else:
                    write_msg(event.user_id, f"""Вас приветствует бот VKinder, введите "старт", чтобы начать.""")