import requests


def send_msg(text): # функция принимает текст и отправляет его в чат в тг
    token = "5863662131:AAEbBIJhoN8HLHNI3FoBQNxlciJudi8F1P4" # тут лежит токен бота
    chat_id = "-959491185" # id чата который получает сообщение
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    return requests.get(url_req)