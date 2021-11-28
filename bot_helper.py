from __future__ import annotations
import telebot.types as types
import typing

from bot import TBot


class TScenarioItem:
    def __init__(self, ask_text: str, register_key: str, keyboard_rows: typing.Optional[typing.List[str]] = None):
        self._ask_text = ask_text
        self._register_key = register_key
        self._keyboard = None
        if keyboard_rows is not None:
            self._keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for row in keyboard_rows:
                self._keyboard.row(row)

        self._next_ask: typing.Optional[TScenarioItem] = None

    def get_ask_function(self, bot: TBot) -> typing.Callable[[int], None]:
        def ret_func(chat_id: int):
            bot.send_message(chat_id, self._ask_text, reply_markup=self._keyboard)
            bot.register_next_step_handler_by_chat_id(chat_id, self.get_register_function(bot))

        return ret_func

    def get_register_function(self, bot: TBot) -> typing.Callable[[types.Message], None]:
        def ret_func(message: types.Message):
            bot.register_chat_state(message.chat.id, self._register_key, message.text)
            if self._next_ask is not None:
                self._next_ask(message.chat.id)

        return ret_func

    def set_next_ask(self, next_ask: typing.Callable[[int], None]):
        self._next_ask = next_ask


class TScenarioHandler:
    def __init__(self, bot: TBot, scenario: typing.List[TScenarioItem], ending_message: str):
        self._bot: TBot = bot
        self._scenario: typing.List[TScenarioItem] = scenario

        for item, next_item in zip(self._scenario, self._scenario[1:]):
            item.set_next_ask(next_item.get_ask_function(self._bot))
        else:
            self._scenario[-1].set_next_ask(lambda chat_id: self._bot.send_message(chat_id, ending_message))

    def get_scenario_beginning(self) -> typing.Callable[[types.Message], None]:
        def ret_func(message: types.Message):
            return self._scenario[0].get_ask_function(self._bot)(message.chat.id)

        return ret_func
