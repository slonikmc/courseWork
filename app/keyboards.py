from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Каталог').add('Корзина').add('Контакты')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
(main_admin.add('Каталог').add('Корзина').add('Контакты').add('Панель администратора'))

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар').add('Удалить товар').add('Сделать рассылку').add('В главное меню')

delete_panel = ReplyKeyboardMarkup(resize_keyboard=True)
delete_panel.add('Удалить по названию').add('Удалить по id').add('В главное меню')

catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='Пейзажи', callback_data='peizaj'),
                 InlineKeyboardButton(text='Натюрморты', callback_data='naturmorts'),
                 InlineKeyboardButton(text='Портреты', callback_data='portrets'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')