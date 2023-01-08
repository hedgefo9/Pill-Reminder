import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio
from aiogram.filters import Command, CommandObject

token = open('token.txt').readline()

users = {}

async def handle_start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Я помогу вам пить таблетки вовремя\n\n' +
                         'Мои команды:\n' +
                         '• Для добавления препарата используйте команду \n' +
                         '/add {Название препарата}, {Количество препарата в один приём с единицами измерения}, '
                         '{Время}, {Количество дней приёма}\n' +
                         'Таким образом, каждый день в указанное время я буду вам напоминать о приёме данного лекарства\n' +
                         'Пример команды: /add Парацетамол, 1 таблетка, 10:00, 3\n' +
                         '• Для просмотра текущего списка принимаемых препаратов используйте команду /show\n' +
                         '• Для удаления лекарства из списка принимаемых препаратов используйте команду '
                         '/del {Уникальный номер из списка препаратов, который можно запросить при помощи команды /show}\n')


async def handle_delete(message: Message, command: CommandObject):
    try:
        pill_id_to_del = int(command.args)
        user_id = message.from_user.id
        current_answer = ' '
        if user_id in users:
            if (('pills' in users[user_id]) and
                    (users[user_id]['pills'] != {})):
                if (pill_id_to_del in users[user_id]['pills']):
                    del users[user_id]['pills'][pill_id_to_del]
                    current_answer = "Препарат успешно удален"
                else:
                    current_answer = "Указанный уникальный номер принимаемого препарата отсутствует в списке!"
            else:
                current_answer = 'Нет принимаемых препаратов 🥳'
        else:
            current_answer = 'Нет принимаемых препаратов 🥳'
        await message.answer(current_answer)
    except Exception as e:
        await message.answer("Команда /del использована неверно!")


async def handle_show(message: Message):
    current_answer = 'Принимаемые вами препараты:\n'
    current_answer += '<b>Формат: Уникальный номер) Название препарата, Количество препарата в один приём с единицами измерения, Время, Количество дней приёма</b>\n\n'
    user_id = message.from_user.id
    if user_id in users:
        if len(users[user_id]['pills']):
            for id in users[user_id]['pills']:
                current_answer += f'{id}) ' + ', '.join(str(x) for x in users[user_id]['pills'][id]) + '\n'
        else:
            current_answer = 'Нет принимаемых препаратов 🥳'
    else:
        current_answer = 'Нет принимаемых препаратов 🥳'
    await message.answer(current_answer, parse_mode='HTML')


# {Название препарата} {Количество препарата} {Время} {Количество дней приёма}
async def handle_add_reminder(message: Message, command: CommandObject):
    try:
        parts_of_text = command.args.split(',')
        parts_of_text = [x.strip() for x in parts_of_text]
        pill_name = parts_of_text[0]
        pill_dose = parts_of_text[1]
        pill_time = parts_of_text[2]
        pill_days = int(parts_of_text[3])
        user_id = message.from_user.id
        current_pill_id = None
        if (user_id not in users) or (users[user_id]['pills'] == {}):
            users[user_id] = {
                'pills': {
                    1: [pill_name, pill_dose, pill_time, pill_days]
                }
            }
            current_pill_id = 1
        else:
            current_pill_id = max(users[user_id]['pills'].keys()) + 1
            users[user_id]['pills'][current_pill_id] = [pill_name, pill_dose, pill_time, pill_days]

        await message.answer("Препарат успешно добавлен")

        pill_time_hour, pill_time_minute = (int(x) for x in pill_time.split(":"))
        for i in range(pill_days):
            now = datetime.datetime.now()
            next_reminder = datetime.datetime(now.year, now.month, now.day, pill_time_hour, pill_time_minute, now.second)
            if (next_reminder > now):
                delay = (next_reminder - now).seconds
            else:
                next_reminder += datetime.timedelta(days=1)
                delay = (next_reminder - now).seconds
            await asyncio.sleep(delay)
            if (current_pill_id in users[user_id]['pills']):
                users[user_id]['pills'][current_pill_id][3] -= 1
                await message.answer(f'❗ {message.from_user.first_name}, пришло время принять препарат "{pill_name}", количество: {pill_dose} ❗')
            else:
                break
        if current_pill_id in users[user_id]['pills']:
            del users[user_id]['pills'][current_pill_id]
    except Exception as e:
        await message.answer(f'Команда /add использована неверно!')


async def start():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.message.register(handle_start, Command(commands='start'))
    dp.message.register(handle_add_reminder, Command(commands='add'))
    dp.message.register(handle_show, Command(commands='show'))
    dp.message.register(handle_delete, Command(commands='del'))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(start())
