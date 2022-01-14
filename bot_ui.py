import creds
from vkinder_code import VkAPIClass
from creds import APP_ID
from vk_api.longpoll import VkEventType


def start_bot():
    vk = VkAPIClass()
    # проверка на заполнение данных
    if creds.TOKEN == '' or creds.BOT_TOKEN == '' or creds.APP_ID == '' or creds.DB == '':
        print('Enter credentials in creds.py')
    else:
        # проверяем, не протух ли токен
        vk.check_token()
        # запуск UI бота
        for event in vk.bot_longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                vk.current_user_id = event.user_id
                if event.to_me:
                    query = event.text.lower()
                    if query.find('!refreshtoken') != -1:
                        vk.get_access_token(int(APP_ID))
                        vk.send_message('Скопируйте новый токен в creds.py :)')

                    elif vk.token_expired:
                        vk.send_message('Пользовательский токен невалиден! Воспользуйтесь командой !refreshtoken')

                    elif query.find('!start') != -1:
                        if query == '!start':
                            vk.get_user_info(event.user_id)
                            vk.is_profile_picked = True
                        elif query.find('vk.com') != -1:
                            target_id = query.split('vk.com/')[-1]
                            vk.get_user_info(target_id)
                            vk.is_profile_picked = True
                        else:
                            vk.send_message('Неверный формат ссылки!\nПример: !start vk.com/id1')

                    elif query.find('!block') != -1:
                        if query.find('vk.com/id') != -1:
                            target_id = query.split('!block vk.com/id')[-1]
                            vk.block_user(target_id)
                        else:
                            vk.send_message('Неверный формат ссылки!\nПример: !block vk.com/id1')

                    elif query.find('!fav') != -1:
                        if query.find('vk.com/id') != -1:
                            target_id = query.split('!fav vk.com/id')[-1]
                            vk.fav_user(target_id)
                        else:
                            vk.send_message('Неверный формат ссылки!\nПример: !fav vk.com/id1')

                    elif query.find('!like') != -1:
                        sub_query = query.split('!fav')[-1]
                        if sub_query.find('vk.com/id') != -1:
                            user_id = sub_query.split(' vk.com/id')[-1].split(' ')[0]
                            photo_num = sub_query.split(' vk.com/id')[-1].split(' ')[-1]
                            vk.like_user(user_id, photo_num)
                        else:
                            vk.send_message('Неверный формат ссылки!\nПример: vk.com/id1')

                    elif query.find('!getusers') != -1:
                        amount = query.split('!getusers ')[-1]
                        vk.db_get_users(amount)

                    elif query.find('!getblocked') != -1:
                        vk.db_get_blocked_users()

                    elif query.find('!getfav') != -1:
                        vk.db_get_favored_users()

                    elif query.find('!clearall') != -1:
                        vk.clear_database_all()

                    elif query.find('!clearusers') != -1:
                        vk.clear_users()

                    elif query.find('!clearblocked') != -1:
                        vk.clear_blocked_users()

                    elif query.find('!clearfav') != -1:
                        vk.clear_favored_users()

                    elif query.find('!params') != -1:
                        if vk.bdate:
                            formatted_date = '.'.join(vk.bdate)
                        else:
                            formatted_date = None
                        vk.send_message(f'Установлены следующие параметры поиска:\n'
                                        f'Дата рождения: {formatted_date}\n'
                                        f'Пол: {vk.sex_tag} \n'
                                        f'Город: {vk.city_title}\n'
                                        f'Семейное положение: {vk.relation_tag}'
                                        f'\n\nДля запуска поиска введите !search <количество пользователей>')

                    elif query.find('!sex') != -1:
                        if vk.is_profile_picked:
                            vk.set_sex(query.split('!sex')[-1])
                        else:
                            vk.send_message('Не выбран профиль для поиска!')

                    elif query.find('!birthday') != -1:
                        if vk.is_profile_picked:
                            vk.set_birthday(query.split('!birthday')[-1])
                        else:
                            vk.send_message('Не выбран профиль для поиска!')

                    elif query.find('!city') != -1:
                        if vk.is_profile_picked:
                            vk.set_city(query.split('!city')[-1])
                        else:
                            vk.send_message('Не выбран профиль для поиска!')

                    elif query.find('!relation') != -1:
                        if vk.is_profile_picked:
                            vk.set_relation(query.split('!relation')[-1])
                        else:
                            vk.send_message('Не выбран профиль для поиска!')

                    elif query.find('!search') != -1:
                        if vk.is_profile_picked:
                            try:
                                amount = int(query.split('!search ')[-1])
                            except ValueError:
                                vk.send_message('Неверный синтаксис команды, '
                                                'используйте только положительные целые числа.\nПример: !search 10')
                                continue
                            if amount < 0:
                                vk.send_message('Неверно введено количество, '
                                                'используйте только положительные целые числа.')
                                continue
                            vk.search_users(amount)
                            vk.send_message(f'Поиск завершен. Для повторного поиска введите !search')
                        else:
                            vk.send_message('Невозможно выполнить поиск, профиль ВК не был выбран.')

                    else:
                        vk.send_message('Неверная команда, !start для начала работы')
