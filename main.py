import vk_config.Vk_Bot
import vk_config.vk_find_user
import Data_Base.DataBase
from vk_config.tokens import token_bot, token_vk
import re

vk_client = vk_config.vk_find_user.Vk_user(token_vk)
info_for_DataBase = {}  # Словарь с данными для внесения в базу данных
list_info_for_DataBase = []  # Список словарей с данными для записи в БД
dict_blacklist = {}  # Словарь с заблоированными пользователями
list_blacklist = []  # Список словарей с заблоированными пользователями

my_token = token_bot


def user_relation(msg):
    info_user_relation = {1: 'не женат/не замужем', 2: ' есть друг/есть подруга', 3: 'помолвлен/помолвлена',
                          4: 'женат/замужем', 5: 'всё сложно', 6: 'в активном поиске', 7: 'влюблён/влюблена',
                          8: 'в гражданском браке', 0: 'не указано'}
    return info_user_relation.get(msg)


def get_photo(result, owner_id):
    pare_id = result[0].get('id')
    first_name = result[0].get('first_name')
    last_name = result[0].get('last_name')
    bdate = result[0].get('bdate')
    city = result[0].get('city').get('title')
    relation = user_relation(result[0].get('relation'))

    pare = {'pare_id': pare_id, 'first_name': first_name, 'last_name': last_name, 'bdate': bdate,
            'city': city, 'relation': relation}

    # Если получили id подходящей пары с фото
    if vk_client.get_photos(pare_id):
        account = 'https://vk.com/id' + str(pare_id)
        dict_photo = vk_client.get_photos(pare_id)
        list_photo = vk_client.photo_pare(dict_photo)
        pare_info = {'url_account': account, 'url_photo1': list_photo[0].get('id_photo'),
                     'url_photo2': list_photo[1].get('id_photo'), 'url_photo3': list_photo[2].get('id_photo')}
        pare_info_all = {**pare, **pare_info}  # Объединили данные словарей
        info_for_DataBase['owner_id'] = owner_id
        info_for_DataBase['pare_info_all'] = pare_info_all
        temp = info_for_DataBase.copy()  # Создаем временный словарь для передачи словарей в список
        list_info_for_DataBase.append(temp)
        #  Заносим в словарь для записи в БД данные о пользователе и словарь с  данными пары
        return pare_info_all


def find_user(users, owner_params, owner_id):
    owner_params = owner_params
    owner_id = owner_id
    list_find = []
    users = users
    error_connect = False
    blacklist_dict = {}
    for i in users:
        any_info = vk_client.get_user(i)
        any_id = any_info[0].get('id')
        try:
            pare_id_for_user_id = Data_Base.DataBase.get_pare_id_for_user_id(owner_id, any_id)
            blacklist_user = Data_Base.DataBase.if_in_black_list(any_id)
            if (not pare_id_for_user_id) and (not blacklist_user):
                # Если текущей пары нет в списке данных пользователя и в списке заблокированных
                if not any_info[0].get('fail'):
                    #  Если текущая пара не заблокирована и ее нет в списке заблокированных
                    find_users = vk_client.select_users(any_info, owner_params)
                    #  Поиск пары по параметрам
                    if find_users:
                        list_find.append(find_users)
                    print('.', end='')
                else:
                    #  В нести в список пар с пометкой заблокированных
                    blacklist_dict['blacklist_user'] = any_info[0].get('id')
                    blacklist_dict['blacklist_info'] = any_info[0].get('fail')
                    black = blacklist_dict.copy()  # Копируем словарь с заблокированными и добавляем в список
                    list_blacklist.append(black)

        except Exception as Error:
            error_connect = True
            if not any_info[0].get('fail'):
                #  Если текущая пара не заблокирована
                find_users = vk_client.select_users(any_info, owner_params)
                #  Ищем пару по параметрам пользователя
                if find_users:
                    list_find.append(find_users)
                print('.', end='')

    if error_connect:
        print('База данных временно недоступна. find_user, pare_id_for_user_id')

    return list_find


def check_user_params(owner_id, owner_params):
    owner_params = owner_params
    owner_id = owner_id
    if not owner_params.get('city', None):  # Если не указан город
        vk_config.Vk_Bot.write_msg(owner_id, 'Укажите ваш город')
        city = vk_config.Vk_Bot.dialog()[1].title()
        owner_params['city'] = city

    if owner_params.get('sex') not in (1, 2):  # Если не указан пол
        message = """
        Укажите ваш пол
        женщина - 1
        мужчина - 2
        """
        vk_config.Vk_Bot.write_msg(owner_id, message)
        sex = vk_config.Vk_Bot.dialog()[1]
        owner_params[sex] = sex

    if owner_params.get('bdate', None) and re.findall(r"\d{1,2}.\d{1,2}.\d{4}", owner_params.get('bdate')):
        return owner_params
    else:
        # Если не указан год или неверный формат
        vk_config.Vk_Bot.write_msg(owner_id, 'Укажите ваш год рождения "дд.мм.гггг')
        bdate = vk_config.Vk_Bot.dialog()[1]
        owner_params['bdate'] = bdate


