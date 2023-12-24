from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import state
from aiogram.types import callback_query
from aiogram.types import InputFile
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import os
from datetime import date
from app import keyboards as kb
from app import database as db
from app import models as md
import pandas as pd
from docx import Document
import os

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)

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
@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def delete_item_from_cart(call: types.CallbackQuery):
    print("ПУСТО")
    user_id = call.from_user.id
    print(f"Содержимое callback_data: {call.data}")  # Вывод содержимого call.data для отладки
    item_id = int(call.data.split('_')[1])
    print(f"Извлеченный item_id: {item_id}")  # Вывод извлеченного item_id для отладки

    cart_item = md.Cart.get_or_none(item_id=item_id, user_id=user_id)  # Получить конкретный товар из корзины
    if cart_item:  # Проверить, найден ли товар
        cart_item.delete_instance()
        await bot.answer_callback_query(call.id, text="Товар удален из корзины")  # Ответить на запрос об удалении
    else:
        await bot.answer_callback_query(call.id, text="Товар не найден в корзине")  # Ответить, если товар не найден


# Обработчик для кнопки "Сделать заказ"
@dp.callback_query_handler(lambda c: c.data.startswith('order_'))
async def make_order(call: types.CallbackQuery):
    user_id = call.from_user.id
    print(f"Содержимое callback_data: {call.data}")
    item_id = int(call.data.split('_')[1])
    print(f"Извлеченный item_id: {item_id}")

    # Получаем цену товара
    item = md.Item.get(md.Item.i_id == item_id)
    if item:
        price = item.price

        # Создаем запись в таблице History
        history_entry = md.History.create(item_id=item_id, i_id=user_id, date=date.today(), price=price)
        history_entry.save()

        item.delete_instance()

        cart_item = md.Cart.get_or_none(item_id=item_id)  # Получить конкретный товар из корзины
        if cart_item:  # Проверить, найден ли товар
            cart_item.delete_instance()
        await bot.answer_callback_query(call.id, text="Заказ оформлен успешно")
    else:
        await bot.answer_callback_query(call.id, text="Вы не успели, товар куплен!")




# Функция для отображения корзины
@dp.message_handler(text='Корзина')
async def cart(message: types.Message):
    user_id = message.from_user.id

    # Проверяем наличие товаров в корзине перед удалением
    query = md.Item.select(md.Item.i_id)
    cart_items_to_delete = md.Cart.delete().where(~(md.Cart.item_id.in_(query)))
    deleted_rows = cart_items_to_delete.execute()

    if deleted_rows:
        # Уведомляем пользователя об удаленных товарах из корзины
        await message.reply(f"Некоторые товары были удалены из вашей корзины, так как их больше нет в магазине.")

    # Получаем список товаров в корзине пользователя
    cart_items = (md.Item
                  .select(md.Item.i_id, md.Item.name, md.Item.description, md.Item.price, md.Item.photo)
                  .join(md.Cart, on=(md.Item.i_id == md.Cart.item_id))
                  .where(md.Cart.user_id == user_id))

    if cart_items:
        for cart_item in cart_items:
            item_id = cart_item.i_id
            name = cart_item.name
            description = cart_item.description
            price = cart_item.price
            photo = cart_item.photo

            # Подготавливаем сообщение о товаре
            caption = f"ID товара: {item_id}, Название: {name}, Описание: {description}, Цена: {price}"

            # Генерируем клавиатуру для товара в корзине
            keyboard = kb.generate_cart_keyboard(item_id)

            # Отправляем сообщение с изображением товара
            await bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=keyboard)
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption, reply_markup=keyboard)
    else:
        # Отправляем уведомление, когда корзина пользователя пуста
        await message.reply("Ваша корзина пуста")


@dp.message_handler(text='Контакты')
async def contacts(message: types.Message):
    await message.reply('@slonikmc')

import os
import pandas as pd
from aiogram import types
from docx import Document

# ... (остальной код)

