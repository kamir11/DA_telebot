import telebot
import re
import os
from telebot import types

bot = telebot.TeleBot('6017525957:AAFmfeNLS4mrKAaGKPLRTEdVLfz3t34atZc')
shopping_list = {}


# Обработчик начальных команд 'start', а также создание папки для каждого пользователя с названием папки ID пользователя
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_message = message.from_user.id
    user_folder = str(user_message)

    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(user_message, "Привет! Я бот, который поможет тебе управлять списком покупок.")
    bot.send_message(user_message, 'Для справки напиши в чат команду /help', reply_markup=markup)
    show_main_menu(user_message)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    help_text = """
    Этот бот позволяет вам управлять вашим списком покупок. Вот доступные команды:

    /start - начать взаимодействие с ботом
    
    <b>Список покупок</b> - просмотреть текущий список покупок
    
    <b>Добавить покупку</b> - добавить покупку в список (напишите боту в формате "Продукт, Количество")
    
    <b>Удалить покупку</b> - удалить покупку из списка (укажите номер строки для удаления)

    Вы также можете использовать кнопки в меню для выполнения этих действий.

    Для получения справки в любое время, введите /help.
    """
    bot.send_message(user_id, help_text, parse_mode='HTML')
    show_main_menu(user_id)


# Здесь главное меню с кнопками
def show_main_menu(user_message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_list = types.KeyboardButton('Список покупок')
    button_delete = types.KeyboardButton('Удалить покупку')
    button_add = types.KeyboardButton('Добавить покупку')
    markup.row(button_list)
    markup.row(button_add, button_delete)
    bot.send_message(user_message, 'Выбери действие:', reply_markup=markup)


def load_shopping_list(user_id):
    user_folder = str(user_id)
    list_filename = os.path.join(user_folder, 'shopping_list.txt')

    if os.path.exists(list_filename):
        with open(list_filename, 'r') as file:
            lines = file.readlines()
            return {line.split('-')[0].strip(): line.split('-')[1].strip() for line in lines}
    else:
        return {}


def save_shopping_list(user_id, shopping_list):
    user_folder = str(user_id)
    list_filename = os.path.join(user_folder, 'shopping_list.txt')

    with open(list_filename, 'w') as file:
        for product, quantity in shopping_list.items():
            file.write(f"{product} - {quantity}\n")


@bot.message_handler(commands=['list'])
def handle_list(message):
    user_id = message.from_user.id
    shopping_list = load_shopping_list(user_id)

    if shopping_list:
        items = "\n".join(
            [f"{index + 1}. {product} - {quantity}" for index, (product, quantity) in enumerate(shopping_list.items())])
        bot.send_message(user_id, f"Твой текущий список покупок:\n\n{items}")
    else:
        bot.send_message(user_id, "Твой список покупок пуст.")

    show_main_menu(user_id)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == 'Список покупок':
        handle_list(message)
    elif text == 'Удалить покупку':
        bot.send_message(user_id, "Напиши номер строки, которую нужно удалить:")
        bot.register_next_step_handler(message, handle_delete)
    elif text == 'Добавить покупку':
        bot.send_message(user_id, "Напиши новую покупку для добавления в формате \"Продукт, Количество\":")
        bot.register_next_step_handler(message, handle_add)
    else:
        bot.send_message(user_id,
                         'Я не понимаю эту команду. Воспользуйтесь кнопками или напишите "Список покупок", "Удалить покупку" или "Добавить покупку".')


def handle_delete(message):
    user_id = message.from_user.id
    text = message.text.strip()

    try:
        index_to_delete = int(text) - 1
        shopping_list = load_shopping_list(user_id)

        if 0 <= index_to_delete < len(shopping_list):
            string_to_delete = list(shopping_list.keys())[index_to_delete]
            del shopping_list[string_to_delete]
            save_shopping_list(user_id, shopping_list)
            bot.send_message(user_id, f'Покупка "{string_to_delete}" удалена из списка.')
        else:
            bot.send_message(user_id, "Неверный номер строки для удаления.")
    except (ValueError, IndexError):
        bot.send_message(user_id,
                         "Пожалуйста, введите номер строки для удаления в правильном формате (например, \"1\").")
    show_main_menu(user_id)


def handle_add(message):
    user_id = message.from_user.id
    text = message.text.strip()

    try:
        product, quantity = map(str.strip, re.split(r', |,| ', text))
        shopping_list = load_shopping_list(user_id)
        shopping_list[product] = quantity
        save_shopping_list(user_id, shopping_list)
        bot.send_message(user_id, f'Покупка "{product}" в количестве {quantity} добавлена в список.')
    except ValueError:
        bot.send_message(user_id,
                         'Пожалуйста, введите новую покупку в правильном формате (например, \"Продукт, Количество\")')
    show_main_menu(user_id)


if __name__ == "__main__":
    bot.polling(none_stop=True)
