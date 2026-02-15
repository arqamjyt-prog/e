import telebot
import requests
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import io
import time
import hashlib
import sys
import logging
from flask import Flask
import os
import threading

# إخفاء جميع التحذيرات والرسائل
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('telebot').setLevel(logging.CRITICAL)
logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

# تعطيل طباعة stdout و stderr
class SilentOutput:
    def write(self, text):
        pass
    def flush(self):
        pass

sys.stdout = SilentOutput()
sys.stderr = SilentOutput()

BOT_TOKEN = "8535425056:AAEVNBjgq5tfeMfcLNLf9wCr-DJ7dlFEXrg"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== FORCED SUBSCRIPTION ==================
CHANNEL_ID = -1003735672225
CHANNEL_LINK = "https://t.me/+EiI2wMtaru9hZTAy"
GROUP_ID = -1003757848848
GROUP_LINK = "https://t.me/+2fbbsgcF5ao2ZWNi"

# ================== DATA STORAGE ==================
used_numbers_pool = {}
all_numbers_cache = {}
USER_LANG = {}
USER_CHECKED = {}

# ================== DATA ==================
DATA = {
    "🇧🇾 Belarus": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/belarus%20WS.txt"
    },
    "🇪🇬 Egypt": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/egypt%20WS.txt"
    },
    "🇳🇵 Nepal": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/nepal%20WS.txt"
    },
    "🇲🇿 Mozambique": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/mozabique%20WS.txt"
    },
    "🇾🇪 Yemen": {
        "WS1": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen%20WS.txt",
        "WS2": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen2%20WS.txt",
        "WS3": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen3%20WS.txt",
        "WS4": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen4%20Ws.txt",
        "WS5": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen5%20WS.txt",
        "WS6": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen6%20WS.txt",
        "WS7": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/yemen7%20WS.txt"
    },
    "🇲🇬 Madagascar": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/madagascar%20WS.txt"
    },
    "🇿🇼 Zimbabwe": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/zimbabwe%20WS.txt"
    },
    "🇮🇶 Iraq": {
        "WS1": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/iraq%20WS.txt",
        "WS2": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/iraq2%20WS.txt",
        "WS3": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/iraq3%20WS.txt"
    },
    "🇺🇦 Ukraine": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/ukraine%20WS.txt"
    },
    "🇸🇦 Saudi Arabia": {
        "WS1": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/saudi%20WS.txt",
        "WS2": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/saudi2%20WS.txt"
    },
    "🇰🇪 Kenya": {
        "TG": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/kenya%20TG.txt"
    },
    "🇩🇿 Algeria": {
        "WS1": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/algeria%20WS.txt",
        "WS2": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/algeria2%20WS.txt"
    },
    "🇰🇼 Kuwait": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/kuwait%20WS.txt",
        "TG": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/kuwait2%20TG.txt"
    },
    "🇮🇷 Iran": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/iran%20WS.txt"
    },
    "🇶🇦 Qatar": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/qatar%20WS.txt"
    },
    "🇦🇫 Afghanistan": {
        "WS": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/afghanistan%20WS.txt"
    },
    "🇦🇿 Azerbaijan": {
        "TMV": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/azerbijan%20tmv.txt",
        "TG": "https://huggingface.co/spaces/otdqcs/vakhvsl/raw/main/azerbijan2%20TG.txt"
    }
}

# ================== LANGUAGES ==================
LANGS = {"ar": "🇸🇦 العربية", "en": "🇺🇸 English"}