@dp.message_handler(text='Сделать выгрузку данных')
async def import_to(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        # Удаление файла, если уже существует
        if os.path.exists('history_output.xlsx'):
            os.remove('history_output.xlsx')
        if os.path.exists('history_output.docx'):
            os.remove('history_output.docx')

        # Выборка данных из таблицы History
        query = md.History.select()

        # Преобразование данных из выборки в DataFrame
        history_data = list(query.dicts())
        df = pd.DataFrame(history_data)

        # Экспорт DataFrame в Excel файл
        df.to_excel('history_output.xlsx', index=False)

        # Создание файла docx и запись данных из DataFrame построчно
        doc = Document()
        doc.add_heading('История Заказов', 0)

        for index, row in df.iterrows():
            for column in df.columns:
                doc.add_paragraph(f"{column}: {row[column]}")
            doc.add_paragraph('')

        doc.save('history_output.docx')

        # Отправка файлов пользователю
        with open('history_output.xlsx', 'rb') as file_xlsx, open('history_output.docx', 'rb') as file_docx:
            await message.reply_document(file_xlsx, caption="Excel файл")
            await message.reply_document(file_docx, caption="Word файл")

    else:
        await message.reply('У Вас недостаточно прав')


@dp.message_handler(text='История заказов')
async def show_history(message: types.Message):
    query = md.History.select()
    orders_info = "История заказов:\n"
    if query.count() > 0:
        for order in query:
            order_info = f"Заказ №{order.item_id}: ID - {order.i_id}, Дата - {order.date}, Цена - {order.price}\n"
            orders_info += order_info
    else:
        orders_info = "Нет доступных заказов."

    await message.reply(orders_info)


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
        item = md.Item.get_or_none(name=name)  # Retrieve the item by name from the database
        if item:
            photo_name = item.photo  # Assuming the photo name is stored as an attribute on the Item model
            item.delete_instance()  # Delete the item from the database
            await delete_photo_by_filename(photo_name)  # Assuming a function to delete the photo by filename
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
        id = message.text
        item = md.Item.get_or_none(i_id=id)  # Retrieve the item by name from the database
        if item:
            photo_name = item.photo  # Assuming the photo name is stored as an attribute on the Item model
            item.delete_instance()  # Delete the item from the database
            await delete_photo_by_filename(photo_name)  # Assuming a function to delete the photo by filename
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
    new_art = md.Cart.create(user_id=user_id, item_id=item_id)
    new_art.save()
    await call.message.answer("Товар добавлен в корзину!")


@dp.message_handler(text='Пейзажи')
async def handle_show_landscapes(message: types.Message):
    landscapes = md.Item.select().where(
        md.Item.category == 'peizaj')  # Assuming 'Пейзажи' is the category for landscapes
    if landscapes:
        for landscape in landscapes:
            photo_path = os.path.join(photo_directory,
                                      landscape.photo)  # Assuming 'photo' is the attribute representing the photo path
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {landscape.i_id}, Название: {landscape.name}, Описание: {landscape.description}, Цена: {landscape.price}"
                keyboard = kb.generate_cart(landscape.i_id)  # Assuming a function to generate the cart keyboard
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'),
                                     caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Пейзажи не найдены в каталоге")


@dp.message_handler(text='Натюрморты')
async def handle_show_still_life(message: types.Message):
    still_life = md.Item.select().where(md.Item.category == 'naturmorts')
    if still_life:
        for still_l in still_life:
            photo_path = os.path.join(photo_directory,
                                      still_l.photo)  # Assuming 'photo' is the attribute representing the photo path
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {still_l.i_id}, Название: {still_l.name}, Описание: {still_l.description}, Цена: {still_l.price}"
                keyboard = kb.generate_cart(still_l.i_id)  # Assuming a function to generate the cart keyboard
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'),
                                     caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Натюрморты не найдены в каталоге")


@dp.message_handler(text='Портреты')
async def handle_show_portrets(message: types.Message):
    portret = md.Item.select().where(md.Item.category == 'portrets')
    if portret:
        for prt in portret:
            photo_path = os.path.join(photo_directory,
                                      prt.photo)  # Assuming 'photo' is the attribute representing the photo path
            with open(photo_path, 'rb') as photo_file:
                caption = f"Артикул: {prt.i_id}, Название: {prt.name}, Описание: {prt.description}, Цена: {prt.price}"
                keyboard = kb.generate_cart(prt.i_id)  # Assuming a function to generate the cart keyboard
                await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo_file, filename='photo'),
                                     caption=caption, reply_markup=keyboard)
    else:
        await message.reply("Портреты не найдены в каталоге")


# Обработка отмены
@dp.message_handler(text='Отмена', state='*')
async def cancel_add_item(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Добавление товара отменено.', reply_markup=kb.admin_panel)


# Handling the addition of a new item
@dp.message_handler(text='Добавить товар')
async def add_item_type(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await NewOrder.type.set()
        await message.answer(f'Выберите тип товара', reply_markup=kb.catalog_list)
    else:
        await message.reply('Доступ запрещен.')


# Handling the states and message handlers for adding a new item using ORM
@dp.callback_query_handler(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer(f'Напишите название', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Напишите описание')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.description)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await message.answer('Введите цену')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.price)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.answer('Пришлите фотографию')
    await NewOrder.next()


@dp.message_handler(content_types=['photo'], state=NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Save the photo to the server and store the file path in the data
        file_name = f"photo_{message.photo[-1].file_id}.jpg"
        photo_path = os.path.join(photo_directory, file_name)
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file.read())
        data['photo'] = file_name
        print(data['type'], data['name'], data['description'], data['price'], data['photo'])
        # Create a new item in the database using the provided details
        new_item = md.Item(category=data['type'], name=data['name'], description=data['description'],
                           price=data['price'], photo=data['photo'])
        new_item.save()  # Assuming 'save' is the method to save a new item to the database
    await message.answer('Товар успешно загружен!', reply_markup=kb.admin_panel)
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
