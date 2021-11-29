import time
import signal
import sys

import config
import bot_options
from bot_helper import TScenarioItem, TScenarioHandler
from bot import TBot
from db_helper import DatabaseHandler


def raise_keyboard_interruption(*args):
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, raise_keyboard_interruption)


def main():
    bot = TBot(config.BOT_TOKEN)
    scenario = TScenarioHandler(
        bot,
        [
            TScenarioItem("Как Вас зовут?", "name"),
            TScenarioItem("Ваш пол?", "sex", keyboard_rows= bot_options.SEXES),
            TScenarioItem("На каком языке Вам удобнее вести диалог?", "lang", keyboard_rows=bot_options.LANGUAGES),
            TScenarioItem("Сколько Вам лет?", "age", value_type=int, key_filter=lambda text: text.isnumeric()),
            TScenarioItem("Какая у Вас проблема из списка?", "pr_type", keyboard_rows=bot_options.PROBLEM_TYPES),
            TScenarioItem("Опишите Вашу проблему", "pr_descr"),
        ],
        "Ваша зявка на рассмотрении",
        DatabaseHandler(),
    )
    bot.register_initial_action(scenario.get_scenario_beginning())
    bot.start()
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        print("zdes2")
        bot.stop()


if __name__ == "__main__":
    main()