def send_message_to_user(res, owner_id, pare):
    result = res
    owner_id = owner_id
    pare = pare
    if pare:  # Если найдена пара с подходящими параметрами и фото
        vk_config.Vk_Bot.write_msg(owner_id, 'Аккаунт кандидата: ')
        vk_config.Vk_Bot.write_msg(owner_id,
                                   f"{result[0].get('first_name')} {result[0].get('last_name')} "
                                   f"{pare.get('url_account')}")
        vk_config.Vk_Bot.write_msg(owner_id, 'Фотография пары 1:',
                                   f"photo{pare.get('pare_id')}_{pare.get('url_photo1')}")
        vk_config.Vk_Bot.write_msg(owner_id, 'Фотография пары 2:',
                                   f"photo{pare.get('pare_id')}_{pare.get('url_photo2')}")
        vk_config.Vk_Bot.write_msg(owner_id, 'Фотография пары 3:',
                                   f"photo{pare.get('pare_id')}_{pare.get('url_photo3')}")
        vk_config.Vk_Bot.write_msg(owner_id, '*' * 40)

    else:
        vk_config.Vk_Bot.write_msg(owner_id, 'Людей по вашему запросу не найдено(((( ')


def main():
    # Диапазон id для сканирования сети
    users = (i for i in range(100_000_000, 100_000_200))
    user_message = vk_config.Vk_Bot.dialog()
    owner_id = user_message[0]
    owner_message = user_message[1]
    pare_list_clear = False
    ban_list_clear = False

    while owner_message != 'поиск пары':  # Ждем от пользователя фразы поиска
        bot_message = 'Для поиска пары, напишите "поиск пары"'
        vk_config.Vk_Bot.write_msg(owner_id, bot_message)
        user_message = vk_config.Vk_Bot.dialog()
        owner_id = user_message[0]
        owner_message = user_message[1]

    owner_info = vk_client.get_user(owner_id)  # Получили в списке словарь с необходимыми данными пользователя
    owner_params = vk_client.user_info(owner_info)  # Сформировали нужные данные
    owner_params = check_user_params(owner_id, owner_params)
    vk_config.Vk_Bot.write_msg(owner_id, 'Ищем подходящую пару по вашим параметрам')
    list_find = find_user(users, owner_params, owner_id)

    #  Ищем пару для данного пользователя
    if list_find:
        vk_config.Vk_Bot.write_msg(owner_id, 'Вот подходящие пары: ')
        for i in list_find:
            pare = get_photo(i, owner_id)
            send_message_to_user(i, owner_id, pare)

    # Если нашли пару - заносим в базу данных DataBase
    if list_info_for_DataBase:
        for i in list_info_for_DataBase:
            owner_id = i.get('owner_id')
            #  Проверяем на наличие текущего id пользователя в БД. Если нет - заносим
            try:
                user_in_list = Data_Base.DataBase.if_user_in_list(owner_id)
                if not user_in_list:
                    Data_Base.DataBase.insert_user(owner_id)
            except Exception as Error:
                print('База данных временно недоступна. owner_id не внесен в БД', {Error})

            try:
                Data_Base.DataBase.insert_pare(owner_id, i.get('pare_info_all'))  # Заносим в БД информацию о паре
                pare_list_clear = True
            except Exception as Error:
                print('База данных временно недоступна, возможны повторы', {Error})
                vk_config.Vk_Bot.write_msg(owner_id, 'База данных временно недоступна, возможны повторы.')
    else:
        print('Записей удовлетворяющих запросу не обнаруеженно.')
        vk_config.Vk_Bot.write_msg(owner_id, 'Записей удовлетворяющих запросу не обнаруеженно.')
    if list_blacklist:
        for i in list_blacklist:
            try:
                Data_Base.DataBase.insert_black_list(i.get('blacklist_user'), i.get('blacklist_info'))
                ban_list_clear = True
            except Exception as Error:
                print('База данных временно недоступна, невозможно внести данные о блокеровке пользователя', {Error})

    #  Если данные внесены в БД очищаем список для записи в БД
    if pare_list_clear:
        list_info_for_DataBase.clear()
        pare_list_clear = False
    if ban_list_clear:
        list_blacklist.clear()
        ban_list_clear = False


if __name__ == "__main__":
    main()
