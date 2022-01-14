import vk_api
import requests
import database_code as db
from creds import TOKEN, BOT_TOKEN
import webbrowser
from datetime import datetime
from vk_api.longpoll import VkLongPoll


class VkAPIClass:
    """
    Основной класс для работы с API ВКонтакте.
    Ниже инициализируется бот, хранятся системные переменные для функций
    """
    main_url = 'https://api.vk.com/method/'
    bot = vk_api.VkApi(token=BOT_TOKEN)
    bot_longpoll = VkLongPoll(bot)
    # ниже - системные переменные для работы
    token_expired = False
    current_user_id = None
    sex = None
    # список для красивого вывода пола
    sex_tags = [
        'пол не указан',
        'Женский',
        'Мужской'
    ]
    sex_tag = None
    relation = None
    # список для красивого вывода статуса СП
    relation_tags = [
        'не указано',
        'не женат/не замужем',
        'есть друг/есть подруга',
        'помолвлен/помолвлена',
        'женат/замужем',
        'всё сложно',
        'в активном поиске',
        'влюблён/влюблена',
        'в гражданском браке'
    ]
    relation_tag = None
    city_id = None
    city_title = None
    bdate = None
    is_profile_picked = False

    def _if_active(self, vk_id: int) -> bool:
        """
        Приватная функция для проверки активности профиля. Возвращает True, если активен.
        :param vk_id: ID ВКонтакте
        """
        url = self.main_url + 'users.get/'
        params = {
            'user_ids': vk_id,
            'access_token': TOKEN,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params).json()['response'][0]
        if 'deactivated' not in response:
            return True
        else:
            return False

    def fav_user(self, vk_id: int):
        """
        Функция для добавления пользователя в избранный список. Передает данные в модуль с БД для дальнейших действий.
        :param vk_id: ID ВКонтакте
        """
        try:
            vk_id = int(vk_id)
        except ValueError:
            self.send_message('Неверная ссылка на пользователя!')
            return
        if self._if_active(vk_id):
            if db.check_favored(vk_id):
                self.send_message('Пользователь уже в избранном!')
            else:
                if db.check_user_and_photos(vk_id):
                    db.favorite_user(vk_id)
                    self.send_message(f'Пользователь vk.com/id{vk_id} добавлен в избранное')
                else:
                    self.send_message('Такого пользователя нет в результатах поиска, добавить в избранное можно тех '
                                      'пользователей, которые уже были в истории поиска')
        else:
            self.send_message('Пользователь неактивен, проверьте ссылку')

    def block_user(self, vk_id: int):
        """
        Функция для добавления пользователя в черный список. Передает данные в модуль с БД для дальнейших действий.
        :param vk_id: ID ВКонтакте
        """
        try:
            vk_id = int(vk_id)
        except ValueError:
            self.send_message('Неверная ссылка на пользователя!')
            return
        if self._if_active(vk_id):
            if db.check_blacklist(vk_id):
                self.send_message('Пользователь уже заблокирован!')
            else:
                db.block_user(vk_id)
                self.send_message(f'Пользователь vk.com/id{vk_id} заблокирован')
        else:
            self.send_message('Пользователь неактивен, проверьте ссылку')

    def db_get_users(self, user_amount: int):
        """
        Функция для вывода N пользователей из пользователей в БД. Передает данные в модуль с БД для дальнейших действий.
        :param user_amount: количество записей, которые нужно вывести.
        """
        try:
            user_amount = int(user_amount)
        except ValueError:
            self.send_message('Неверный синтаксис команды, '
                              'используйте только положительные целые числа.\nПример: !getusers 10')
            return
        if user_amount < 0:
            self.send_message('Неверно введено количество, используйте только положительные целые числа.')
            return
        counter = 0
        db_length = db.get_len_users()
        if db_length == 0:
            self.send_message('БД пуста.')
        else:
            if user_amount > db_length:
                user_amount = db_length
                self.send_message('Указанное число пользователей больше количества записей в БД,'
                                  ' вывожу все существующие записи.')
            users = db.get_all_users()
            self.send_message('Пользователи в базе данных:')
            for user in users:
                if counter > user_amount - 1:
                    break
                user_id = user[0]
                user_photos = user[1]
                self.send_attachments(f'vk.com/id{user_id}', user_photos)
                counter += 1

    def db_get_blocked_users(self):
        """
        Функция для вывода всех ID пользователей в черном списке.
        """
        users = db.get_blocked_users()
        if db.get_len_blacklist() == 0:
            self.send_message('Черный список пуст')
        else:
            self.send_message('Пользователи в черном списке:')
            for user in users:
                self.send_message(f'vk.com/id{user}')

    def db_get_favored_users(self):
        """
        Функция для вывода всех ID пользователей в избранном списке.
        """
        users = db.get_favored_users()
        if db.get_len_favored() == 0:
            self.send_message('Список избранных пуст')
        else:
            self.send_message('Пользователи в избранном:')
            for user in users:
                user_id = user[0]
                user_photos = user[1]
                self.send_attachments(f'vk.com/id{user_id}', user_photos)

    def clear_database_all(self):
        """
        Функция для очистки всей БД.
        """
        db.drop_all()
        self.send_message('БД очищена полностью.')

    def clear_users(self):
        """
        Функция для очистки таблицы пользователей БД.
        :return:
        """
        db.drop_users()
        self.send_message('Список пользователей очищен.')

    def clear_blocked_users(self):
        """
        Функция для очистки таблицы черного списка.
        """
        db.drop_blacklist()
        self.send_message('Черный список очищен.')

    def clear_favored_users(self):
        """
        Функция для очистки таблицы избранных пользователей.
        """
        db.drop_favored()
        self.send_message('Список избранных очищен.')

    def check_token(self):
        """
        Функция, которая проверяет валидность токена.
        Валидность проверяется путем простого запроса к API и анализа ответа от сервера. Если токен протух - системная
        переменная token_expired переключается на True

        :return:
        """
        url = self.main_url + 'photos.get/'
        params = {
            'owner_id': 1,
            'album_id': 'profile',
            'access_token': TOKEN,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params).json()
        if 'error' in response:
            print('Token expired!')
            self.token_expired = True
        else:
            print('Token OK')

    def set_city(self, city_name: str):
        """
        Функция для изменения параметра города для поиска. Принимает строку с названием или частью названия города и
        через метод database.getCities находит город по названию. Метод ищет по похожим названиям, иногда выдача не
        понимает до конца, что имелось в виду и выдает ближайший похожий город или федеральную единицу. Поиск городов
        только по РФ.
        :param city_name: строка с названием города.
        """
        url = self.main_url + 'database.getCities/'
        params = {
            'country_id': 1,
            'q': city_name,
            'count': 1,
            'access_token': TOKEN,
            'v': '5.131'
        }
        res = requests.get(url=url, params=params).json()['response']['items'][0]
        self.city_id = res['id']
        self.city_title = res['title']
        self.send_message(f'Установлен город: {self.city_title}')

    def set_relation(self, status: str):
        """
        Функция для изменения параметра СП для поиска. Берет данные из relation_tags для отображения.
        :param status: число, отображающее статус СП.
        """
        try:
            self.relation = int(status)
        except ValueError:
            self.send_message('Неверный формат семейного положения,'
                              ' используйте только цифры\nПример: !relation 2')
            return
        self.relation_tag = self.relation_tags[self.relation]
        if 0 <= self.relation <= 8:
            self.send_message(f'Установлено СП: {self.relation_tag}')
        else:
            self.send_message('Неверно указан параметр СП\nПример: !relation <0-8>')

    def set_birthday(self, bdate: str):
        """
        Функция для изменения параметра даты рождения. Принимает полную дату в формате ДД.ММ.ГГГГ или неполную в формате
        ДД.ММ. Для более красивого вывода даты используется переменная formatted_date, сама дата хранится в виде списка.
        :param bdate: строка с датой
        """
        bdate = bdate.strip()
        date = bdate.split('.')
        if len(date) == 2:
            try:
                datetime.strptime(bdate, '%d.%m')
            except ValueError:
                self.send_message('Неверный формат даты\nПример: 01.01')
                return
        elif len(date) == 3:
            try:
                datetime.strptime(bdate, "%d.%m.%Y")
            except ValueError:
                self.send_message('Неверный формат даты\nПример: 01.01.2000')
                return
        else:
            self.send_message('Неверный формат команды.\n Формат: ДД.ММ.ГГГГ или ДД.ММ')
            return
        self.bdate = bdate.split('.')
        formatted_date = '.'.join(self.bdate)
        self.send_message(f'Установлена дата рождения: {formatted_date}')

    def set_sex(self, sex: str):
        """
        Функция для изменения параметра пола для поиска. По умолчанию всегда выставляется противоположный пол.
        :param sex: число, отображающее пол.
        """
        try:
            self.sex = int(sex)
        except ValueError:
            self.send_message('Неверный формат пола, используйте только цифры от 0 до 2')
        if 0 <= self.sex <= 2:
            self.sex_tag = self.sex_tags[self.sex]
            self.send_message(f'Установлен пол: {self.sex_tag}')
        else:
            self.send_message('Неверно введен пол, используйте только цифры от 0 до 2')

    def get_access_token(self, app_id: int):
        """
        Функция для более простого получения токена пользователя. Принимает на вход ID приложения ВКонтакте,
        конструирует ссылку для получения токена и открывает новое окно для подтверждения авторизации, откуда можно
        будет скопировать обновленный токен. Токен будет иметь разрешения: wall, photos, status, groups
        :param app_id: ID приложения ВК
        """
        url = 'https://oauth.vk.com/authorize'
        params = {
            'client_id': app_id,
            'display': 'page',
            'scope': 'wall,photos,status,groups',
            'response_type': 'token',
            'v': '5.131'
        }
        res = requests.get(url=url, params=params)
        webbrowser.open(res.url, new=2)

    def like_user(self, vk_id, photo_number):
        """
        Функция для выставления лайка фотографии пользователя. Функция обращается к БД, проверяет наличие ID в БД,
        получает фотографии пользователя и через API ставит лайк на фотографию от имени держателя токена.
        :param vk_id: ID пользователя ВК
        :param photo_number: номер фотографии пользователя.
        """
        url = self.main_url + 'likes.add/'
        try:
            photo_number = int(photo_number)
        except ValueError:
            self.send_message('Неверный синтаксис команды, '
                              'используйте только положительные целые числа.')
            return
        if photo_number < 1 or photo_number > 3:
            self.send_message('Неверно введено количество, введите число от 1 до 3.')
            return
        try:
            vk_id = int(vk_id)
        except ValueError:
            self.send_message('Неверный вид ссылки\nПример: vk.com/id1')
            return
        database_info = db.get_user_for_likes(vk_id)
        if database_info:
            photos = database_info[1].split(',')
            if photo_number <= len(photos):
                params = {
                    'owner_id': vk_id,
                    'type': 'photo',
                    'access_token': TOKEN,
                    'v': '5.131'
                }
                photo = photos[photo_number - 1]
                photo_id = photo.split('_')[-1]
                params.setdefault('item_id', photo_id)
                requests.get(url=url, params=params)
                self.send_message('Фотография лайкнута! :)')
            else:
                self.send_message(f'Неверно введен номер фотографии, у пользователя всего {len(photos)}')
                return
        else:
            self.send_message('Пользователя нет в БД!')
            return

    def search_users(self, amount: int):
        """
        Функция для поиска пользователей ВК по заданным параметрам дня рождения, статуса СП, города проживания и пола.
        Функция проверяет, есть пользователь в БД или в черном списке или приватность профиля, если нет - с помощью бота
        отправляет ссылку на пользователя вместе с тремя самыми популярными фотографиями пользователя. Также заносит ID
        пользователя и ссылки на фото в БД.
        :param amount: количество пользователей на выдачу ботом.
        """
        counter = 0
        url = self.main_url + 'users.search/'
        params = {
            'count': 1000,
            'has_photo': 1,
            'access_token': TOKEN,
            'v': '5.131'
        }
        # ниже добавляем параметры в словарь с параметрами, если они выставлены
        if self.sex and self.sex != 0:
            params.setdefault('sex', self.sex)
        if self.relation and self.relation != 0:
            params.setdefault('status', self.relation)
        if self.city_id:
            params.setdefault('city', self.city_id)
        if self.bdate:
            if len(self.bdate) == 2:
                params.setdefault('birth_day', self.bdate[0])
                params.setdefault('birth_month', self.bdate[1])
            elif len(self.bdate) == 3:
                params.setdefault('birth_day', self.bdate[0])
                params.setdefault('birth_month', self.bdate[1])
                params.setdefault('birth_year', self.bdate[2])
        response = requests.get(url, params=params).json()['response']['items']
        for person in response:
            if counter > amount - 1:
                break
            if person['is_closed']:
                continue
            if db.check_blacklist(person['id']) or db.check_user_and_photos(person['id']):
                continue
            else:
                person_id = person['id']
                top_photos = self.get_photos(person_id)
                attachment = ','.join(top_photos)
                db.add_user(person_id, attachment)
                self.send_attachments(f'vk.com/id{person_id}', attachment)
                counter += 1

    def get_photos(self, user_id: int):
        """
        Функция для получения идентификаторов аватарок пользователя. Функция делает запрос на выдачу ID фото, количество
        лайков, количество комментариев. Популярность фотографий рассчитывается из суммы лайков и комментариев на фото.
        :param user_id: ID пользователя ВК.
        """
        url = self.main_url + 'photos.get/'
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'count': 100,
            'extended': 1,
            'photo_sizes': 1,
            'access_token': TOKEN,
            'v': '5.131'
        }
        photo_list = []
        res = requests.get(url=url, params=params).json()
        for photo in res['response']['items']:
            likes = photo['likes']['count']
            comments = photo['comments']['count']
            photo_url = f'photo{photo["owner_id"]}_{photo["id"]}'
            metadata = (likes + comments, photo_url)
            photo_list.append(metadata)
        # выбираем самые популярные
        photo_list = sorted(photo_list, key=lambda x: x[0], reverse=True)
        # берем первые три фотографии
        photo_list = photo_list[:3]
        # возвращаем только ID фото
        top_photos = [photo[-1] for photo in photo_list]
        return top_photos

    def get_user_info(self, user_id: str):
        """
        Функция для получения параметров поиска. Функция анализирует пол, дату рождения, город проживания и статус СП.
        При получении данных, выводит установленные параметры через бота.
        :param user_id: ID пользователя ВК
        """
        url = self.main_url + 'users.get/'
        params = {
            'user_ids': user_id,
            'fields': 'sex, bdate, city, relation',
            'access_token': TOKEN,
            'v': '5.131'
        }
        try:
            res = requests.get(url, params=params).json()['response']
        except KeyError:
            self.send_message('Невалидная ссылка на пользователя')
            return
        # выставление противоположного пола
        sex = res[0].get('sex')
        if sex == 1:
            self.sex = 2
            self.sex_tag = self.sex_tags[self.sex]
        else:
            self.sex = 1
            self.sex_tag = self.sex_tags[self.sex]
        self.relation = res[0].get('relation')
        # выставление статуса СП
        try:
            self.relation_tag = self.relation_tags[self.relation]
        except TypeError:
            self.relation_tag = None
        # выставление города проживания
        try:
            self.city_id = res[0].get('city')['id']
            self.city_title = res[0].get('city')['title']
        except TypeError:
            self.city_id = None
            self.city_title = None
        # выставление даты рождения
        try:
            self.bdate = res[0].get('bdate').split('.')
        except AttributeError:
            self.bdate = None

        if self.relation is None:
            self.send_message('Не найден статус семейного положения, '
                              'введите !relation <1-8> для расширения условий поиска')
        if self.city_id is None:
            self.send_message('Не найден город проживания, '
                              'введите !city <название> для расширения условий поиска')
        if self.bdate is None:
            self.send_message('Не найден возраст, '
                              'введите !birthday <ДД.ММ.ГГГГ> для расширения условий поиска')
        if self.bdate:
            formatted_date = '.'.join(self.bdate)
        else:
            formatted_date = None
        self.send_message('Входные параметры:\n'
                          f'Дата рождения: {formatted_date}\n'
                          f'Пол: {self.sex_tag} \n'
                          f'Город: {self.city_title}\n'
                          f'Семейное положение: {self.relation_tag}'
                          f'\n\nДля запуска поиска введите !search <количество пользователей>'
                          '.\nДля повторного просмотра параметров введите !params')

    def send_attachments(self, text, attachments):
        """
        Функция для отправки сообщения через бота.
        """
        self.bot.method('messages.send', {'user_id': self.current_user_id, 'message': text,
                                          'attachment': attachments, 'random_id': 0})

    def send_message(self, text):
        """
        Функция для отправки сообщения с приложенными фотографиями через бота.
        :param text:
        :return:
        """
        self.bot.method('messages.send', {'user_id': self.current_user_id, 'message': text, 'random_id': 0})
