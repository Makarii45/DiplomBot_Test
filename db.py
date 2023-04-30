import psycopg2
from psycopg2 import errors


def create_tables(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            vk_id INTEGER NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS result_users(
            id SERIAL PRIMARY KEY,
            vk_id INTEGER NOT NULL UNIQUE,
            user_id INT REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            conn.commit()
            print('Таблицы успешно созданы.')
    except (psycopg2.errors.Error, Exception) as e:
        print(f'create_tables {e} {type(e)}')


def delete_tables(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            DROP TABLE IF EXISTS result_users CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            """)
            conn.commit()
            print('Таблицы успешно удалены.')
    except (psycopg2.errors.Error, Exception) as e:
        print(f'delete_tables {e} {type(e)}')


def insert_user(conn, user_info):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO users(vk_id) VALUES
            (%s) RETURNING id
            """, (user_info.get('id'),))
            user_db_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        return False
    except Exception as e:
        print(f'insert_user Exception {e} {type(e)}')
        return False
    return user_db_id or False


def insert_result_user(conn, user_db_id, finally_selected_user):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO result_users(vk_id, user_id) VALUES
            (%s, %s) RETURNING id
            """, (finally_selected_user.get('id'),
                  user_db_id,))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        return False
    except Exception as e:
        print(f'insert_result_user Exception {e} {type(e)}')
        return False


def get_user_db_id(conn, vk_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT id FROM users
            WHERE vk_id = %s
            """, (vk_id,))
            user_db_id = cursor.fetchone()
    except psycopg2.errors.Error as e:
        print(f'get_user_db_id {e} {type(e)}')
        return False
    except Exception as e:
        print(f'get_user_db_id {e} {type(e)}')
        return False
    return user_db_id[0] if user_db_id else False


def check_result_user(conn, user_id, user_db_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT vk_id FROM result_users
            WHERE vk_id = %s AND user_id = %s
            """, (user_id, user_db_id,))
            result_user_db_id = cursor.fetchone()
    except psycopg2.errors.Error as e:
        print(f'check_result_user {e} {type(e)}')
        return False
    except Exception as e:
        print(f'check_result_user {e} {type(e)}')
        return False
    return False if result_user_db_id else True