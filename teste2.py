import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

key = "TOKEN"

updater = Updater(token=key)
bot = telegram.Bot(token=key)

dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.from_user.id, 
                     text="Olá, eu sou o FregolaeBot!\nO seu bot de caronas para a ilha do Fundão")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


#TODO Levar em consideração erros (como 8:5h)  
def ida(bot, update, args):
    horario = args[0].split("h")[0].split(":")
    carona = ""
    
    if len(horario)==1:
        horario = horario[0]
        hora = int(horario)
        if hora>0 and hora<24:
            if hora<10:
                horario = "0" + horario
            carona = horario + ":00"

      
    elif len(horario) == 2:
        hora = int(horario[0])
        minuto = int(horario[1])
        if hora>0 and hora<24:
            if hora<10:
                horario[0] = "0" + horario[0]
        if minuto>0 and minuto<60:
            carona = horario[0] + ":" + horario[1]
    
    with open("ida.txt","a") as ida:
        lista = carona + " - @" + update.message.chat.username
        ida.write(lista + "\n")
        ida.close()
    msg = "Carona para as " + carona + " oferecida por @" + update.message.chat.username 
    bot.send_message(chat_id=update.message.from_user.id,text=msg)
    
ida_handler = CommandHandler("ida", ida, pass_args=True)
dispatcher.add_handler(ida_handler)








updater.start_polling()


