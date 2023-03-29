from config import user_token, comm_token, offset, line
import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from base import *


class SearchBot:
    def __init__(self):
        print('Бота удалось создать')
        self.vk = vk_api.VkApi(token=comm_token)  # Авторизация сообщества
        self.longpoll = VkLongPoll(self.vk)  # Обработка сообщений

    def write_message(self, user_id, message):
        """ Отправка сообщений"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def name(self, user_id):
        """Запрос имени пользователя бота"""
        url = f'https://api.vk.com/method/users.get'
        options = {'access_token': user_token,
                  'user_ids': user_id,
                  'v': '5.131'}
        replacement = requests.get(url, options=options)
        answer = replacement.json()
        try:
            information_data = answer['answer']
            for q in information_data:
                for key, value in q.items():
                    first_name = q.get('first_name')
                    return first_name
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    def sex(self, user_id):
        """Получение пола, меняет на противоположный"""
        url = f'https://api.vk.com/method/users.get'
        options = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'sex',
                  'v': '5.131'}
        replacement = requests.get(url, options=options)
        answer = replacement.json()
        try:
            information_data = answer['answer']
            for q in information_data:
                if q.get('sex') == 2:
                    find_sex = 1
                    return find_sex
                elif q.get('sex') == 1:
                    find_sex = 2
                    return find_sex
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    def lower_age(self, user_id):
        """Получение нижней границы возраста"""
        url = url = f'https://api.vk.com/method/users.get'
        options = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        replacement = requests.get(url, options=options)
        answer = replacement.json()
        try:
            information_data = answer['answer']
            for q in information_data:
                date = q.get('bdate')
            list_date = date.split('.')
            if len(list_date) == 3:
                year = int(list_date[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(list_date) == 2 or date not in information_data:
                self.write_msg(user_id, 'Укажите нижнюю границу возраста (min - 16): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')


    def upper_age(self, user_id):
        """Получение верхней границы возраста"""
        url = url = f'https://api.vk.com/method/users.get'
        options = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        replacement = requests.get(url, options=options)
        answer = replacement.json()
        try:
            information_data = answer['answer']
            for q in information_data:
                date = q.get('bdate')
            list_date = date.split('.')
            if len(list_date) == 3:
                year = int(list_date[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(list_date) == 2 or date not in information_data:
                self.write_message(user_id, 'Введите верхний порог возраста (max - 65): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    
    def city_id(self, user_id, city_name):
        """Получение id города пользователя"""
        url = url = f'https://api.vk.com/method/database.getCities'
        options = {'access_token': user_token,
                  'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': '5.131'}
        replacement = requests.get(url, options=options)
        answer = replacement.json()
        try:
            information_data = answer['answer']
            list_cities = information_data['items']
            for q in list_cities:
                found_city_name = q.get('title')
                if found_city_name == city_name:
                    found_city_id = q.get('id')
                    return int(found_city_id)
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    def city_user(self, user_id):
        """Получение информации о городе пользователя"""
        url = f'https://api.vk.com/method/users.get'
        options = {'access_token': user_token,
                  'fields': 'city',
                  'user_ids': user_id,
                  'v': '5.131'}
        replacement = requests.get(url, options=options)
        answer = replacement.json()
        try:
            information_data = answer['answer']
            for q in information_data:
                if 'city' in q:
                    city = q.get('city')
                    id = str(city.get('id'))
                    return id
                elif 'city' not in q:
                    self.write_message(user_id, 'Введите название вашего города: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.city_id(user_id, city_name)
                            if id_city != '' or id_city != None:
                                return str(id_city)
                            else:
                                break
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    def search_user(self, user_id):
        """Поиск подходящего человека"""
        url = f'https://api.vk.com/method/users.search'
        options = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.sex(user_id),
                  'age_from': self.lower_age(user_id),
                  'age_to': self.upper_age(user_id),
                  'city': self.city_user(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': '1' or '6',
                  'count': 500}
        replac = requests.get(url, options=options)
        replac_json = replac.json()
        try:
            dict_1 = replac_json['replacement']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск окончен'
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    def photos_id(self, user_id):
        """Получение id фото с распределением в обратном порядке """
        url = 'https://api.vk.com/method/photos.getAll'
        options = {'access_token': user_token,
                  'type': 'album',
                  'owner_id': user_id,
                  'extended': 1,
                  'count': 25,
                  'v': '5.131'}
        replac = requests.get(url, options=options)
        dict_photos = dict()
        replac_json = replac.json()
        try:
            dict_1 = replac_json['response']
            list_1 = dict_1['items']
            for q in list_1:
                photo_id = str(q.get('id'))
                q_likes = q.get('likes')
                if q_likes.get('count'):
                    likes = q_likes.get('count')
                    dict_photos[likes] = photo_id
            list_of_ids = sorted(dict_photos.items(), reverse=True)
            return list_of_ids
        except KeyError:
            self.write_message(user_id, 'Ошибка, связанная с токеном. Введите токен в переменную "user_token"')

    def photo_1_id(self, user_id):
        """Получение id первого фото"""
        date = self.photos_id(user_id)
        count = 0
        for q in date:
            count += 1
            if count == 1:
                return q[1]

    def photo_2_id(self, user_id):
        """Получение id второго фото"""
        date = self.photos_id(user_id)
        count = 0
        for q in date:
            count += 1
            if count == 2:
                return q[1]

    def photo_3_id(self, user_id):
        """Получение id третьего фото"""
        date = self.photos_id(user_id)
        count = 0
        for q in date:
            count += 1
            if count == 3:
                return q[1]

    def photo_1(self, user_id, message, offset):
        """Отправка первого фото"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.users_id(offset)}_{self.photo_1_id(self.users_id(offset))}',
                                         'random_id': 0})

    def photo_2(self, user_id, message, offset):
        """Отправка второго фото"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.users_id(offset)}_{self.photo_2_id(self.users_id(offset))}',
                                         'random_id': 0})

    def photo_3(self, user_id, message, offset):
        """Отправка третьего фото"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.users_id(offset)}_{self.photo_1_id(self.person_id(offset))}',
                                         'random_id': 0})

    def find_users(self, user_id, offset):
        self.write_message(user_id, self.found_user_info(offset))
        self.user_id(offset)
        seen_users(self.users_id(offset), offset) 
        self.photo_id(self.users_id(offset))
        self.photo_1(user_id, 'Первое фото', offset)
        if self.photo_2_id(self.users_id(offset)) != None:
            self.photo_2(user_id, 'Второе фото', offset)
            self.photo_3(user_id, 'Третье фото', offset)
        else:
            self.write_message(user_id, f'Больше фотографий нет')

    def found_user_info(self, offset):
        """Информация о найденном пользователе"""
        tuple_person = choose(offset)
        list_person = []
        for q in tuple_person:
            list_person.append(q)
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    def users_id(self, offset):
        """Информация о id найденого пользователя"""
        tuple_person = choose(offset)
        list_person = []
        for q in tuple_person:
            list_person.append(q)
        return str(list_person[2])


bot = SearchBot()