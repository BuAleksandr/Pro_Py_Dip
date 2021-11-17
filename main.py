from pprint import pprint
from random import randrange

import requests
import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType


class VK_User:
    # Сбор информации от пользователя
    url = 'https://api.vk.com/method/'

    def __init__(self, token):
        self.params = {
            'access_token': token,
            'v': '5.131'
        }

    def write_msg(self, message):
        vk.method('messages.send', {'user_id': self, 'message': message, 'random_id': randrange(10 ** 7)})

    def info_user(self, owner_id, sorting=0):
        search_url = self.url + 'users.get'
        search_params = {
            'user_ids': owner_id,
            'fields': 'sex, city, relation, bdate'
        }
        req = requests.get(search_url, params={**self.params, **search_params}).json()
        result = req['response'][0]
        if 'sex' in result:
            user_sex = result['sex']
        else:
            user_sex = input('Введите Ваш пол(1-женщина, 2-мужчина): ')

        if 'id' in result['city']:
            user_city = result['city']['id']
        else:
            user_city_name = input('Введите название вашего город : ')
            city_url = self.url + 'database.getCities'
            city_params = {
                'q': user_city_name,
                'count': 100
            }
            res_city = requests.get(city_url, params={**self.params, **city_params}).json()
            user_city = res_city['items'][0]['id']
            return user_city

        if 'bdate' in result:
            user_bdate = result['bdate']
            user_bdate = str(user_bdate)
            bdate = user_bdate[-4:]
            bdate = int(bdate)
        else:
            bdate = input('Введите вашу дату рождения(день,месяц,год): ').replace(",", ".")

        if 'relation' in result:
            user_relation = result['relation']
        else:
            user_relation = input('Введите ваше семейное положение(1-не женат/не замужем; 2 — есть друг/есть подруга;/n'
                                  ' 3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; /n'
                                  '6 — в активном поиске; 7 — влюблён/влюблена; 8 — в гражданском браке): ')
            if user_relation == '1' or '6':
                pass
            else:
                print('Извините для Вас поиск невозможен')

        # Сбор допольнительной информации для поиска второго пользователя
        user_info = {'sex': user_sex, 'city': user_city, 'bdate': bdate, 'relation': user_relation}

        if user_info['relation'] == '1' or '6':
            status = user_info['relation']
        else:
            print('Извините для Вас поиск невозможен')
        if user_info['sex'] == 1:
            sex = 2
        else:
            sex = 1

        age_from = input('Введите минимальный возраст поиска: ')
        age_to = input('Введите максимальный возраст поиска: ')
        offset = 0
        count = 1000
        users_ids = []
        while True:
            rs = api.users.search(city=user_city, age_from=age_from, age_to=age_to, sex=sex, offset=offset,
                                  status=status, count=count)
            if not rs['count'] or not rs['items']:
                break
            users_ids += [user['id'] for user in rs['items']]
            if len(users_ids) > 1:
                break
        # print(f'Найдены люди с ID: {users_ids}')

    def search_photo(self, users_ids, sorting=0):
        photos_search_url = self.url + 'photos.get'
        photos_search_params = {
            'count': 50,
            'owner_id': users_ids,
            'extended': 1,
            'album_id': 'profile'
        }
        req = requests.get(photos_search_url, params={**self.params, **photos_search_params}).json()
        req = req['response']['items']
        photo_count = len(req)

        photo_dict = {}
        i = 0
        while i < photo_count:
            likes = req[i]['likes']['count']
            comments = req[i]['comments']['count']
            photo_dict[req[i]['sizes'][-1]['url']] = int(likes) + int(comments)
            i += 1
        photo_dict = sorted(photo_dict.items(), key=lambda x: x[1])
        if len(photo_dict) > 3:
            photo_dict = photo_dict[-3:]
        return photo_dict


if __name__ == "__main__":
    token_bot = input(f'Введите ваш токен для чат бота: ')
    vk = vk_api.VkApi(token=token_bot)
    Poll = VkLongPoll(vk)
    token_vk = input(f'Введите ваш токен для работы с VK: ')
    vk_reg = vk_api.VkApi(token=token_vk)
    api = vk_reg.get_api()
    vk_client = VK_User(token_vk)


    def search_pare_photo(users_ids):
        url_pare = 'https://vk.com/id' + str(users_ids)
        photo_dict = vk_client.search_photo(users_ids)
        # pprint(photo_dict)
        list_pare_user = [url_pare]
        for photos in photo_dict:
            list_pare_user.append(photos[0])
        # print(list_pare_user)
        return list_pare_user

    # Чат-бот
    def bot():
        for event in Poll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    user_id = event.user_id
                    if request == "привет":
                        VK_User.write_msg(user_id, f"Привет меня зовут VKinder я помогу Вам найти вторую половинку!"
                                                   f"Для начала необходимо проверить ваши данные, чтобы начать поиск."
                                                   f"Если Вы солласны напишите 'ОК'")
                    elif request == "пока":
                        VK_User.write_msg(user_id, "До свидания и хорошего Вам настроения (^_^)")

                    elif request == 'ок':
                        text = search_pare_photo(VK_User.info_user)
                        for i in text:
                            pare_list = str(i)
                            VK_User.write_msg(user_id, pare_list)
                    else:
                        VK_User.write_msg(user_id, 'Я вас не понимаю, напишите "привет" для начала работы')
    bot()
