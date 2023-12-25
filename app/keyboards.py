from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

# Клавиатура для обычного пользователя
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Каталог').add('Корзина').add('Контакты').add('История заказов')

# Клавиатура администратора
main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
(main_admin.add('Каталог').add('Корзина').add('Контакты').add('История заказов').add('Панель администратора'))

# Панель администратора
admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар').add('Удалить товар').add('Сделать выгрузку данных').add('Выполнить backup').add('В главное меню')

# Панель для удаления товара
delete_panel = ReplyKeyboardMarkup(resize_keyboard=True)
delete_panel.add('Удалить по названию').add('Удалить по id').add('В главное меню')

# Генерация кнопки 'Добавить в корзину' для конкретного товара
def generate_cart(i_id):
    cart = InlineKeyboardMarkup(row_width=2)
    cart.add(InlineKeyboardButton("Добавить в корзину", callback_data=f'add_to_cart_{int(i_id)}'))
    return cart


# Генерация клавиатуры для взаимодействия с конкретным товаром в корзине
def generate_cart_keyboard(item_id):
    cart_actions = InlineKeyboardMarkup(row_width=2)
    cart_actions.add(InlineKeyboardButton(text="Заказать", callback_data=f"order_{int(item_id)}"))
    cart_actions.add(InlineKeyboardButton(text="Удалить из корзины", callback_data=f"delete_{int(item_id)}"))
    return cart_actions

# Клавиатура для каталога
catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='Пейзажи', callback_data='peizaj'),
                 InlineKeyboardButton(text='Натюрморты', callback_data='naturmorts'),
                 InlineKeyboardButton(text='Портреты', callback_data='portrets'))

# Кнопка отмены
cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')