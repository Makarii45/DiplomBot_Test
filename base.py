import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    base=db_name
)

connection.autocommit = True


def users():
    """Создание таблицы найденных пользователей"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                first_name varchar(60) NOT NULL,
                last_name varchar(30) NOT NULL,
                vk_id varchar(40) NOT NULL PRIMARY KEY,
                vk_link varchar(60));"""
        )
    print ('[INFO] Table created.')


def seen_users():  
    """Cоздание таблицы просмотренных пользователей"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(60) PRIMARY KEY);"""
        )
    print('[INFO] Table created.')


def data_users(first_name, last_name, vk_id, vk_link):
    """Перемещение данных в таблицу user"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO users (first_name, last_name, vk_id, vk_link) 
            VALUES ('{first_name}', '{last_name}', '{vk_id}', '{vk_link}');"""
        )


def data_seen_users(vk_id, offset):
    """Перемещение данных в таблицу seen_user"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id) 
            VALUES ('{vk_id}')
            OFFSET '{offset}';"""
        )


def choose(offset):
    """Непросмотренные пользователи"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.first_name,
                        u.last_name,
                        u.vk_id,
                        u.vk_link,
                        su.vk_id
                        FROM users AS u
                        LEFT JOIN seen_users AS su 
                        ON u.vk_id = su.vk_id
                        WHERE su.vk_id IS NULL
                        OFFSET '{offset}';"""
        )
        return cursor.fetchone()


def drop_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ USERS КАСКАДОМ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS users CASCADE;"""
        )
        print('[INFO] Table deleted.')


def drop_seen_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ SEEN_USERS КАСКАДОМ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_users CASCADE;"""
        )
        print('[INFO] Table deleted.')


def creating_database():
    drop_users()
    drop_seen_users()
    users()
    seen_users()
