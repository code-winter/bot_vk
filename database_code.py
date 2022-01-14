import sqlalchemy as sql
from creds import DB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound

engine = sql.create_engine(DB)
session = sessionmaker(bind=engine)
Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'
    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, unique=True)
    photo_ids = sql.Column(sql.String)


class Blacklist(Base):
    __tablename__ = 'Blacklisted_Users'
    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, unique=True)


class Favorites(Base):
    __tablename__ = 'Favored_Users'
    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, unique=True)
    photo_ids = sql.Column(sql.String)


Base.metadata.create_all(engine)


def add_user(user_id: int, photos: str):
    """
    Функция для добавления пользователя в БД
    :param user_id: ID пользователя ВК
    :param photos: строка со ссылками на объекты фотографий ВК
    """
    s = session()
    user = Users(user_id=user_id, photo_ids=photos)
    s.add(user)
    s.commit()
    s.close()


def block_user(user_id: int):
    """
    Функция для добавления пользователя в таблицу заблокированных в БД.
    Также удаляет пользователя из списка пользователей.
    :param user_id: ID пользователя ВК
    """
    s = session()
    user = Blacklist(user_id=user_id)
    s.add(user)
    if check_user_and_photos(user_id):
        user_record = s.query(Users).filter(Users.user_id == user_id)
        user_record.delete(synchronize_session='fetch')
    s.commit()
    s.close()


def favorite_user(user_id):
    """
    Функция для добавления пользователя в таблицу избранных в БД
    :param user_id: ID пользователя ВК
    """
    s = session()
    query = s.query(Users).filter(Users.user_id == user_id).one()
    user = Favorites(user_id=query.user_id, photo_ids=query.photo_ids)
    s.add(user)
    s.commit()
    s.close()


def get_user(user_id) -> list:
    """
    Функция для выдачи пользователя из БД по его ID
    :param user_id: ID пользователя ВК
    """
    s = session()
    query = s.query(Users).filter(Users.user_id == user_id).one()
    user = query.user_id
    photo = query.photo_ids
    result = [user, photo]
    s.close()
    return result


def get_user_for_likes(user_id):
    """
    Функция для выдачи пользователи или из списков пользователей, или из списка избранных.
    :param user_id: ID пользователя ВК
    """
    s = session()
    try:
        query = s.query(Users).filter(Users.user_id == user_id).one()
        user = query.user_id
        photo = query.photo_ids
        result = [user, photo]
        s.close()
        return result
    except NoResultFound:
        try:
            second_query = s.query(Favorites).filter(Favorites.user_id == user_id).one()
            user = second_query.user_id
            photo = second_query.photo_ids
            result = [user, photo]
            s.close()
            return result
        except NoResultFound:
            return False


def get_all_users() -> list:
    """
    Функция для выдачи информации по всем пользователям в БД
    """
    s = session()
    result = []
    query = s.query(Users).all()
    for record in query:
        user = record.user_id
        photos = record.photo_ids
        result.append([user, photos])
    s.close()
    return result


def get_blocked_users() -> list:
    """
    Функция для вывода всех пользователей в черном списке
    """
    s = session()
    result = []
    query = s.query(Blacklist).all()
    for record in query:
        user = record.user_id
        result.append(user)
    s.close()
    return result


def get_favored_users() -> list:
    """
    Функция для вывода всех пользователей избранного списка.
    """
    s = session()
    result = []
    query = s.query(Favorites).all()
    for record in query:
        user = record.user_id
        photos = record.photo_ids
        result.append([user, photos])
    s.close()
    return result


def check_user_and_photos(user_id: int) -> bool:
    """
    Функция для проверки наличия пользователя в списке пользователей.
    :param user_id: ID пользователя ВК
    """
    s = session()
    res = s.query(Users).filter(Users.user_id == user_id).all()
    if res:
        s.close()
        return True
    else:
        s.close()
        return False


def check_blacklist(user_id: int) -> bool:
    """
    Функция для проверки наличия пользователя в черном списке.
    :param user_id: ID пользователя ВК
    :return:
    """
    s = session()
    res = s.query(Blacklist).filter(Blacklist.user_id == user_id).all()
    if res:
        s.close()
        return True
    else:
        s.close()
        return False


def check_favored(user_id: int) -> bool:
    """
    Функция для проверки наличия пользователя в списке избранных.
    :param user_id: ID пользователя ВК
    """
    s = session()
    res = s.query(Favorites).filter(Favorites.user_id == user_id).all()
    if res:
        s.close()
        return True
    else:
        s.close()
        return False


def get_len_users() -> int:
    """
    Функция для получения длины списка пользователей.
    """
    s = session()
    length = s.query(sql.func.count(Users.id)).scalar()
    return length


def get_len_blacklist() -> int:
    """
    Функция для получения длины черного списка.
    """
    s = session()
    length = s.query(sql.func.count(Blacklist.id)).scalar()
    return length


def get_len_favored() -> int:
    """
    Функция для получения длины избранного списка.
    """
    s = session()
    length = s.query(sql.func.count(Favorites.id)).scalar()
    return length


def drop_all():
    """
    Функция для очистки ВСЕЙ БД и ее последующей ре-инициализации.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def drop_blacklist():
    """
    Функция для очистки черного списка и его последующей ре-инициализации.
    """
    Base.metadata.drop_all(engine, tables=[Blacklist.__table__])
    Base.metadata.create_all(engine, tables=[Blacklist.__table__])


def drop_favored():
    """
    Функция для очистки избранного списка и его последующей ре-инициализации.
    :return:
    """
    Base.metadata.drop_all(engine, tables=[Favorites.__table__])
    Base.metadata.create_all(engine, tables=[Favorites.__table__])


def drop_users():
    """
    Функция для очистки списка пользователей и его последующей ре-инициализации.
    :return:
    """
    Base.metadata.drop_all(engine, tables=[Users.__table__])
    Base.metadata.create_all(engine, tables=[Users.__table__])
