
import logging
import random
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import os
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, CallbackContext
import json

os.system('cls' if os.name == 'nt' else 'clear')

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на токен вашего бота
TELEGRAM_BOT_TOKEN = '8149689117:AAEfa2HVNtZjPWNUVl6z6_BJTiwOo4AFsYU'

# Настройка логирования (для отладки)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return random.choice(USER_AGENTS)

def is_valid_value(value):
    return not re.match(r'^[a-f0-9]{32,}$', value.strip())

def extract_emails(text):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    emails = [email for email in emails if "email protected" not in email.lower()]
    return list(set(emails))

def search_info(query):
    query_encoded = quote_plus(query)
    headers = {'User-Agent': get_random_user_agent()}
    reveng_url = f'https://reveng.ee/search?q={query_encoded}&per_page=100'
    results = []
    try:
        reveng_response = requests.get(reveng_url, headers=headers, timeout=10)
        reveng_response.raise_for_status()
        soup = BeautifulSoup(reveng_response.text, 'html.parser')
        for link in set(a['href'] for a in soup.find_all('a', href=True) if 'entity' in a['href']):
            time.sleep(0.5)  # Add a small delay
            page_response = requests.get(f'https://reveng.ee{link}', headers=headers, timeout=10)
            page_response.raise_for_status()
            soup = BeautifulSoup(page_response.text, 'html.parser')
            entity = soup.find('div', class_='bg-body rounded shadow-sm p-3 mb-2 entity-info')
            if entity:
                result = {'База данных': 'Mystery Project | DataBase'}
                name = entity.find('span', class_='entity-prop-value')
                if name:
                    result['Имя'] = name.get_text(strip=True)
                emails = extract_emails(page_response.text)
                if emails:
                    result['E-mail'] = ", ".join(emails)
                for row in entity.find_all('tr', class_='property-row'):
                    prop_name = row.find('td', class_='property-name').get_text(strip=True)
                    prop_value = row.find('td', class_='property-values').get_text(strip=True)
                    if is_valid_value(prop_value):
                        result[prop_name] = prop_value
                results.append(result)
    except requests.exceptions.RequestException as e:
        return f"Ошибка при выполнении запроса: {e}\nПопробуйте использовать VPN либо попробуйте снова."
    except Exception as e:
        return f"Неизвестная ошибка: {e}"
    return results

def format_results(results, duration):
    if not results:
        return f"Информация не найдена\nПоиск занял: {duration:.2f} секунд"
    formatted_text = f"Информация найдена\nПоиск занял: {duration:.2f} секунд\n\n"
    for result in results:
        formatted_text += f"База данных: {result['База данных']}\n"
        for key, value in result.items():
            if key != 'База данных':
                formatted_text += f"   {key}: {value}\n"
        formatted_text += "\n"
    return formatted_text

# Обработчики команд
def start(update: Update, context: CallbackContext):
    keyboard = [['Поиск']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Нажмите на кнопку 'Поиск', чтобы начать.", reply_markup=reply_markup)

def search_command(update: Update, context: CallbackContext):
    update.message.reply_text("Введите запрос для поиска:")
    return "waiting_for_query"

def handle_query(update: Update, context: CallbackContext):
    query = update.message.text
    if not query.strip():
        update.message.reply_text("Пожалуйста, введите корректные данные.")
        return

    update.message.reply_text("Поиск... Пожалуйста, подождите.")
    start_time = time.time()
    results = search_info(query)
    duration = time.time() - start_time

    if isinstance(results, str): # Check if an error occurred
        update.message.reply_text(results)
    else:
        formatted_result = format_results(results, duration)
        update.message.reply_text(formatted_result)
    return "default"

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Неизвестная команда. Пожалуйста, попробуйте снова.")

def main_bot():
    bot = Bot(TELEGRAM_BOT_TOKEN)
    dispatcher = Dispatcher(bot, None, use_context=True)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(None, unknown))  # Обработчик для неизвестных команд

    # States for conversation
    states = {
       "default":0,
       "waiting_for_query":1
    }
    current_state = "default"
    # Start polling
    while True:
      try:
        updates = bot.get_updates(timeout=30)
        if updates:
          for update in updates:
            if update.message and update.message.text == "Поиск" and current_state == "default":
               current_state = search_command(update, None)
            elif update.message and current_state == "waiting_for_query":
              current_state = handle_query(update, None)
            else:
              dispatcher.process_update(update)
      except Exception as e:
        logger.error(f"Error during update processing: {e}")
        time.sleep(5)


if __name__ == "__main__":
    main_bot()