MESSAGES = {
    "ar": {
        "choose_lang": "🌐 اختر اللغة:",
        "choose_country": "🌍 اختر الدولة:",
        "choose_server": "🖥 اختر السيرفر:",
        "no_numbers": "❌ لا يوجد أرقام",
        "file_created": "✅ تم إنشاء ملف 20 رقم مختلف",
        "change_lang": "🌐 تغيير اللغة",
        "refresh": "🔄 رقم جديد",
        "create_file": "📄 ملف 20 رقم",
        "request_code": "🔑 طلب الكود",
        "telegram_bot": "🤖 بوت تلجرام",
        "contact_dev": "📞 تواصل مع المطور",
        "must_join": "❌ عذراً، يجب عليك الاشتراك في القناة والمجموعة أولاً لاستخدام البوت.\n\n📢 يرجى الانضمام ثم الضغط على زر 'تحقق'.",
        "check_btn": "✅ تحقق",
        "join_channel": "📢 انضم للقناة",
        "join_group": "👥 انضم للمجموعة",
        "welcome": "👋 مرحباً بك في البوت!",
        "all_numbers_shown": "🔄 تم عرض جميع الأرقام، سيتم إعادة تعيين القائمة",
        "total_countries": "إجمالي الدول: {count} دولة",
        "total_servers": "إجمالي السيرفرات: {count} سيرفر"
    },
    "en": {
        "choose_lang": "🌐 Choose language:",
        "choose_country": "🌍 Choose country:",
        "choose_server": "🖥 Choose server:",
        "no_numbers": "❌ No numbers available",
        "file_created": "✅ 20 different numbers file created",
        "change_lang": "🌐 Change language",
        "refresh": "🔄 New number",
        "create_file": "📄 20 numbers file",
        "request_code": "🔑 Request code",
        "telegram_bot": "🤖 Telegram Bot",
        "contact_dev": "📞 Contact Developer",
        "must_join": "❌ Sorry, you must join the channel and group first to use the bot.\n\n📢 Please join and then click the 'Check' button.",
        "check_btn": "✅ Check",
        "join_channel": "📢 Join Channel",
        "join_group": "👥 Join Group",
        "welcome": "👋 Welcome to the bot!",
        "all_numbers_shown": "🔄 All numbers have been shown, resetting list",
        "total_countries": "Total countries: {count}",
        "total_servers": "Total servers: {count}"
    }
}

# ================== HELPERS ==================
def get_all_numbers(url):
    if url in all_numbers_cache:
        return all_numbers_cache[url].copy()
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        numbers = [l.strip() for l in r.text.splitlines() if l.strip()]
        all_numbers_cache[url] = numbers
        return numbers.copy()
    except Exception:
        return []

def generate_unique_id(length=4):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_unique_number(chat_id, country, server):
    key = (chat_id, country, server)
    url = DATA[country][server]
    
    all_numbers = get_all_numbers(url)
    if not all_numbers:
        return None, False
    
    if key not in used_numbers_pool:
        used_numbers_pool[key] = []
    
    available_numbers = [n for n in all_numbers if n not in used_numbers_pool[key]]
    
    if not available_numbers:
        used_numbers_pool[key] = []
        available_numbers = all_numbers.copy()
        was_reset = True
    else:
        was_reset = False
    
    chosen = random.choice(available_numbers)
    used_numbers_pool[key].append(chosen)
    
    return chosen, was_reset

def get_file_numbers(url, count=20):
    all_numbers = get_all_numbers(url)
    if not all_numbers:
        return []
    
    if len(all_numbers) <= count:
        return all_numbers.copy()
    
    return random.sample(all_numbers, count)

def create_unique_filename(country, server):
    unique_id = generate_unique_id(4)
    clean_country = country.replace(' ', '_').replace('🇧🇾', 'Belarus').replace('🇪🇬', 'Egypt').replace('🇳🇵', 'Nepal').replace('🇲🇿', 'Mozambique').replace('🇾🇪', 'Yemen').replace('🇲🇬', 'Madagascar').replace('🇿🇼', 'Zimbabwe').replace('🇮🇶', 'Iraq').replace('🇺🇦', 'Ukraine').replace('🇸🇦', 'Saudi_Arabia').replace('🇰🇪', 'Kenya').replace('🇩🇿', 'Algeria').replace('🇰🇼', 'Kuwait').replace('🇮🇷', 'Iran').replace('🇶🇦', 'Qatar').replace('🇦🇫', 'Afghanistan').replace('🇦🇿', 'Azerbaijan')
    clean_server = server.replace(' ', '_')
    return f"{clean_country}_{clean_server}_{unique_id}.txt"

def buttons_two_per_row(lst, prefix):
    kb = InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(lst), 2):
        if i + 1 < len(lst):
            kb.add(
                InlineKeyboardButton(lst[i], callback_data=f"{prefix}|{lst[i]}"),
                InlineKeyboardButton(lst[i+1], callback_data=f"{prefix}|{lst[i+1]}")
            )
        else:
            kb.add(InlineKeyboardButton(lst[i], callback_data=f"{prefix}|{lst[i]}"))
    return kb

