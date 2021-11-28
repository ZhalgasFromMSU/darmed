import config
import time

from bot_helper import TScenarioItem, TScenarioHandler
from bot import TBot


def main():
    bot = TBot(config.BOT_TOKEN)
    scenario = TScenarioHandler(
        bot,
        [
            TScenarioItem("Как Вас зовут?", "name"),
            TScenarioItem("Ваш пол?", "sex"),
            TScenarioItem("На каком языке Вам удобнее вести диалог?", "lang"),
            TScenarioItem("Сколько Вам лет?", "age"),
            TScenarioItem("Какая у Вас проблема из списка?", "type", keyboard_rows=[
                "Уход за кожей",
                "Уход за волосами",
                "Питание",
                "Универсальные базовые витамины",
                "Совместимость витаминов",
                "Анализы",
                "Планирование беременности",
                "Послеродовой период",
                "Коррекция веса",
                "Недомогание, слабость",
                "Проблемы менструального цикла",
            ]),
            TScenarioItem("Опишите Вашу проблему", "descr"),
        ],
        "Ваша зявка на рассмотрении",
    )
    bot.register_initial_action(scenario)
    bot.start()
    time.sleep(20)
    bot.stop()


if __name__ == "__main__":
    main()