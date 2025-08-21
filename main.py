import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler, \
    CallbackContext
from datetime import datetime
import sqlite3
import json

# Настройки
BOT_TOKEN = "8108251831:AAEQdueZ_a1mR4_3uuQCaNdGU-k6jBApWDw"
DB_NAME = "furniture_bot.db"
ITEMS_PER_PAGE = 5

# Упрощенная база данных
FURNITURE_ITEMS = {
    # ДИВАНЫ
    "Д.Амадей - накладки": 92,
    "Д.Амадей - хром": 72,
    "Д.Амадей 1,2 - все комплектации": 1094,
    "Д.Амадей 0,7 (подлокотники Сочи закругленные)": 979,
    "Д.Амадей 0,7 без подлокотников": 979,
    "Д.Амадей 1,0 б.п.": 1105,
    "Д.Амадей 1,0 с подлокотниками Сочи": 1037,
    "Д.Амадей 1,4 б.п.": 1209,
    "Д.Амадей 1,4 с подлокотниками Сочи": 1349,
    "Д.Амадей 1,6 б.п.": 1324,
    "Д.Амадей 1,6 с подлокотники Сочи": 1416,
    "Д.Амадей LUXE 0,7 без подлокотников": 863,
    "Д.Амадей LUXE 0,7 подлокотники прямоугольные": 863,
    "Д.Амадей LUXE 0,7 с накладками на опорах": 1027,
    "Д.Амадей LUXE 1,0 без подлокотников": 921,
    "Д.Амадей LUXE 1,0 подлокотники прямоугольные": 921,
    "Д.Амадей LUXE 1,0 с накладками на опорах": 1119,
    "Д.Амадей LUXE 1,2 без подлокотников": 978,
    "Д.Амадей LUXE 1,2 подлокотники прямоугольные": 978,
    "Д.Амадей LUXE 1,2 с накладками на опорах": 978,
    "Д.Амадей LUXE 1,4 без подлокотников": 1093,
    "Д.Амадей LUXE 1,4 подлокотники прямоугольные": 1093,
    "Д.Амадей LUXE 1,4 с накладками на опорах": 1257,
    "Д.Амадей LUXE 1,6 без подлокотников": 1208,
    "Д.Амадей LUXE 1,6 подлокотники прямоугольные": 1208,
    "Д.Амадей LUXE 1,6 с накладками на опорах": 1372,
    "Д.Амстердам": 1289,
    "Д.Гранд": 1350,
    "Д.Дубай 1,6": 1267,
    "Д.Дубай 1,6 с доп. секцией выкатной 0,8": 2209,
    "Д.Дубай 1,6 с подъёмной оттоманкой": 1863,
    "Д.Дубай 1,9": 1481,
    "Д.Дубай 1,9 с доп. секцией 0,95 (НПБ)": 2209,
    "Д.Мадрид ПБ/НПБ": 790,
    "Д.Мадрид ППУ": 560,
    "Д.Марсель без полок": 1327,
    "Д.Мартин": 1294,
    "Д.Мартин (с доп. секцией)": 2312,
    "Д.Монро (с бельевым ящиком)": 655,
    "Д.Монро (дельфин со спальным местом)": 655,
    "Д.Монро (угловая секция)": 410,
    "Д.Невада 1900/2000 (подлокотники 100)": 943,
    "Д.Невада 1900/2000 (подлокотники 30)": 851,
    "Д.Ника ПБ": 642,
    "Д.Ника ППУ": 442,
    "Д.Нирвана": 1180,
    "Д.Нью-Йорк (НПБ)": 1348,
    "Д.Нью-Йорк (ПБ)": 1348,
    "Д.Остин": 1293,
    "Д.Релакс выкатной": 706,
    "Релакс оттоманка": 532,
    "Релакс полукресло": 398,
    "Релакс угловая секция": 766,
    "Д.Софт 0,7": 369,
    "Д.Софт 1,2": 369,
    "Д.Фаворит": 1430,
    "Д.Фолиант": 1367,
    "Д.Эрвин ПБ/НПБ": 1081,
    "Д.Эрвин накладки ПБ/НПБ": 1173,
    "Д.Эрвин ППУ": 955,
    # КРЕСЛА и КУШЕТКИ
    "К.Амстердам (без механизма)": 731,
    "К.Козырек": 390,
    "К.Козырек LUXE": 805,
    "К.Лучик": 450,
    "К.Мартин без механизма": 920,
    "К.Прованс (ППУ+ПЗ)": 805,
    "Комплект Прованс (кресло и пуф)": 1028,
    "К.Фолиант": 708,
    "К.Эрвин без механизма ПБ/НПБ": 538,
    "К.Эрвин без механизма ППУ": 480,
    "К.Эрвин ПБ/НПБ - 1,2": 1140,
    "К.Эрвин ППУ - 0,7": 686,
    "К.Эрвин ППУ - 1,2": 910,
    "К.Эрвин 1,0 НПБ": 1040,
    "К.Эрвин 1,0 ППУ": 845,
    "Кушетка Сверчок ППУ": 400,
    # МОДУЛИ (М.У.)
    "М.У.Амстердам": 1663,
    "М.У.Престиж НПБ": 2692,
    "М.У.Фаворит": 1995,
    "М.У.Фаворит - оттоманка": 565,
    "М.У.Эрвин НПБ": 1513,
    "К.У.Монро (дельфин со спальным местом)": 1555,
    "К.У.Мonро (с бельевым коробом)": 1555,
    # ТРАНСФОРМЕРЫ (Т.)
    "Т.Кузнечик": 308,
    "Т.Совенок - ППУ": 558,
    "Т.Совенок универсальный НПБ": 820,
    "Т.Совенок универсальный ППУ": 570,
    "Т.Соня вык. ППУ": 989,
    "Т.Соня одн. НПБ": 874,
    "Т.Софи дельфин (выкатная) ПБ/НПБ": 1243,
    "Т.Софи дельфин (выкатная) ППУ": 989,
    "Т.Софи ПБ/НПБ - 1900*1000 / 2000*1000": 945,
    "Т.Софи ПБ/НПБ - 1900*1200 / 2000*1200": 995,
    "Т.Софи ПБ/НПБ - 1900*800 / 2000*800 / 1900*900 / 2000*900": 895,
    "Т.Софи ППУ - 1900*1000 / 2000*1000": 813,
    "Т.Софи ППУ - 1900*1200 / 2000*1200": 763,
    "Т.Софи ППУ - 1900*800 / 2000*800 / 1900*900 / 2000*900": 763,
    # ДЕТСКИЕ КРОВАТИ
    "Детская кровать": 1100,
    "Детская кровать - бортик": 70,
    "Детская кровать - Комплект(без матраса)": 1170,
    "Детская кровать - матрас": 250,
    "Детская кровать - подушка думка": 17,
    "Детская кровать Ариэль без матрасов и бортика": 790,
    "Детская кровать Ариэль с 2 матрасами и бортиком": 1050,
    "Детская кровать Ариэль с матрасом и бортиком": 950,
    "Кровать Ассоль": 555,
    "Кровать Бемби": 625,
    "Совенок НПБ": 805,
    "Симба": 500,
    # БАНКЕТКИ, ПУФЫ, ОТТОМАНКИ
    "Банкетка Виктория 1,2": 230,
    "Банкетка Виктория 1,4": 240,
    "Банкетка Виктория 1,6": 250,
    "Пуф Комплимент": 68,
    "Пуф Норка": 143,
    "Пуф Прованс": 223,
    "Пуф Фолиант": 183,
    # ПОДУШКИ
    "Подушка (5) думка": 23,
    "Подушка Дубай тип Мадрид": 35,
    "Подушка думка (заказная)": 17,
    "Подушка Мадрид": 30,
    # ЗАПЧАСТИ И АКСЕССУАРЫ
    "Д.Монро - подлокотник": 57,
    "ЗП для Д.Сочи": 100,
    "Мартин доп. секция": 695,
    # УСЛУГИ
    "Изготовление пуговицы": 9,
    "Рекламация - 1ч": 400,
    "Рекламация - 30мин": 200,
    "Установка USB розетки": 58,
    "Установка второго подлокотника Софи": 95,
    "Установка накладки на подлокотник(2х)": 92
}

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.init_db()

    def init_db(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS work_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_name TEXT,
                    price INTEGER,
                    quantity INTEGER DEFAULT 1,
                    work_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def add_work_record(self, user_id, item_name, quantity=1):
        if item_name in FURNITURE_ITEMS:
            price = FURNITURE_ITEMS[item_name] * quantity
            work_date = datetime.now().strftime("%Y-%m-%d")

            with sqlite3.connect(DB_NAME) as conn:
                conn.execute(
                    'INSERT INTO work_records (user_id, item_name, price, quantity, work_date) VALUES (?, ?, ?, ?, ?)',
                    (user_id, item_name, price, quantity, work_date)
                )
            return price
        return 0

    def get_day_stats(self, user_id, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute('''
                SELECT item_name, SUM(quantity), SUM(price) 
                FROM work_records 
                WHERE user_id = ? AND work_date = ?
                GROUP BY item_name
                ORDER BY SUM(price) DESC
            ''', (user_id, date))

            results = cursor.fetchall()
            total = sum(row[2] for row in results) if results else 0

        display_date = datetime.now().strftime("%d.%m.%Y")
        return results, total, display_date

    def clear_day(self, user_id, date):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute(
                "DELETE FROM work_records WHERE user_id = ? AND work_date = ?",
                (user_id, date)
            )
            return cursor.rowcount


db = Database()


def get_current_date():
    return datetime.now().strftime("%d.%m.%Y")


def find_matching_items(text):
    text = text.lower()
    return [item for item in FURNITURE_ITEMS.keys() if text in item.lower()]


def get_items_page(items, page=1):
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    return items[start_idx:end_idx], len(items), page


def create_callback_data(action, data):
    """Создает короткий callback_data"""
    return f"{action}:{data}"


def parse_callback_data(callback_data):
    """Парсит callback_data"""
    if ":" in callback_data:
        return callback_data.split(":", 1)
    return callback_data, ""


def create_pagination_keyboard(total_items, current_page, search_query=""):
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    keyboard = []

    # Кнопки навигации
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад",
                                                callback_data=create_callback_data("page",
                                                                                   f"{current_page - 1}_{search_query}")))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️",
                                                callback_data=create_callback_data("page",
                                                                                   f"{current_page + 1}_{search_query}")))

    if nav_buttons:
        keyboard.append(nav_buttons)

    # Добавляем кнопки выбора моделей
    matching_items = find_matching_items(search_query)
    items_page, _, _ = get_items_page(matching_items, current_page)

    for item in items_page:
        # Используем короткий идентификатор вместо полного названия
        item_id = str(list(FURNITURE_ITEMS.keys()).index(item))
        keyboard.append([InlineKeyboardButton(f"✅ {item}",
                                              callback_data=create_callback_data("select", item_id))])

    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


