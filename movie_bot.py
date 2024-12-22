import requests
import json
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Ваш API ключ от Кинопоиска
KINOPOISK_API_KEY = '7adc812c-7a98-47a5-be4d-fe9911b89828'

# Токен вашего Telegram-бота
TELEGRAM_BOT_TOKEN = '7174640207:AAFvE7D4wq36BtG4J1PrmRUH2DBw_KmeG1s'

# Базовый URL для запросов к API Кинопоиска
KINOPOISK_API_URL = 'https://kinopoiskapiunofficial.tech/api/v2.1/films'

# Функция для поиска фильма по названию
def search_movie(title):
    headers = {
        'X-API-KEY': KINOPOISK_API_KEY,
        'Content-Type': 'application/json',
    }
    params = {
        'keyword': title,
        'page': 1
    }
    response = requests.get(KINOPOISK_API_URL + '/search-by-keyword', headers=headers, params=params)
    return response.json()

# Функция для поиска фильмов по жанру
def search_movies_by_genre(genre):
    headers = {
        'X-API-KEY': KINOPOISK_API_KEY,
        'Content-Type': 'application/json',
    }
    params = {
        'genres': genre,
        'page': 1
    }
    response = requests.get(KINOPOISK_API_URL + '/search-by-filters', headers=headers, params=params)
    return response.json()

# Список заранее выбранных фильмов для каждого жанра
PRESELECTED_MOVIES = {
    'комедия': ['Мальчишник в вегасе', 'Во всё тяжкое', 'Выкрутасы', 'Ёлки 10', 'Холоп'],
    'драма': ['1+1', 'Брат', 'Зеленая миля', 'Форрест Гамп', 'Король и шут'],
    'фантастика': ['Интерстеллар', 'Аватар', 'Марсианин', 'Матрица', 'Пятый элемент'],
    'ужасы': ['Оно', 'Астрал', 'Мы', 'Тихое место', 'Синистер'],
    'боевик': ['Гнев человеческий', 'Обливион', 'Никто', 'Пчеловод', 'Вторжение'],
    'триллер': ['Пропавшая', 'Отрыв', 'Побег из претории', 'Остров фантазий', 'Счастливого дня смерти'],
    'детектив': ['Пленницы', 'Остров проклятых', 'Шерлок Холмс', 'Черный ящик', 'Достать ножи'],
    # Добавьте другие жанры и соответствующие фильмы
}

# Функция-обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот для поиска фильмов и сериалов. Напиши мне название и я найду основную информацию для тебя. Также ты можешь использовать команды /genre или /year, чтобы получить небольшую подборку фильмов по жанру или году соответственно.')

# Функция-обработчик текстовых сообщений
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title = update.message.text
    response = search_movie(title)
    
    if 'films' in response and len(response['films']) > 0:
        film = response['films'][0]
        poster_url = film['posterUrl']
        
        # Формируем сообщение с информацией о фильме
        message = f"Название: {film['nameRu']}\n" \
                  f"Год: {film['year']}\n" \
                  f"Жанр: {', '.join([genre['genre'] for genre in film['genres']])}\n" \
                  f"Страна: {', '.join([country['country'] for country in film['countries']])}\n" \
                  f"Рейтинг: {film['rating']}"
        
        # Отправляем изображение фильма
        await update.message.reply_photo(poster_url, caption=message)
    else:
        await update.message.reply_text("К сожалению, фильм не найден.")

# Функция-обработчик команды /genre
async def genre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    genre = ' '.join(context.args).lower()
    
    if genre in PRESELECTED_MOVIES:
        movie_titles = PRESELECTED_MOVIES[genre]
        movies = []
        
        for movie_title in movie_titles:
            response = search_movie(movie_title)
            if 'films' in response and len(response['films']) > 0:
                film = response['films'][0]
                poster_url = film['posterUrl']
                message = f"Название: {film['nameRu']}\n" \
                          f"Год: {film['year']}\n" \
                          f"Жанр: {', '.join([genre['genre'] for genre in film['genres']])}\n" \
                          f"Страна: {', '.join([country['country'] for country in film['countries']])}\n" \
                          f"Рейтинг: {film['rating']}"
                movies.append((poster_url, message))
        
        if movies:
            for poster_url, message in movies:
                await update.message.reply_photo(poster_url, caption=message)
        else:
            await update.message.reply_text("К сожалению, фильмы не найдены.")
    else:
        await update.message.reply_text("К сожалению, жанр не найден.")

# Функция-обработчик команды /year
async def year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем год из аргументов команды
    year_arg = ' '.join(context.args)
    
    # Проверяем, что год указан и является числом
    if not year_arg.isdigit():
        await update.message.reply_text("Пожалуйста, укажите год в формате /year <год>.")
        return
    
    year = int(year_arg)
    
    # Ищем фильмы по указанному году
    headers = {
        'X-API-KEY': KINOPOISK_API_KEY,
        'Content-Type': 'application/json',
    }
    params = {
        'yearFrom': year,
        'yearTo': year,
        'page': 1
    }
    response = requests.get(KINOPOISK_API_URL + '/search-by-filters', headers=headers, params=params)
    data = response.json()
    
    if 'films' in data and len(data['films']) > 0:
        # Выбираем первые три фильма из списка
        movies = data['films'][:3]
        
        for film in movies:
            poster_url = film['posterUrl']
            message = f"Название: {film['nameRu']}\n" \
                      f"Год: {film['year']}\n" \
                      f"Жанр: {', '.join([genre['genre'] for genre in film['genres']])}\n" \
                      f"Страна: {', '.join([country['country'] for country in film['countries']])}\n" \
                      f"Рейтинг: {film['rating']}"
            
            # Отправляем изображение и информацию о фильме
            await update.message.reply_photo(poster_url, caption=message)
    else:
        await update.message.reply_text("К сожалению, фильмы за указанный год не найдены.")

def main() -> None:
    # Создаем объект Application и передаем ему токен вашего бота
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).read_timeout(60).write_timeout(60).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик команды /genre
    application.add_handler(CommandHandler("genre", genre))

    # Регистрируем обработчик команды /year
    application.add_handler(CommandHandler("year", year))

    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()