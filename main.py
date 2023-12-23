from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import callback_query
from aiogram.types import InputFile
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import os
from app import keyboards as kb
from app import database as db

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)
import os

photo_directory = "C:/Users/Akelk/arts_store2/pythonProject/photo"  # Путь к папке с фотографиями


async def on_startup(_):
    await db.db_start()
    print('Бот успешно запустился')


class NewOrder(StatesGroup):
    type = State()
    name = State()
    description = State()
    price = State()
    photo = State()


class DeleteBy(StatesGroup):
    name = State()
    id = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await db.cmd_start_db(message.from_user.id)
    await message.answer_sticker('CAACAgIAAxkBAAMpZBAAAfUO9xqQuhom1S8wBMW98ausAAI4CwACTuSZSzKxR9LZT4zQLwQ')
    await message.answer(f'{message.from_user.first_name}, добро пожаловать в магазин картин!',
                         reply_markup=kb.main)
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы авторизовались как администратор!', reply_markup=kb.main_admin)

@dp.message_handler(text='В главное меню')
async def process_main_menu(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Выберите действие:', reply_markup=kb.main_admin)
    else:
        await message.answer('Выберите действие:', reply_markup=kb.main)

@dp.message_handler(text='Каталог')
async def catalog(message: types.Message):
    await message.answer(f'Держи!', reply_markup=kb.catalog_list)


# Обработчик для кнопки "Удалить из корзины"
# Обработчик для кнопки "Удалить из корзины"
@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def delete_item_from_cart(call: types.CallbackQuery):
    user_id = call.from_user.id
    print(f"Содержимое callback_data: {call.data}")  # Вывод содержимого call.data для отладки
    item_id = int(call.data.split('_')[1])
    print(f"Извлеченный item_id: {item_id}")  # Вывод извлеченного item_id для отладки

    await db.delete_item_from_cart(user_id, item_id)  # Вызываем функцию удаления товара из корзины
    await bot.answer_callback_query(call.id, text="Товар удален из корзины")

# Обработчик для кнопки "Сделать заказ"
@dp.callback_query_handler(lambda c: c.data.startswith('order_'))
async def make_order(call: types.CallbackQuery):
    user_id = call.from_user.id
    print(f"Содержимое callback_data: {call.data}")  # Вывод содержимого call.data для отладки
    item_id = int(call.data.split('_')[1])
    print(f"Извлеченный item_id: {item_id}")  # Вывод извлеченного item_id для отладки

    # Здесь можно добавить логику выполнения заказа, например, добавление товара в базу данных заказов
    await process_order(user_id, item_id)  # Здесь нужно написать логику обработки заказа

    await bot.answer_callback_query(call.id, text="Заказ оформлен успешно")

# Пример функции обработки заказа
async def process_order(user_id, item_id):
    # Здесь может содержаться логика обработки заказа, такая как добавление товара в базу данных заказов
    print(f"Пользователь {user_id} сделал заказ товара с id {item_id}")
    await db.delete_item_from_cart(user_id, item_id)

# Функция для отображения корзины
@dp.message_handler(text='Корзина')
async def cart(message: types.Message):
    user_id = message.from_user.id
    cart_items = await db.get_user_cart_items(user_id)

    if cart_items:
        for item_id, name, description, price, photo in cart_items:
            photo_path = os.path.join(photo_directory, photo)
            with open(photo_path, 'rb') as photo_file:
                caption = f"ID товара: {item_id}, Название: {name}, Описание: {description}, Цена: {price}"

                keyboard = kb.generate_cart_keyboard(item_id)
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'), caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Ваша корзина пуста")

@dp.message_handler(text='Контакты')
async def contacts(message: types.Message):
    await message.answer(f'Покупать товар у него: @slomnikc')


@dp.message_handler(text='Панель администратора')
async def contacts(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы вошли в админ-панель', reply_markup=kb.admin_panel)
    else:
        await message.reply('Я тебя не понимаю.')

async def delete_photo_by_filename(file_name):
    # Обработка пути к файлу
    file_path = os.path.join(photo_directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)  # Удаляем файл
        return True
    else:
        return False
@dp.message_handler(text='Удалить товар')
async def delete_by_name(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(text=f"Пожалуйста, выберите товар который нужно удалить", reply_markup=kb.delete_panel)
    else:
        await message.reply('У вас нет прав для выполнения этой команды.')


@dp.message_handler(text='Удалить по названию')
async def delete_by_name(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Введите название товара, который необходимо удалить')
        await DeleteBy.name.set()
    else:
        await message.reply('У вас нет прав для выполнения этой команды.')

@dp.message_handler(state=DeleteBy.name)
async def process_delete_by_name(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        name = message.text
        photo_name = await db.get_item_photo_by_name(name)  # Получение названия фотографии
        if photo_name:
            await db.delete_item_by_name(name)
            await delete_photo_by_filename(photo_name)  # Удаление фотографии
            await state.finish()
            await message.answer(f'Товар с названием "{name}" успешно удален вместе с фотографией.')
        else:
            await message.answer('Товар с таким названием не найден.')
            await state.finish()
    else:
        await message.reply('У вас нет прав для выполнения этой команды.')


@dp.message_handler(text='Удалить по id')
async def delete_by_id(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Введите артикул товара, который необходимо удалить')
        await DeleteBy.id.set()
    else:
        await message.reply('У вас нет прав для выполнения этой команды.')

@dp.message_handler(state=DeleteBy.id)
async def process_delete_by_id(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        id = int(message.text)
        photo_name = await db.get_item_photo_by_id(id)  # Получение названия фотографии
        if photo_name:
            await db.delete_item_by_id(id)
            await delete_photo_by_filename(photo_name)  # Удаление фотографии
            await state.finish()
            await message.answer(f'Товар с артикулом "{id}" успешно удален вместе с фотографией.')
        else:
            await message.answer('Товар с таким артикулом не найден.')
            await state.finish()
    else:
        await message.reply('У вас нет прав для выполнения этой команды.')

@dp.callback_query_handler(lambda c: c.data.startswith('add_to_cart_'))
async def add_to_cart_handler(call: types.CallbackQuery):
    split_data = call.data.split('_')
    print(split_data)  # Добавляем эту строку для отображения значений, полученных после разделения
    item_id = int(split_data[3])
    user_id = call.from_user.id
    await db.add_item_to_cart(user_id, item_id)
    await call.message.answer("Товар добавлен в корзину!")

@dp.message_handler(text='Пейзажи')
async def handle_show_landscapes(message: types.Message):
    landscapes = await db.get_landscapes()
    if landscapes:
        for landscape in landscapes:
            i_id, name, description, price, photo = landscape
            photo_path = os.path.join(photo_directory, photo)
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {i_id}, Название: {name}, Описание: {description}, Цена: {price}"
                keyboard = kb.generate_cart(i_id)
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'), caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Пейзажи не найдены в каталоге")
@dp.message_handler(text='Пейзажи')
async def handle_show_landscapes(message: types.Message):
    landscapes = await db.get_landscapes()
    if landscapes:
        for landscape in landscapes:
            i_id, name, description, price, photo = landscape
            photo_path = os.path.join(photo_directory, photo)
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {i_id}, Название: {name}, Описание: {description}, Цена: {price}"
                keyboard = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{str(i_id)}"))
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'),
                                     caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Пейзажи не найдены в каталоге")
@dp.message_handler(text='Натюрморты')
async def handle_show_still_life(message: types.Message):
    still_life = await db.get_still_lifes()
    if still_life:
        for stl in still_life:
            i_id, name, description, price, photo = stl
            photo_path = os.path.join(photo_directory, photo)  # Формируем полный путь к файлу фотографии
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {i_id}, Название: {name}, Описание: {description}, Цена: {price}"
                keyboard = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{str(i_id)}"))
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'),
                                     caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Натюрморты не найдены в каталоге")

@dp.message_handler(text='Портреты')
async def handle_show_portrets(message: types.Message):
    portret = await db.get_portrets()
    if portret:
        for prt in portret:
            i_id, name, description, price, photo = prt
            photo_path = os.path.join(photo_directory, photo)  # Формируем полный путь к файлу фотографии
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {i_id}, Название: {name}, Описание: {description}, Цена: {price}"
                await bot.send_photo(chat_id=message.chat.id, photo=InputFile(photo_file, filename='photo'), caption=caption)
    else:
        await message.reply("Портреты не найдены в каталоге")

# Обработка отмены
@dp.message_handler(text='Отмена', state='*')
async def cancel_add_item(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'photo' in data:
            del data['photo']  # Удалить сохраненный путь к фотографии
        if 'description' in data:
            del data['description']  # Удалить введенное описание, если есть
    await state.finish()
    await message.answer('Добавление товара отменено.', reply_markup=kb.admin_panel)

# Добавление товара
@dp.message_handler(text='Добавить товар')
async def add_item(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await NewOrder.type.set()
        await message.answer(f'Выберите тип товара', reply_markup=kb.catalog_list)
    else:
        await message.reply('Я тебя не понимаю.')


@dp.callback_query_handler(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer(f'напишите название товара', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Напишите описание товара')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.description)
async def add_item_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await message.answer('Напишите цену товара')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.price)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.answer('Отправьте фотографию товара')
    await NewOrder.next()


@dp.message_handler(lambda message: not message.photo, state=NewOrder.photo)
async def add_item_photo_check(message: types.Message):
    await message.answer('Это не фотография!')


@dp.message_handler(content_types=['photo'], state=NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        file_name = f"photo_{message.photo[-1].file_id}.jpg"
        photo_path = os.path.join(photo_directory, file_name)
        file_info = await bot.get_file(message.photo[-1].file_id)
        # Сохранение файла на сервере
        downloaded_file = await bot.download_file(file_info.file_path)

        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file.read())

        data['photo'] = file_name
    await db.add_item(state)
    await message.answer('Товар успешно создан!', reply_markup=kb.admin_panel)
    await state.finish()


@dp.message_handler(content_types=['sticker'])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)
    await bot.send_message(message.from_user.id, message.chat.id)


@dp.message_handler(content_types=['document', 'photo'])
async def forward_message(message: types.Message):
    await bot.forward_message(os.getenv('GROUP_ID'), message.from_user.id, message.message_id)


@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == 'naturmorts':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали натюрморты')
        await handle_show_still_life(callback_query.message)
    elif callback_query.data == 'peizaj':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали пейзажи')
        await handle_show_landscapes(callback_query.message)
    elif callback_query.data == 'portrets':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали портреты')
        await handle_show_portrets(callback_query.message)


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Я тебя не понимаю')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
