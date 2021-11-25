import sqlalchemy
import psycopg2
from Data_Base.config_data_base import host, user, password, db_name

DataBase = f'postgresql://{user}:{password}@{host}:5432/{db_name}'
engine = sqlalchemy.create_engine(DataBase)
#  Установливаем соединение с базой данных
try:
    connection = engine.connect()
except Exception as error:
    print('Ошибка при работе с PostgreSQL', {error})


def insert_user(user_id):
    return connection.execute(f"INSERT INTO vk_users (user_id) VALUES({user_id})")


def insert_pare(owner_id, pare_info):
    info = f"""INSERT INTO vk_pare (pare_id, first_name, last_name, bdate, city, relation, url_account, url_photo1, 
    url_photo2, url_photo3, black_list) VALUES({pare_info.get('pare_id')}, '{pare_info.get('first_name')}', 
    '{pare_info.get('last_name')}', 
    '{pare_info.get('bdate')}','{pare_info.get('city')}', '{pare_info.get('relation')}',
    '{pare_info.get('url_account')}', '{pare_info.get('url_photo1')}', 
    '{pare_info.get('url_photo2')}', '{pare_info.get('url_photo3')}', '{pare_info.get('black_list')}');"""
    connection.execute(info)
    id_user = connection.execute(f"""SELECT id from vk_users WHERE user_id = {owner_id}""").fetchone()
    id_pare = connection.execute(
        f"""SELECT id from vk_pare WHERE pare_id = {pare_info.get('pare_id')}""").fetchone()
    insert_vk_users_vk_pare(*id_user, *id_pare)


def insert_black_list(any_id, black_list):
    return connection.execute(f"""INSERT INTO vk_pare (pare_id, black_list) VALUES({any_id}, '{black_list}')""")


def insert_vk_users_vk_pare(id_user, id_pare):
    return connection.execute(
        f"""INSERT INTO vk_users_vk_pare (id_user, id_pare) VALUES({id_user}, {id_pare})""")


def bd(table_name, column):
    return connection.execute(f"SELECT {column} FROM {table_name}").fetchall()


def get_pare_id_for_user_id(user_id, pare_id):
    user_pare_id = connection.execute(f"""SELECT pare_id FROM vk_pare
    JOIN vk_users_vk_pare ON vk_pare.id=vk_users_vk_pare.id_pare
    JOIN vk_users ON vk_users_vk_pare.id_user = vk_users.id
    WHERE (vk_users.user_id = {user_id}) AND (vk_pare.pare_id = {pare_id})""").fetchall()
    return user_pare_id


def if_user_in_list(user_id):
    return connection.execute(f"""SELECT user_id FROM vk_users WHERE user_id = {user_id}""").fetchall()


def if_in_black_list(pare_id):
    return connection.execute(f""" SELECT black_list FROM vk_pare WHERE pare_id = {pare_id} """).fetchone()