async def show_main_keyboard(update: Update, text=None):
    keyboard = [
        ['➕ Добавить работу', '📋 Список моделей'],
        ['📊 Сегодня', '🏁 Конец дня'],
        ['❌ Очистить сегодня']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    message = text or "Выберите действие:"
    await update.message.reply_text(message, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await show_main_keyboard(update, f"Привет, {user.first_name}! 👋\nРаботаем за {get_current_date()}?")


async def handle_model_selection(update: Update, item_name):
    user_id = update.effective_user.id
    price = db.add_work_record(user_id, item_name, 1)
    records, total, display_date = db.get_day_stats(user_id)

    await update.message.reply_text(
        f"✅ Добавлено: {item_name}\n"
        f"💰 Стоимость: {price} руб.\n"
        f"📊 За сегодня: {total} руб."
    )
    await show_main_keyboard(update)


async def handle_stop_command(update: Update):
    await update.message.reply_text("🔄 Возвращаемся в меню")
    await show_main_keyboard(update)


async def show_search_results(update: Update, search_query, page=1):
    matching_items = find_matching_items(search_query)

    if not matching_items:
        await update.message.reply_text("❌ Модели не найдены. Попробуйте другой запрос.")
        await show_main_keyboard(update)
        return

    items_page, total_items, current_page = get_items_page(matching_items, page)

    message = f"🔍 Найдено моделей: {total_items}\n"
    message += f"📄 Страница {current_page}/{(total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE}\n\n"

    for i, item in enumerate(items_page, 1):
        message += f"{i}. {item} - {FURNITURE_ITEMS[item]} руб.\n"

    keyboard = create_pagination_keyboard(total_items, current_page, search_query)
    await update.message.reply_text(message, reply_markup=keyboard)


async def show_categories(update: Update):
    message = "📋 Доступные модели:\n\n"
    for item, price in FURNITURE_ITEMS.items():
        message += f"• {item} - {price} руб.\n"

    message += "\n🔍 Введите часть названия модели для поиска"
    await update.message.reply_text(message)
    await show_main_keyboard(update)


async def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == "cancel":
        await query.message.delete()
        await show_main_keyboard(update)
        return

    action, data = parse_callback_data(callback_data)

    if action == "select":
        # Выбор модели по ID
        try:
            item_id = int(data)
            item_name = list(FURNITURE_ITEMS.keys())[item_id]
            await query.message.delete()
            await handle_model_selection(update, item_name)
        except (ValueError, IndexError):
            await query.message.edit_text("❌ Ошибка выбора модели")

    elif action == "page":
        # Пагинация
        parts = data.split("_")
        page = int(parts[0])
        search_query = "_".join(parts[1:]) if len(parts) > 1 else ""

        matching_items = find_matching_items(search_query)
        items_page, total_items, current_page = get_items_page(matching_items, page)

        message = f"🔍 Найдено моделей: {total_items}\n"
        message += f"📄 Страница {current_page}/{(total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE}\n\n"

        for i, item in enumerate(items_page, 1):
            message += f"{i}. {item} - {FURNITURE_ITEMS[item]} руб.\n"

        keyboard = create_pagination_keyboard(total_items, current_page, search_query)
        await query.message.edit_text(message, reply_markup=keyboard)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id

    if user_text.upper() == 'СТОП':
        await handle_stop_command(update)
        return

    if user_text == '📊 Сегодня':
        records, total, display_date = db.get_day_stats(user_id)
        if not records:
            await update.message.reply_text("📅 Сегодня нет записей")
        else:
            message = f"📅 Заработок за {display_date}:\n\n"
            for item, quantity, price in records:
                message += f"• {item} x{quantity}: {price} руб.\n"
            message += f"\n💰 Итого: {total} руб."
            await update.message.reply_text(message)
        await show_main_keyboard(update)
        return

    elif user_text == '➕ Добавить работу':
        await update.message.reply_text(
            "Введите название модели:\n(например: 'эрвин', 'амадей', 'пуф')\n\nДля отмены: СТОП"
        )
        return

    elif user_text == '📋 Список моделей':
        await show_categories(update)
        return

    elif user_text == '❌ Очистить сегодня':
        deleted = db.clear_day(user_id, datetime.now().strftime("%Y-%m-%d"))
        await update.message.reply_text(f"🗑️ Удалено записей: {deleted}")
        await show_main_keyboard(update)
        return

    elif user_text == '🏁 Конец дня':
        records, total, display_date = db.get_day_stats(user_id)
        if not records:
            await update.message.reply_text("📅 Сегодня работ не было")
        else:
            message = f"🏁 Итоги дня {display_date}:\n\n"
            for item, quantity, price in records:
                message += f"• {item} x{quantity}: {price} руб.\n"
            message += f"\n💰 ИТОГО: {total} руб.\n"
            message += "🎉 Хорошая работа!"
            await update.message.reply_text(message)
        await show_main_keyboard(update)
        return

    elif user_text in FURNITURE_ITEMS:
        await handle_model_selection(update, user_text)
        return

    # Поиск модели
    await show_search_results(update, user_text)


def main():
    print(f"Бот запущен с {len(FURNITURE_ITEMS)} моделями")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    print("Бот готов к работе...")
    application.run_polling()


if __name__ == "__main__":
    main()
