import telebot as tb
import json
from telebot import types as t
from datetime import date, time, datetime, timedelta


token = "7819228238:AAGmY1aqMjlY5ewzt4timEsEzNx0cXoxJlc"
bot = tb.TeleBot(token)

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Hello {name}!")

def add_appointment(date, time, client):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"appointments": [], "reviews": [], "clients": {}}
    new_appointment = {"date": date, "time": time, "client": client}
    data["appointments"].append(new_appointment)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
        if call.data.startswith("day:"):
            date = call.data.split(":")[1]
            bot.send_message(call.message.chat.id, f"Вы выбрали: {date}")
            bot.send_message(call.message.chat.id, "Выберите время: ", reply_markup=summon_time_keyboard(date))
        if call.data.startswith("appointment:"):
            chosen_date = call.data.split(":")[1]
            chosen_time = call.data.split(":")[2] + ":00"
            add_appointment(chosen_date, chosen_time, call.message.chat.id)
            bot.send_message(call.message.chat.id, f"Вы выбрали дату: {chosen_date}, время: {chosen_time}")
        if call.data.startswith("cancel:"):
            data = call.data
            data = data.split(" ")
            with open("data.json", "r", encoding="utf-8") as f:
                f = json.load(f)
            for appointment in f["appointments"]:
                if appointment["time"] == data[2] and appointment["date"] == data[1] and appointment["client"] == call.message.chat.id:
                    pop = int(data[3])
                    f["appointments"].pop(pop)
            with open("data.json", "w", encoding="utf-8") as file:
                json.dump(f, file, ensure_ascii=False, indent=4)
                bot.send_message(call.message.chat.id, f"Ваша встреча в {data[1]} {data[2]} отменина!")
        
@bot.message_handler(commands=["show_dates"])
def show_dates(message):
    keyboard = summon_date_keyboard()
    bot.send_message(message.chat.id, "Выберите день: ", reply_markup=keyboard)

@bot.message_handler(commands=["ask_question"])
def ask(message):
    bot.send_message(message.chat.id, "Какой у вас вопрос?")
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda message: ask_q(message))

@bot.message_handler(commands=["set_name"])
def set_name(message):
    bot.send_message(message.chat.id, "Напишите ваше имя: ")
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda message: save_name(message))

@bot.message_handler(commands=["add_review"])
def add_review(message):
    bot.send_message(message.chat.id, "Напишите ваш отзыв:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda message: save_review(message))

@bot.message_handler(commands=["cancel_appointment"])
def can_app(message):
    with open("data.json", "r", encoding="utf-8") as f:
        file = json.load(f)
    canceble_appointments_by_date = []
    for appointment in file["appointments"]:
        if appointment["client"] == message.chat.id:
            canceble_appointments_by_date.append(f"{appointment['date']} {appointment['time']}")
    length = len(canceble_appointments_by_date)
    if length == 0:
        bot.send_message(message.chat.id, "У вас пока нет встреч.")
    else:
        bot.send_message(message.chat.id, "Выберите какую встречу ва хотите отменить:", reply_markup=summon_keyboard_for_cancel(canceble_appointments_by_date))

def ask_q(message):
    q = message.text
    with open("data.json", "r", encoding="utf-8") as f:
        f = json.load(f)
    f["FAQs"][str(message.chat.id)] = q
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(f, file, ensure_ascii=False, indent=4)
        bot.send_message(message.chat.id, "Ваш вопрос сохранили!")

def save_review(message):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        data["reviews"][str(message.chat.id)] = message.text
    except FileNotFoundError:
        data = {"appointments": [], "reviews": [], "clients": {}}   
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    bot.send_message(message.chat.id, "Ваш  отзыв сохранили!")
    
def save_name(message):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"appointments": [], "reviews": [], "clients": {}}    
    try:
        data["clients"][str(message.chat.id)] = message.text
    except FileNotFoundError:
        data = {"appointments": [], "reviews": [], "clients": {}} 
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    bot.send_message(message.chat.id, "Ваше имя сохранено!")
    
def summon_date_keyboard():
    keyboard = t.InlineKeyboardMarkup()
    with open("data.json", "r", encoding="utf-8") as f:
        file = json.load(f)
    for i in range(7):
        today = date.today()
        delta = timedelta(days=1)
        data = f"day:{today + 3*delta + i*delta}"
        checker = 0
        for appointment in file["appointments"]:
            if appointment["date"] == f'{today + 3*delta + i*delta}':
                checker += 1
        if checker != 6:
            button = t.InlineKeyboardButton(text=data[4:], callback_data=data)
            keyboard.add(button)
    return keyboard

def summon_time_keyboard(date):
    keyboard = t.InlineKeyboardMarkup()
    li = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    with open("data.json", "r", encoding="utf-8") as f:
        file = json.load(f)
        for appointment in file["appointments"]:
            if appointment["date"] == date:
                li.remove(appointment["time"])
    for l in li:
        data = f"appointment:{date}:{l}"
        button = t.InlineKeyboardButton(text=l, callback_data=data)
        keyboard.add(button)
    return keyboard

def summon_keyboard_for_cancel(list):
    keyboard = t.InlineKeyboardMarkup()
    num = -1
    for element in list:
        num += 1
        data = f"cancel: {element} {num}"
        button = t.InlineKeyboardButton(text=element, callback_data=data)
        keyboard.add(button)
    return keyboard

bot.polling(none_stop=True)