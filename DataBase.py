import psycopg2
from config_data_base import host, user, password, db_name


try:
    # подключаем базу данных
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE Client(
            id serial PRIMARY KEY,
            sex integer,
            city varchar(50),
            bdata integer,
            relation integer);"""
        )
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE Partner(
            id serial PRIMARY KEY,
            name varchar(50) NOT NULL,
            sex integer,
            city varchar(50),
            bdata integer,
            relation integer,
            id_photo integer references Photo(id),
            id_Blacklist integer references Blacklist(id));"""
        )
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE Photo(
            id serial PRIMARY KEY,
            url varchar(50) NOT NULL);"""
        )
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE Blacklist(
            id serial PRIMARY KEY);"""
        )

except Exception as ex:
    print("Ошибка работы с PostgreSQL", ex)
finally:
    if connection:
        connection.close()
        print('Соединение с базой данных закрыто')
