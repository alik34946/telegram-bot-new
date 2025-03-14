from telebot import TeleBot
from transformers import pipeline
from flask import Flask, request
import os

# Инициализация бота и веб-сервера
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Загружаем модель distilgpt2
generator = pipeline('text-generation', model='distilgpt2')

# Обработчики команд
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой автономный AI. Спрашивай что угодно!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = generator(message.text, max_length=100, num_return_sequences=1)[0]['generated_text']
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "Ошибка при генерации ответа.")

# Вебхук для Render
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update:
        message = update['message']
        text = message.get('text', '')
        chat_id = message['chat']['id']
        try:
            response = generator(text, max_length=100, num_return_sequences=1)[0]['generated_text']
            bot.send_message(chat_id, response)
        except Exception as e:
            bot.send_message(chat_id, "Ошибка.")
    return {'status': 'ok'}

if __name__ == "__main__":
    # Устанавливаем вебхук для Telegram
    bot.remove_webhook()
    bot.set_webhook(url='https://telegram-bot-new-2.onrender.com/webhook')