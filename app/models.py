from peewee import *
from app.database import *
import asyncio

# Базовая модель
class BaseModel(Model):
    class Meta:
        database = db

# ORM связана с таблицей accounts
class Account(BaseModel):
    id = AutoField
    tg_id = BigIntegerField(unique=True)

    class Meta:
        table_name = 'accounts'

# ORM связана с таблицей items
class Item(BaseModel):
    i_id = AutoField()
    name = CharField()
    description = TextField()
    price = IntegerField()
    photo = CharField()
    category = CharField()

    class Meta:
        table_name = 'items'

# ORM связана с таблицей cart
class Cart(BaseModel):
    id = AutoField()
    user_id = BigIntegerField()
    item_id = IntegerField()

    class Meta:
        table_name = 'cart'

# ORM связана с таблицей history
class History(BaseModel):
    id = AutoField()
    item_id = IntegerField()
    i_id = BigIntegerField()
    date = DateField()
    price = IntegerField()

    class Meta:
        table_name = 'history'
        database = db

# Соединение с базой данных и подключение к ней
async def setup_database():
    db = await create_db_connection()
    await db.connect()
    await db.create_tables([Item, History, Cart, Account])

# инициализация основного цикла событий
loop = asyncio.get_event_loop()
loop.run_until_complete(db_start())