def number_keyboard(country, server, lang):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(MESSAGES[lang]["refresh"], callback_data=f"refresh|{country}|{server}"))
    kb.add(InlineKeyboardButton(MESSAGES[lang]["create_file"], callback_data=f"file|{country}|{server}"))
    kb.add(InlineKeyboardButton(MESSAGES[lang]["request_code"], url=GROUP_LINK))
    return kb

def get_stats(lang):
    total_countries = len(DATA)
    total_servers = sum(len(servers) for servers in DATA.values())
    return MESSAGES[lang]["total_countries"].format(count=total_countries) + "\n" + MESSAGES[lang]["total_servers"].format(count=total_servers)

# ================== SUBSCRIPTION CHECK ==================
def is_user_member(user_id):
    try:
        channel_status = bot.get_chat_member(CHANNEL_ID, user_id).status
        group_status = bot.get_chat_member(GROUP_ID, user_id).status
        member_statuses = ['member', 'administrator', 'creator']
        return channel_status in member_statuses and group_status in member_statuses
    except Exception:
        return False

def subscription_keyboard(lang):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(MESSAGES[lang]["join_channel"], url=CHANNEL_LINK),
        InlineKeyboardButton(MESSAGES[lang]["join_group"], url=GROUP_LINK),
        InlineKeyboardButton(MESSAGES[lang]["check_btn"], callback_data="check_subscription")
    )
    return kb

