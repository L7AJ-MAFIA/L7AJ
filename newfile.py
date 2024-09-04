import telebot
import requests
from flask import Flask
from threading import Thread

app = Flask('')

# توكن البوت من BotFather
TOKEN = '6173015397:AAFUai_g0yHwLHEz1YLlaPhIPJzz6Q4anlo'
bot = telebot.TeleBot(TOKEN)

# قائمة بالمستخدمين المسموح لهم باستخدام البوت
ALLOWED_USERS = [5654838744]  # ضع هنا معرفات المستخدمين المسموح لهم

# تخزين التوكنات للمستخدمين
user_tokens = {}

# دالة للتحقق من إذن المستخدم
def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS

# دالة بدء المحادثة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "عـذرا عزيزي انت لا تمـلك الإذن لإستخدام البوت. تواصل مـع المطـور 🧑🏻‍💻 @WA_JD_A")
        return

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button1 = telebot.types.InlineKeyboardButton("📱أكتب رقمك هنا", callback_data='send_phone')
    button2 = telebot.types.InlineKeyboardButton("إعادة تعبئة رصيدك بدون رمز", callback_data='update_code')
    button3 = telebot.types.InlineKeyboardButton("عرض رصيدك الحالي", callback_data='show_balance')
    keyboard.add(button1, button2, button3)

    welcome_message = f"""
♕ أهلا بك يا {message.from_user.first_name} ♕

♡ L7AJ MAFIA' ♡

♕ إختر عرضًا من هذه العروض حسب رغبتك ♕
"""
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard)

# دالة لمعالجة الرقم المدخل
def handle_number(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "عـذرا عزيزي، لا تملك الإذن لاستخدام البوت. تواصل مع المطور 🧑🏻‍💻 https://t.me/WA_JD_A")
        return

    num = message.text
    bot.send_message(message.chat.id, 'يتم التحقق من رقم هاتفك وسيتم إرسال الرمز لك 🔍')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.9.3',
    }

    data = {
        'client_id': 'ibiza-app',
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)
    
    if 'ROOGY' in response.text:
        bot.send_message(message.chat.id, 'تم إرسال رمز التحقق، قم بكتابته هنا من فضلك 📨🧾')
        bot.register_next_step_handler(message, handle_otp, num)
    else:
        bot.send_message(message.chat.id, 'حدث خطأ أثناء إرسال الرمز. يرجى إعادة المحاولة بعد دقيقتين.')

# دالة لمعالجة الكود المدخل
def handle_otp(message, num):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "عـذرا عزيزي، لا تملك الإذن لاستخدام البوت. تواصل مع المطور 🧑🏻‍💻 t.me/WA_JD_A")
        return

    otp = message.text

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp',
    }

    data = {
        'client_id': 'ibiza-app',
        'otp': otp,
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)
    access_token = response.json().get('access_token')

    if access_token:
        user_tokens[message.from_user.id] = access_token
        bot.send_message(message.chat.id, 'تم التحقق من الرمز بنجاح. يتم الآن إرسال الانترنت...')

        initial_volume = check_internet_volume(access_token)
        bot.send_message(message.chat.id, f'حجم الانترنت قبل الإرسال: {initial_volume} 🪪')

        send_internet(message, access_token)
    else:
        bot.send_message(message.chat.id, 'عذرا، هناك خطأ في التحقق من الرمز. يرجى المحاولة لاحقاً.')

# دالة للتحقق من حجم الانترنت
def check_internet_volume(access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/balance'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    volume = response.json().get('accounts', [{}])[1].get('value', 'غير متاح')
    return volume

# دالة لإرسال الانترنت
def send_internet(message, access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'request-id': 'ef69f4c6-2ead-4b93-95df-106ef37feefd',
        'flavour-type': 'gms',
        'Content-Type': 'application/json'
    }

    payload = {
        "mgmValue": "ABC"
    }

    for _ in range(10):
        response = requests.post(url, headers=headers, json=payload).text
        if 'Request Rejected' not in response:
            final_volume = check_internet_volume(access_token)
            bot.send_message(message.chat.id, f'حجم الانترنت بعد الإرسال: {final_volume}')
            break
        else:
            bot.send_message(message.chat.id, 'حدث خطأ أثناء إرسال البيانات. يرجى المحاولة مرة أخرى.')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'send_phone':
        bot.send_message(call.message.chat.id, 'أرسل رقمك من فضلك.')
        bot.register_next_step_handler(call.message, handle_number)
    elif call.data == 'update_code':
        if call.from_user.id in user_tokens:
            bot.send_message(call.message.chat.id, 'تتم التعبئة...')
            send_internet(call.message, user_tokens[call.from_user.id])
        else:
            bot.send_message(call.message.chat.id, 'رقمك غير محفوظ. قم بالتسجيل لحفظه.')
    elif call.data == 'show_balance':
        if call.from_user.id in user_tokens:
            volume = check_internet_volume(user_tokens[call.from_user.id])
            bot.send_message(call.message.chat.id, f'رصيدك الحالي: {volume}')
        else:
            bot.send_message(call.message.chat.id, 'رقمك غير محفوظ. قم بالتسجيل لحفظه.')

# بدء البوت
@app.route('/')
def home():
    return "<b>telegram @WA_JD_A</b>"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)