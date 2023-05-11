from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import vk_api
from random import randrange
from pprint import pprint
from db import *

#Нужно указать токены
group_token = vk_api.VkApi(token="")
user_token = vk_api.VkApi(token="")


class Bot:
    def __init__(self):
        print('Bot was created')
        self.vk_user = vk_api.VkApi(
            token=user_token)
        self.vk_user_got_api = self.vk_user.get_api()
        self.vk_group = vk_api.VkApi(token=group_token) 
        self.vk_group_got_api = self.vk_group.get_api()
        self.longpoll = VkLongPoll(
            self.vk_group)

    def send_msg(self, user_id, message):
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=randrange(10 ** 7)
        )

    def name(self, user_id):
        user_info = self.vk_group_got_api.users.get(user_id=user_id)
        try:
            name = user_info[0]['first_name']
            return name

    def naming_of_years(self, years, till=True):
        if till is True:
            name_years = [1, 21, 31, 41, 51, 61, 71, 81, 91, 101]
            if years in name_years:
                return f'{years} года'
            else:
                return f'{years} лет'
        else:
            name_years = [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54, 62, 63, 64]
            if years == 1 or years == 21 or years == 31 or years == 41 or years == 51 or years == 61:
                return f'{years} год'
            elif years in name_years:
                return f'{years} года'
            else:
                return f'{years} лет'

    def input_looking_age(self, user_id, age):
        global age_from, age_to
        a = age.split("-")
        try:
            age_from = int(a[0])
            age_to = int(a[1])
            if age_from == age_to:
                self.msg(user_id, f' Ищу {self.naming_of_years(age_to, False)}')
                return
            self.msg(user_id, f' Ищу в пределах от {age_from} и до {self.naming_of_years(age_to, True)}')
            return
        except IndexError:
            age_to = int(age)
            self.msg(user_id, f' Ищу {self.naming_of_years(age_to, False)}')
            return
        except NameError:
            self.msg(user_id, f' Не правильный числовой формат!')
            return
        except ValueError:
            self.msg(user_id, f' Не правильный числовой формат!')
            return

    def get_years_of_person(self, bdate: str) -> object:
        bdate_splited = bdate.split(".")
        month = ""
        try:
            reverse_bdate = datetime.date(int(bdate_splited[2]), int(bdate_splited[1]), int(bdate_splited[0]))
            today = datetime.date.today()
            years = (today.year - reverse_bdate.year)
            if reverse_bdate.month >= today.month and reverse_bdate.day > today.day or reverse_bdate.month > today.month:
                years -= 1
            return self.naming_of_years(years, False)
        except IndexError:
            if bdate_splited[1] == "1":
                month = "января"
            elif bdate_splited[1] == "2":
                month = "февраля"
            elif bdate_splited[1] == "3":
                month = "марта"
            elif bdate_splited[1] == "4":
                month = "апреля"
            elif bdate_splited[1] == "5":
                month = "мая"
            elif bdate_splited[1] == "6":
                month = "июня"
            elif bdate_splited[1] == "7":
                month = "июля"
            elif bdate_splited[1] == "8":
                month = "августа"
            elif bdate_splited[1] == "9":
                month = "сентября"
            elif bdate_splited[1] == "10":
                month = "октября"
            elif bdate_splited[1] == "11":
                month = "ноября"
            elif bdate_splited[1] == "12":
                month = "декабря"
            return f'День рождения {int(bdate_splited[0])} {month}.'

    def get_age_of_user(self, user_id):
        """determine the user's age"""
        global age_from, age_to
        try:
            info = self.vk_user_got_api.users.get(
                user_ids=user_id,
                fields="bdate",
            )[0]['bdate']
            num_age = self.get_years_of_person(info).split()[0]
            age_from = num_age
            age_to = num_age
            if num_age == "День":
                print(f'Ваш {self.get_years_of_person(info)}')
                self.msg(user_id,
                              f'   Введите возраст, в формате : 20-25 (или 20).')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return self.input_looking_age(user_id, age)
            return print(f' Ищу {self.naming_of_years(age_to)}')
        except KeyError:
            print(f'День рождения скрыт!')
            self.msg(user_id,
                          f' Введите возраст, в формате : 20-25 (или 20).')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return self.input_looking_age(user_id, age)

    def get_city(self, user_id):
        global city_id, city_title
        self.msg(user_id,
                      f' Введите "Да" - поиск будет произведен в вашем городе.'
                      f' Или введите название города, например: Москва'
                      )
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "да" or answer == "y":
                    info = self.vk_user_got_api.users.get(
                        user_id=user_id,
                        fields="city"
                    )
                    city_id = info[0]['city']["id"]
                    city_title = info[0]['city']["title"]
                    return f' в городе {city_title}.'
                else:
                    cities = self.vk_user_got_api.database.getCities(
                        country_id=1,
                        q=answer.capitalize(),
                        need_all=1,
                        count=1000
                    )['items']
                    for i in cities:
                        if i["title"] == answer.capitalize():
                            city_id = i["id"]
                            city_title = answer.capitalize()
                            return f' в городе {city_title}'

    def gender(self, user_id):
        info = self.vk_user_got_api.users.get(
            user_id=user_id,
            fields="sex"
        )
        if info[0]['sex'] == 1:
            print(f'Ищу мужчину.')
            return 2
        elif info[0]['sex'] == 2:
            print(f'Ищу женщину.')
            return 1
        else:
            print("Ошибка")

    def get_persons(self, user_id):
        global list_found_persons
        list_found_persons = []
        res = self.vk_user_got_api.users.search(
            sort=0,
            city=city_id,
            hometown=city_title,
            sex=self.gender(user_id),
            status=1,
            age_from=age_from,
            age_to=age_to,
            has_photo=1,
            count=1000,
            fields="can_write_private_message, "  
                   "city, "
                   "domain, "
                   "home_town, "
        )
        number = 0
        for person in res["items"]:
            if not person["is_closed"]:
                if "city" in person and person["city"]["id"] == city_id and person["city"]["title"] == city_title:
                    number += 1
                    id_vk = person["id"]
                    list_found_persons.append(id_vk)
        print(f'Bot found {number} opened profiles for  {res["count"]}')
        return

    def photo_of_found_person(self, user_id):
        global attachments
        res = self.vk_user_got_api.photos.get(
            owner_id=user_id,
            album_id="profile",
            extended=1,
            count=30
        )
        dict_photos = dict()
        for i in res['items']:
            photo_id = str(i["id"])
            i_likes = i["likes"]
            if i_likes["count"]:
                likes = i_likes["count"]
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        attachments = []
        photo_ids = []
        for i in list_of_ids:
            photo_ids.append(i[1])
        try:
            attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
            return attachments
        except IndexError:
            try:
                attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
                return attachments
            except IndexError:
                return print(f'Нет фото')

    def get_found_person_id(self):
        global unique_person_id, found_persons
        seen_person = []
        for i in check(): 
            seen_person.append(int(i[0]))
        if not seen_person:
            try: 
                unique_person_id = list_found_persons[0]
                return unique_person_id
            except NameError:
                found_persons = 0
                return found_persons
        else:
            try:
                for ifp in list_found_persons:
                    if ifp in seen_person:
                        pass
                    else:
                        unique_person_id = ifp
                        return unique_person_id
            except NameError:
                found_persons = 0
                return found_persons

    def found_person_info(self, show_person_id):
        res = self.vk_user_got_api.users.get(
            user_ids=show_person_id,
            fields="about, " 
                   "activities, "
                   "bdate, "  
                   "status, "
                   "city, "
        )
        first_name = res[0]["first_name"]
        last_name = res[0]["last_name"]
        age = self.get_years_of_person(res[0]["bdate"])
        vk_link = 'vk.com/' + res[0]["domain"]
        city = ''
        try:
            if res[0]["city"]["title"] is not None:
                city = f'Город {res[0]["city"]["title"]}'
            else:
                city = f'Город {res[0]["home_town"]}'
        except KeyError:
            pass
        print(f'{first_name} {last_name}, {age}, {city}. {vk_link}')
        return f'{first_name} {last_name}, {age}, {city}. {vk_link}'

    def send_photo(self, user_id, message, attachments):
        try:
            self.vk_group_got_api.messages.send(
                user_id=user_id,
                message=message,
                random_id=randrange(10 ** 7),
                attachment=",".join(attachments)
            )
        except TypeError:
            pass

    def show_person(self, user_id):
        print(self.get_found_person_id())
        if self.get_found_person_id() == None:
            self.msg(user_id,
                          f'Анекты закончились. Если хотите начать сначала то: '
                          f'Измените критерии поиска. '
                          f'Введите возраст поиска, на пример от 21 года и до 35 лет, '
                          f'в формате : 21-35 (или 21 конкретный возраст 21 год).  ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    self.input_looking_age(user_id, age)
                    self.get_city(user_id)
                    self.get_persons(user_id)
                    self.show_person(user_id)
                    return
        else:
            self.msg(user_id, self.found_person_info(self.get_found_person_id()))
            self.send_photo(user_id, 'Фото с максимальными лайками',
                            self.photo_of_found_person(self.get_found_person_id()))
            insert_data_seen_person(self.get_found_person_id())


bot = Bot()