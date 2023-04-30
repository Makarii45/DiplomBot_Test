import psycopg2
from func import *
from db import *


def main():
    conn = psycopg2.connect(database="vkdb", user="postgres", password="123")
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower().strip()
            if request == "поехали":
                user_info = get_user_info(event.user_id)

                if user_info is not False:
                    if len(user_info) != 6 or len(user_info.get('bdate', '').split('.')) != 3:
                        write_msg(event.user_id, "Мало информации, пожалуйста, заполните остальное &#128373;")
                        user_info = get_additional_information(user_info)
                        if user_info is False:
                            continue
                    else:
                        user_age = bdate_to_age(user_info['bdate'])
                        if user_age < 18:
                            write_msg(event.user_id, "Сервис недоступен для пользователей моложе 18 лет! &#128286;")
                            continue
                        user_info['age'] = user_age
                        user_info.pop('bdate', None)

                    user_db_id = get_user_db_id(conn, user_info['id'])

                    if user_db_id is False:
                        user_db_id = insert_user(conn, user_info)

                    users_list = get_users_list(user_info)
                    if users_list is False:
                        continue

                    write_msg(event.user_id, "Поиск...ю")
                    last_user = users_list[-1]
                    status = True

                    for user in users_list:
                        if user == last_user and not check_result_user(conn, user.get('id'), user_db_id):
                            write_msg(event.user_id, "Больше никого нет.")
                        else:
                            check = check_result_user(conn, user.get('id'), user_db_id)
                            if check:
                                status = True
                                photos_info = get_photos(user)
                                if photos_info is not False and photos_info.get('count') >= 3:
                                    link_id_list = get_most_popular_photo(photos_info)
                                    write_msg(event.user_id, f"Найден  {user.get('first_name')} {user.get('last_name')}")
                                    for link_id in link_id_list:
                                        photo_link = get_photos(photos_info, link_id)
                                        write_msg(event.user_id, photo_link)
                                    insert_result_user(conn, user.get('id'), user_db_id, link_id_list)
                                    status = False
                                    break
                                else:
                                    photos_link = get_most_popular_photo(photos_info)
                                    write_msg(event.user_id, f"""Вам подходит {user.get('first_name')} """
                                                    f"""{user.get('last_name')} &#128150;\n"""
                                                    f"""Профиль: https://vk.com/id{user.get('id')}\n"""
                                                    f"""Популярные фоторафии:""", user, photos_link)

                                    insert_result_user(conn, user_db_id, user)

                                    write_msg(event.user_id, """Продолжаем? 
                                                            Чтобы продолжить, введите "дальше",
                                                            Чтобы закончить, введите "закончить". """)
                                    for event in long_poll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW:
                                            if event.to_me:
                                                request = event.text.lower().strip()
                                                if request == 'дальше':
                                                    write_msg(event.user_id, "Поиск...")
                                                    break
                                                elif request == 'закончить':
                                                    write_msg(event.user_id, "Заверщение")
                                                    status = False
                                                    break
                                                else:
                                                    write_msg(event.user_id, """Чтобы продолжить, введите \
                                                    "дальше",\nЧтобы закончить, введите "закончить" """)
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


if __name__ == '__main__':
    conn = psycopg2.connect(database="vkdb", user="postgres", password="123")
    delete_tables(conn)
    create_tables(conn)
    conn.close()

    main()