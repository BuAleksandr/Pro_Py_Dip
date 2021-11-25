import requests
from vk_config.tokens import token_vk, token_bot


class Vk_user:
    url = 'https://api.vk.com/method/'
    token = token_vk

    def __init__(self, token):
        self.params = {
            'access_token': token,
            'v': '5.131'
        }

    def b_data(self, date):
        self.date = date
        if self.date and ('.' not in self.date[-4:]):
            return int(self.date[-4:])

    def swap_sex(self, sex):
        self.sex = sex
        out = {1: 2, 2: 1, 0: 0}
        return out.get(self.sex)

    def get_user(self, user_ids):
        user_url = self.url + 'users.get'
        self.user_ids = user_ids
        self.user_params = {
            'user_ids': user_ids,
            'fields': 'bdate, sex, city, relation'
        }

        try:
            res = requests.get(user_url, params={**self.params, **self.user_params}).json()
        except Exception as error:
            return f'Ошибка ввода. {error}'
        if 'error' in res:
            print('Неверный логин')
        return res.get('response')

    def user_info(self, response):
        self.resp = response
        self.city = ''
        self.name = self.resp[0].get('first_name')
        self.last_name = self.resp[0].get('last_name')
        self.bdate = self.resp[0].get('bdate')
        if self.resp[0].get('city'):
            self.city = self.resp[0].get('city').get('title')
        else:
            self.city = None
        self.relation = self.resp[0].get('relation', None)
        self.sex = self.resp[0].get('sex')

        if self.resp[0].get('fail'):
            self.fail = self.resp[0].get('fail')
        else:
            self.fail = None

        self.find_info = {'bdate': self.bdate, 'sex': self.sex, 'city': self.city, 'relation': self.relation,
                          'deactivated': self.fail}
        return self.find_info

    def select_users(self, any_info: list, find_params: list):
        self.any_info = any_info
        self.find_params = find_params

        if not self.any_info[0].get('fail'):
            self.age_any = self.b_data(self.any_info[0].get('bdate'))
            self.age_find = self.b_data(self.find_params.get('bdate'))
            self.sex_find = self.swap_sex(self.find_params.get('sex'))
            if self.age_any:
                self.age_user = range(self.age_find - 5, self.age_find)
                self.city = self.any_info[0].get('city', None)
                if self.city:
                    self.city = self.city.get('title')
                    if ((int(self.age_any) in self.age_user)
                            and (self.any_info[0].get('sex') == self.sex_find)
                            and (self.city == self.find_params.get('city'))
                            and (self.any_info[0].get('relation') in (1, 6, 0))):
                        return self.any_info
        else:
            return self.any_info[0].get('id'), self.any_info[0].get('fail')

    def get_photos(self, user_id):
        self.photo_url = self.url + 'photos.get'
        self.user_id = user_id
        self.photo_params = {
            'access_token': token_bot,
            'owner_id': user_id,
            'count': 50,
            'album_id': 'profile',
            'photo_size': 1,
            'extended': 1
        }
        req = requests.get(self.photo_url, params={**self.params, **self.photo_params}).json()
        if req.get('response').get('count') > 0:
            return req

    def photo_pare(self, req):
        try:
            photos_all_list = req.get('response').get('items')
        except Exception as error:
            return f'Ошибка ввода токена VK и id. {error}'

        all_photo = []
        likes_photo = []

        for i in photos_all_list:
            likes = i.get('likes').get('count')
            comments = i.get('comments').get('count')
            likes_com = likes + comments
            likes_photo.append(likes_com)
        likes_photo.sort()
        likes_com_list = likes_photo[-3:][::-1]

        for i in photos_all_list:
            photo_info = {}
            id_photo = i.get('id')
            likes = i.get('likes').get('count')
            comments = i.get('comments').get('count')
            likes_comments = likes + comments
            likes_com_list.append(likes_comments)

            if likes_comments >= likes_com_list[2]:
                photo_info['likes_com'] = likes_comments
                photo_info['id_photo'] = id_photo
                all_photo.append(photo_info)
        while len(all_photo) > 3:
            del all_photo[0]
        return all_photo
