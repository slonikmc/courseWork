import asyncio
import asyncpg
from peewee import PostgresqlDatabase


db = PostgresqlDatabase(
        user='postgres',
        password='Azaza431',
        host='localhost',
        port=5432,
        database='tg')

# Функция для установления подключения к базе данных
async def create_db_connection():
    return await asyncpg.connect(
        user='postgres',
        password='Azaza431',
        host='localhost',
        port=5432,
        database='tg'
    )



# Функция для создания всех используемых таблиц, если их нет
async def db_start():
    connection = await create_db_connection()
    # Создание таблицы accounts
    await connection.execute("CREATE TABLE IF NOT EXISTS accounts("
                            "id SERIAL PRIMARY KEY, "
                            "tg_id BIGINT NOT NULL)")

    # Создание таблицы items
    await connection.execute("CREATE TABLE IF NOT EXISTS items("
                            "i_id SERIAL PRIMARY KEY, "
                            "name TEXT, "
                            "description TEXT, "
                            "price INT, "
                            "photo TEXT, "
                            "category TEXT)")

    # Создание таблицы cart
    await connection.execute("CREATE TABLE IF NOT EXISTS cart("
                             "id SERIAL PRIMARY KEY, "
                             "user_id BIGINT NOT NULL, "
                             "item_id INT NOT NULL)")

    # Создание таблицы history
    await connection.execute("CREATE TABLE IF NOT EXISTS history("
                             "id SERIAL PRIMARY KEY, "
                             "item_id INT NOT NULL, "
                             "i_id BIGINT NOT NULL, "
                             "date DATE NOT NULL, "
                             "price INT NOT NULL)")

    # Закрытие подключения
    await connection.close()

# Добавление нового пользователя
async def cmd_start_db(user_id):
    # Установление подключения к базе данных
    connection = await create_db_connection()
    # Проверка существования пользователя в таблице
    user = await connection.fetchrow("SELECT * FROM accounts WHERE tg_id = $1", user_id)
    if not user:
        # Вставка данных в таблицу
        await connection.execute("INSERT INTO accounts (tg_id) VALUES ($1)", user_id)

    # Закрытие подключения
    await connection.close()

# Получение пути к фото по айди товара
async def get_item_photo_by_id(i_id):
    try:
        # Установление подключения к базе данных
        connection = await create_db_connection()
        # Получение фотографии по i_id
        photo = await connection.fetchval("SELECT photo FROM items WHERE i_id = $1", i_id)

        return photo
    finally:
        await connection.close()

# Получение пути к фото по названию товара
async def get_item_photo_by_name(name):
    try:
        # Установление подключения к базе данных
        connection = await create_db_connection()
        # Получение фотографии по названию
        photo = await connection.fetchval("SELECT photo FROM items WHERE name = $1", name)

        return photo

    finally:
        await connection.close()

# Добавление в таблицу товара
async def add_item(state):
    async with state.proxy() as data:
        connection = await create_db_connection()
        await connection.execute(
            "INSERT INTO items (name, description, price, photo, category) VALUES ($1, $2, $3, $4, $5)",
            data['name'], data['description'], data['price'], data['photo'], data['type']
        )
        await connection.close()

# Добавление товара в корзину
async def add_item_to_cart(tg_id, item_id):
    connection = await create_db_connection()
    # Проверка наличия существующей записи
    existing_record = await connection.fetchrow(
        "SELECT * FROM cart WHERE user_id = $1 AND item_id = $2",
        tg_id, item_id
    )
    if existing_record:
        # Если запись найдена, удаляем ее
        await connection.execute(
            "DELETE FROM cart WHERE user_id = $1 AND item_id = $2",
            tg_id, item_id
        )

    # Вставка новой записи
    await connection.execute(
        "INSERT INTO cart (user_id, item_id) VALUES ($1, $2)",
        tg_id, item_id
    )

    await connection.close()

# Удаление товара по названию
async def delete_item_by_name(name):
    connection = await create_db_connection()
    await connection.execute("DELETE FROM items WHERE name = $1", name)
    await connection.close()

# Удаление товара по id
async def delete_item_by_id(id):
    connection = await create_db_connection()
    await connection.execute("DELETE FROM items WHERE i_id = $1", id)
    await connection.close()

# Возвращает все пейзажи
async def get_landscapes():
    connection = await create_db_connection()
    try:
        # Выполнение запроса к базе данных для извлечения всех пейзажей
        landscapes = await connection.fetch("SELECT i_id, name, description, price, photo FROM items WHERE category = 'peizaj'")
        return landscapes
    finally:
        await connection.close()

# Возвращает натюрморты
async def get_still_lifes():
    connection = await create_db_connection()
    try:
        # Выполнение запроса к базе данных для извлечения всех пейзажей
        stilllifes = await connection.fetch("SELECT i_id, name, description, price, photo FROM items WHERE category = 'naturmorts'")
        return stilllifes
    finally:
        await connection.close()

# Возвращает портреты
async def get_portrets():
    connection = await create_db_connection()
    try:
        # Выполнение запроса к базе данных для извлечения всех пейзажей
        portrets = await connection.fetch(
            "SELECT i_id, name, description, price, photo FROM items WHERE category = 'portrets'")
        return portrets
    finally:
        await connection.close()

# Возвращает все товары в корзине
async def get_user_cart_items(user_id):
    try:
        connection = await create_db_connection()
        print("Успешное установление соединения с базой данных")
        query = "SELECT items.i_id, items.name, items.description, items.price, items.photo " \
                "FROM cart " \
                "JOIN items ON cart.item_id = items.i_id " \
                "WHERE cart.user_id = $1"
        items = await connection.fetch(query, user_id)
        print("Запрос к базе данных выполнен успешно")
        return items
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

# Удаляет товар item_id в корзине пользователя с user_id
async def delete_item_from_cart(user_id, item_id):
    try:
        connection = await create_db_connection()
        query = "DELETE FROM cart WHERE user_id = $1 AND item_id = $2"
        await connection.execute(query, user_id, item_id)
    finally:
        await connection.close()