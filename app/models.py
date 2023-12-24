from peewee import *
from app.database import *
import asyncio

class BaseModel(Model):
    class Meta:
        database = db

class Account(BaseModel):
    id = AutoField
    tg_id = BigIntegerField(unique=True)

    class Meta:
        table_name = 'accounts'

class Item(BaseModel):
    i_id = AutoField()
    name = CharField()
    description = TextField()
    price = CharField()
    photo = CharField()
    category = CharField()

    class Meta:
        table_name = 'items'

class Cart(BaseModel):
    id = AutoField()
    user_id = BigIntegerField()
    item_id = IntegerField()

    class Meta:
        table_name = 'cart'

class History(BaseModel):
    id = AutoField()
    item_id = IntegerField()
    i_id = BigIntegerField()
    date = DateField()
    price = IntegerField()

    class Meta:
        table_name = 'history'
        database = db  # Set the database attribute on the History model
async def setup_database():
    db = await create_db_connection()
    await db.connect()
    await db.create_tables([Item, History, Cart, Account])

loop = asyncio.get_event_loop()
loop.run_until_complete(db_start())




