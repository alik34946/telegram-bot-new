from telebot import TeleBot
from transformers import pipeline
from flask import Flask, request

# Инициализация бота и веб-сервера
bot = TeleBot("7851619872:AAG2LzU_1LkazNs6e11x-z4Qv688VSDKz0w")
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
    bot.set_webhook(url='https://telegram-bot.onrender.com/webhook')
    app.run(host='0.0.0.0', port=5000)