# ================== HANDLERS ==================
@bot.message_handler(commands=["start"])
def start_command(msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    
    if is_user_member(user_id):
        kb = InlineKeyboardMarkup()
        for code, name in LANGS.items():
            kb.add(InlineKeyboardButton(name, callback_data=f"lang_direct|{code}"))
        bot.send_message(chat_id, "🌐 Choose language / اختر اللغة:", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup()
        for code, name in LANGS.items():
            kb.add(InlineKeyboardButton(name, callback_data=f"lang_first|{code}"))
        bot.send_message(chat_id, "🌐 Choose language / اختر اللغة:", reply_markup=kb)

@bot.message_handler(commands=["mmss"])
def stats_command(msg):
    chat_id = msg.chat.id
    lang = USER_LANG.get(chat_id, "ar")
    stats = get_stats(lang)
    bot.send_message(chat_id, f"📊 **إحصائيات البوت**\n\n{stats}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_direct|"))
def language_direct(call):
    chat_id = call.message.chat.id
    lang = call.data.split("|")[1]
    USER_LANG[chat_id] = lang
    bot.delete_message(chat_id, call.message.message_id)
    show_countries(chat_id, lang)

@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_first|"))
def language_first(call):
    chat_id = call.message.chat.id
    lang = call.data.split("|")[1]
    USER_LANG[chat_id] = lang
    bot.edit_message_text(
        MESSAGES[lang]["must_join"],
        chat_id,
        call.message.message_id,
        reply_markup=subscription_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_subscription")
def check_subscription_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    lang = USER_LANG.get(chat_id, "ar")

    if is_user_member(user_id):
        bot.delete_message(chat_id, call.message.message_id)
        show_countries(chat_id, lang)
        bot.answer_callback_query(call.id, "✅ تم التحقق بنجاح!")
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم الاشتراك بعد. يرجى الانضمام إلى القناة والمجموعة ثم الضغط على تحقق.", show_alert=True)

def show_countries(chat_id, lang):
    countries = list(DATA.keys())
    kb = buttons_two_per_row(countries, "country")
    kb.add(
        InlineKeyboardButton(MESSAGES[lang]["change_lang"], callback_data="change_lang"),
        InlineKeyboardButton(MESSAGES[lang]["telegram_bot"], url="https://t.me/Almunharif13bot"),
        InlineKeyboardButton(MESSAGES[lang]["contact_dev"], url="https://t.me/VlP_12")
    )
    stats = get_stats(lang)
    bot.send_message(chat_id, f"{MESSAGES[lang]['choose_country']}\n\n{stats}", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("country|"))
def choose_country(call):
    chat_id = call.message.chat.id
    lang = USER_LANG.get(chat_id, "en")
    country = call.data.split("|")[1]
    kb = InlineKeyboardMarkup(row_width=1)
    for server in DATA[country]:
        kb.add(InlineKeyboardButton(server, callback_data=f"server|{country}|{server}"))
    bot.edit_message_text(
        f"{MESSAGES[lang]['choose_server']}\n\n🌍 {country}",
        chat_id, 
        call.message.message_id, 
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("server|"))
def choose_server(call):
    chat_id = call.message.chat.id
    lang = USER_LANG.get(chat_id, "en")
    _, country, server = call.data.split("|")
    
    number, was_reset = get_unique_number(chat_id, country, server)
    
    if not number:
        bot.answer_callback_query(call.id, MESSAGES[lang]["no_numbers"])
        return
    
    message = f"🌍 <b>{country}</b>\n🖥 <b>{server}</b>\n\n📱 <code>{number}</code>"
    if was_reset:
        message = "🔄 " + MESSAGES[lang]["all_numbers_shown"] + "\n\n" + message
    
    bot.edit_message_text(
        message,
        chat_id,
        call.message.message_id,
        reply_markup=number_keyboard(country, server, lang)
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("refresh|"))
def refresh_number(call):
    chat_id = call.message.chat.id
    lang = USER_LANG.get(chat_id, "en")
    _, country, server = call.data.split("|")
    
    number, was_reset = get_unique_number(chat_id, country, server)
    
    if not number:
        bot.answer_callback_query(call.id, MESSAGES[lang]["no_numbers"])
        return
    
    message = f"🌍 <b>{country}</b>\n🖥 <b>{server}</b>\n\n📱 <code>{number}</code>"
    if was_reset:
        message = "🔄 " + MESSAGES[lang]["all_numbers_shown"] + "\n\n" + message
    
    bot.edit_message_text(
        message,
        chat_id,
        call.message.message_id,
        reply_markup=number_keyboard(country, server, lang)
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("file|"))
def create_file(call):
    chat_id = call.message.chat.id
    lang = USER_LANG.get(chat_id, "en")
    _, country, server = call.data.split("|")
    url = DATA[country][server]
    
    numbers = get_file_numbers(url, 20)
    
    if not numbers:
        bot.answer_callback_query(call.id, MESSAGES[lang]["no_numbers"])
        return

    file_name = create_unique_filename(country, server)
    file_content = "\n".join(numbers)
    
    file_io = io.BytesIO(file_content.encode("utf-8"))
    file_io.name = file_name
    file_io.seek(0)

    bot.send_document(
        chat_id, 
        file_io,
        caption=f"📁 {country} - {server}\n🆔 {file_name.split('_')[-1].replace('.txt', '')}\n📊 {len(numbers)} رقم"
    )
    bot.answer_callback_query(call.id, MESSAGES[lang]["file_created"])

@bot.callback_query_handler(func=lambda c: c.data == "change_lang")
def change_language(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if not is_user_member(user_id):
        lang = USER_LANG.get(chat_id, "ar")
        bot.edit_message_text(
            MESSAGES[lang]["must_join"],
            chat_id,
            call.message.message_id,
            reply_markup=subscription_keyboard(lang)
        )
        return
    
    kb = InlineKeyboardMarkup()
    for code, name in LANGS.items():
        kb.add(InlineKeyboardButton(name, callback_data=f"lang_change|{code}"))
    bot.edit_message_text("🌐 Choose language / اختر اللغة:", chat_id, call.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_change|"))
def change_language_final(call):
    chat_id = call.message.chat.id
    lang = call.data.split("|")[1]
    USER_LANG[chat_id] = lang
    bot.delete_message(chat_id, call.message.message_id)
    show_countries(chat_id, lang)

# ================== FLASK SERVER WITH POLLING ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بصمت", 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot_polling():
    """تشغيل البوت بطريقة polling"""
    while True:
        try:
            bot.infinity_polling(skip_pending=True, none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(5)
            continue

# ================== RUN ==================
if __name__ == "__main__":
    # تشغيل البوت في thread منفصل
    bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
    bot_thread.start()
    
    # تشغيل خادم Flask
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
