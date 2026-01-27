from aiogram import Bot
from aiogram.types import BotCommand

#Чтобы команды вылезали подсказками в чате 
async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск бота"),
            BotCommand(command="set_profile", description="Создание профиля"),
            BotCommand(command="help", description="Список команд"),
            BotCommand(command="log_water", description="Добавить воду (мл)"),
            BotCommand(command="log_food", description="Добавить еду"),
            BotCommand(command="log_workout", description="Добавить тренировку"),
            BotCommand(command="profile", description="Показать профиль"),
            BotCommand(command="check_progress", description="Прогресс за сегодня"),
            BotCommand(command="recommend_food", description="Совет низкокалорийных продуктов"),
            BotCommand(command="graph_water", description="График выпитой воды по дням"),
            BotCommand(command="graph_calories", description="График потребленных калорий по дням"),
            BotCommand(command="reset_today", description="Обнулить записи за сегодня"),
        ]
    )