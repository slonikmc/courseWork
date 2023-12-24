from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Каталог').add('Корзина').add('Контакты').add('История заказов')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
(main_admin.add('Каталог').add('Корзина').add('Контакты').add('История заказов').add('Панель администратора'))

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар').add('Удалить товар').add('Сделать рассылку').add('В главное меню')

delete_panel = ReplyKeyboardMarkup(resize_keyboard=True)
delete_panel.add('Удалить по названию').add('Удалить по id').add('В главное меню')

def generate_cart(i_id):
    cart = InlineKeyboardMarkup(row_width=2)
    cart.add(InlineKeyboardButton("Добавить в корзину", callback_data=f'add_to_cart_{int(i_id)}'))
    return cart


def generate_cart_keyboard(item_id):
    cart_actions = InlineKeyboardMarkup(row_width=2)
    cart_actions.add(InlineKeyboardButton(text="Заказать", callback_data=f"order_{int(item_id)}"))
    cart_actions.add(InlineKeyboardButton(text="Удалить из корзины", callback_data=f"delete_{int(item_id)}"))
    return cart_actions


catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='Пейзажи', callback_data='peizaj'),
                 InlineKeyboardButton(text='Натюрморты', callback_data='naturmorts'),
                 InlineKeyboardButton(text='Портреты', callback_data='portrets'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')