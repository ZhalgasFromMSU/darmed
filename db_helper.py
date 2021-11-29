from __future__ import annotations

import typing
import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import types
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config
import bot_options


Base = declarative_base()

class TDbClient(Base):
    __tablename__ = "clients"

    chat_id = sqlalchemy.Column(types.Integer, primary_key=True)
    name = sqlalchemy.Column(types.Text)
    sex = sqlalchemy.Column(types.Enum("male", "female", name="sex"))
    lang = sqlalchemy.Column(types.Enum("ru", "kz", "en", name="lang"))
    age = sqlalchemy.Column(types.Integer)
    pr_type = sqlalchemy.Column(types.Integer)
    pr_descr = sqlalchemy.Column(types.Text)

    @classmethod
    def from_dict(cls, chat_id: int, properties: typing.Dict[str, typing.Any]) -> TDbClient:
        properties["sex"] = "male" if properties["sex"] == "Мужской" else "female"
        properties["lang"] = {"Русский": "ru", "Казахский": "kz", "Английский": "en"}[properties["lang"]]
        properties["pr_type"] = bot_options.PROBLEM_TYPES.index(properties["pr_type"])
        return cls(chat_id=chat_id, **properties)

    @staticmethod
    def col_names() -> typing.List[str]:
        return [
            "chat_id",
            "name",
            "sex",
            "lang",
            "age",
            "pr_type",
            "pr_descr",
        ]


class DatabaseHandler():
    def __init__(self):
        self._db_engine: sqlalchemy.engine.Engine = create_engine(config.DATABASE_RECIPE, client_encoding='utf8')
        Base.metadata.create_all(self._db_engine)
        self._Session = sessionmaker(self._db_engine)  # session factory

    @staticmethod
    def get_clients_filter(client: TDbClient) -> typing.List[BinaryExpression]:
        return [
            getattr(TDbClient, col_name) == getattr(client, col_name)
            for col_name in TDbClient.col_names()
            if getattr(client, col_name) is not None
        ]

    def save_client(self, client: TDbClient) -> bool:
        try:
            with self._Session() as session:
                session.add(client)
                session.commit()
            return True
        except sqlalchemy.exc.IntegrityError:
            return False

    def get_client(self, client: TDbClient) -> TDbClient:
        with self._Session() as session:
            return session.query(TDbClient).filter(*self.get_clients_filter(client)).one()
