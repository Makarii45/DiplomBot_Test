import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime

bot_token = input('Введите токен бота группы с необходимыми правами: ')
user_token = input('Введите токен приложения с необходимыми правами: ')

vk_bot_token = vk_api.VkApi(token=bot_token)
vk_app_token = vk_api.VkApi(token=user_token)

long_poll = VkLongPoll(vk_bot_token)


def write_msg(user_id, message, attachment=None):
    params = {'user_id': user_id, 'message': message, 'random_id': 0}
    if attachment:
        params['attachment'] = attachment
    vk_bot_token.method('messages.send', params)


def get_city(city):
    values = {'country_id': 1, 'q': city, 'count': 1}
    try:
        response = vk_app_token.method('database.getCities', values=values)
        city_id = response['items'][0]['id']
    except (vk_api.exceptions.VkApiError, IndexError, Exception) as e:
        print(f'get_city {e} {type(e)}')
        return False
    return city_id


def bdate_to_age(bdate):
    return datetime.datetime.now().year - int(bdate[-4:])


def get_user_info(user_id):
    try:
        response = vk_bot_token.method('users.get', {'user_id': user_id,
                                                     'v': 5.131,
                                                     'fields': 'first_name, last_name, bdate, sex, city'})
        user_info_dict = {key: values for key, values in response[0].items()
                          if key not in ('is_closed', 'can_access_closed')}
        user_info_dict['city'] = user_info_dict['city']['id']
    except (vk_api.exceptions.VkApiError, Exception) as e:
        print(f'get_user_info {e} {type(e)}')
        return False
    return user_info_dict


def get_additional_information(user_info):
    for event in long_poll.listen():
        if 'bdate' not in user_info or len(user_info['bdate'].split('.')) != 3:
            if 'bdate' in user_info:
                user_info.pop('bdate')
            write_msg(user_info['id'], "Ваш возраст (только цифры):")
            for event in long_poll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    request_age = event.text.lower().strip()
                    try:
                        user_info['age'] = int(request_age)
                        break
                    except ValueError:
                        write_msg(user_info['id'], "Вводите только цифры:")
                        continue
        else:
            user_info['age'] = bdate_to_age(user_info['bdate'])
            user_info.pop('bdate')

        if user_info['age'] < 18:
            write_msg(user_info['id'], "Сервис недоступен для лиц моложе 18 лет! &#128286;")
            return False

        if 'city' not in user_info:
            write_msg(user_info['id'], "Введите ваш город:")
            for event in long_poll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    request_city = event.text.lower().strip()
                    city_id = get_city(request_city)
                    if city_id is not False:
                        user_info['city'] = city_id
                        break
                    else:
                        write_msg(user_info['id'], 'Неверный город!:')
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
            'count': 1000,
            'v': 5.131})
    except vk_api.exceptions.VkApiError as e:
        print(f'get_users_list {e} {type(e)}')
        return False

    if response.get('count') != 0 and response.get('items'):
        for items in response.get('items'):
            if not items['is_closed']:
                user_list.append(items)
        return user_list
    else:
        return False


def get_photos(selected_user):
    try:
        response = vk_app_token.method('photos.get', {
            'owner_id': selected_user['id'],
            'album_id': f'profile',
            'photo_sizes': 1,
            'count': 1000,
            'extended': 1})
    except vk_api.exceptions.VkApiError as e:
        print(f'get_photos {e} {type(e)}')
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