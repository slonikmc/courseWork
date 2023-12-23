import asyncpg

# Подключение к базе данных

# Функция для установления подключения к базе данных
async def create_db_connection():
    return await asyncpg.connect(
        user='postgres',
        password='Azaza431',
        host='localhost',
        port=5432,
        database='tg'
    )
async def db_start():
    connection = await create_db_connection()
    # Создание таблицы accounts
    await connection.execute("CREATE TABLE IF NOT EXISTS accounts("
                            "id SERIAL PRIMARY KEY, "
                            "tg_id INTEGER, "
                            "cart_id TEXT)")

    # Создание таблицы items
    await connection.execute("CREATE TABLE IF NOT EXISTS items("
                            "i_id SERIAL PRIMARY KEY, "
                            "name TEXT, "
                            "description TEXT, "
                            "price TEXT, "
                            "photo TEXT, "
                            "category TEXT)")

    # Закрытие подключения
    await connection.close()

async def cmd_start_db(user_id):
    # Установление подключения к базе данных
    connection = await create_db_connection()
    # Проверка существования пользователя в таблице
    user = await connection.fetchrow("SELECT * FROM accounts WHERE tg_id = $1", user_id)
    if not user:
        # Вставка данных в таблицу с использованием параметризированного запроса
        await connection.execute("INSERT INTO accounts (tg_id) VALUES ($1)", user_id)

    # Закрытие подключения
    await connection.close()

async def get_item_photo_by_id(i_id):
    try:
        # Установление подключения к базе данных
        connection = await create_db_connection()
        # Получение фотографии по i_id
        photo = await connection.fetchval("SELECT photo FROM items WHERE i_id = $1", i_id)
        # Закрытие подключения
        return photo
    finally:
        await connection.close()


async def get_item_photo_by_name(name):
    try:
        # Установление подключения к базе данных
        connection = await create_db_connection()
        # Получение фотографии по названию
        photo = await connection.fetchval("SELECT photo FROM items WHERE name = $1", name)
        # Закрытие подключения
        if photo is not None:
            return photo
        else:
            return None  # Возвращаем None, если название товара не найдено
    finally:
        await connection.close()


async def add_item(state):
    async with state.proxy() as data:
        connection = await create_db_connection()
        await connection.execute(
            "INSERT INTO items (name, description, price, photo, category) VALUES ($1, $2, $3, $4, $5)",
            data['name'], data['description'], data['price'], data['photo'], data['type']
        )
        await connection.close()

async def delete_item_by_name(name):
    connection = await create_db_connection()
    await connection.execute("DELETE FROM items WHERE name = $1", name)
    await connection.close()

async def delete_item_by_id(id):
    connection = await create_db_connection()
    await connection.execute("DELETE FROM items WHERE i_id = $1", id)
    await connection.close()
async def get_landscapes():
    connection = await create_db_connection()
    try:
        # Выполнение запроса к базе данных для извлечения всех пейзажей
        landscapes = await connection.fetch("SELECT i_id, name, description, price, photo FROM items WHERE category = 'peizaj'")
        return landscapes
    finally:
        await connection.close()

async def get_still_lifes():
    connection = await create_db_connection()
    try:
        # Выполнение запроса к базе данных для извлечения всех пейзажей
        stilllifes = await connection.fetch("SELECT i_id, name, description, price, photo FROM items WHERE category = 'naturmorts'")
        return stilllifes
    finally:
        await connection.close()

async def get_portrets():
    connection = await create_db_connection()
    try:
        # Выполнение запроса к базе данных для извлечения всех пейзажей
        portrets = await connection.fetch(
            "SELECT i_id, name, description, price, photo FROM items WHERE category = 'portrets'")
        return portrets
    finally:
        await connection.close()
