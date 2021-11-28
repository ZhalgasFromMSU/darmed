import typing
import telebot
import telebot.types as types
import threading
from collections import defaultdict


class TBot(threading.Thread, telebot.TeleBot):
    def __init__(self, token: str):
        threading.Thread.__init__(self)
        telebot.TeleBot.__init__(self, token, threaded=False)
        self._chat_state: typing.Dict[int, typing.Dict[str, typing.Any]] = defaultdict(dict)

    def run(self):
        """Start bot polling in another thread
        """
        self.polling(non_stop=True)

    def stop(self):
        """Stop polling
        """
        self.stop_polling()

    def register_chat_state(self, chat_id: int, key: str, value: typing.Any):
        self._chat_state[chat_id][key] = value

    @property
    def chat_state(self):
        return self._chat_state

    def register_initial_action(self, scenario):
        """What should be done after user sends "/start"
        """
        self.register_message_handler(scenario.get_scenario_beginning(), commands=["start"])
