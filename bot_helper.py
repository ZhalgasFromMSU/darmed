from __future__ import annotations
import telebot.types as types
import typing

from bot import TBot
from db_helper import DatabaseHandler, TDbClient


class TScenarioItem:
    def __init__(self,
                 ask_text: str,
                 register_key: str,
                 value_type: typing.Type = str,
                 key_filter: typing.Callable[[typing.Any], bool] = None,
                 keyboard_rows: typing.List[str] = None):
        self._ask_text = ask_text
        self._register_key = register_key
        self._value_type = value_type
        self._key_filter = key_filter
        self._keyboard: types.ReplyKeyboardMarkup = None
        self._keyboard_rows: typing.List[str] = keyboard_rows
        if self._keyboard_rows is not None:
            self._keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for row in self._keyboard_rows:
                self._keyboard.row(row)

        self._next_ask: typing.Optional[TScenarioItem] = None

    def get_ask_function(self, bot: TBot) -> typing.Callable[[int], None]:
        def ret_func(chat_id: int):
            bot.send_message(chat_id, self._ask_text, reply_markup=self._keyboard)
            bot.register_next_step_handler_by_chat_id(chat_id, self.get_register_function(bot))

        return ret_func

    def get_register_function(self, bot: TBot) -> typing.Callable[[types.Message], None]:
        def ret_func(message: types.Message):
            if self._keyboard is not None and message.text not in self._keyboard_rows:
                bot.send_message(message.chat.id, "Выберите ответ из списка ниже")
                self.get_ask_function(bot)(message.chat.id)
                return

            if self._key_filter is None or self._key_filter(message.text):
                bot.register_chat_state(message.chat.id, self._register_key, self._value_type(message.text))
            else:
                bot.send_message(message.chat.id, "Неправильный формат, попробуйте ещё раз")
                self.get_ask_function(bot)(message.chat.id)
                return

            if self._next_ask is not None:
                self._next_ask(message.chat.id)

        return ret_func

    def set_next_ask(self, next_ask: typing.Callable[[int], None]):
        self._next_ask = next_ask


class TScenarioHandler:
    def __init__(self, bot: TBot, scenario: typing.List[TScenarioItem], ending_message: str, db_handler: DatabaseHandler):
        self._bot: TBot = bot
        self._scenario: typing.List[TScenarioItem] = scenario
        self._db_handler: DatabaseHandler = db_handler

        def ending_func(chat_id: int):
            self._bot.send_message(chat_id, ending_message)
            chat_info: typing.Optional[typing.Dict[str, typing.Any]] = self._bot.pop_from_chat_state(chat_id)
            if chat_info is None:
                return
            self._db_handler.save_client(TDbClient.from_dict(chat_id, chat_info))

        for item, next_item in zip(self._scenario, self._scenario[1:]):
            item.set_next_ask(next_item.get_ask_function(self._bot))
        else:
            self._scenario[-1].set_next_ask(ending_func)

    def get_scenario_beginning(self) -> typing.Callable[[types.Message], None]:
        def ret_func(message: types.Message):
            return self._scenario[0].get_ask_function(self._bot)(message.chat.id)

        return ret_func
