import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import pymongo
from pymongo import MongoClient


def insere_bd(carona):
    client = MongoClient()
    caronas_col = client.fregolae.caronas
    caronas_col.insert_one(carona)
    client.close()

def valida_horario(arg):
    l = len(arg)
    if l>4 and l<6:
        for ch in arg:
            if ch.isalpha():
                raise ValueError
        horario = arg.split(":")
        
        
        hora = int(horario[0])        
        if len(horario)==2:
            minuto = int(horario[1]) 
        else:
            minuto = 0
        if hora>0 and hora<24:
            if hora<10:
                resp = "0" +  str(hora)
            else:
                resp = str(hora)
            if minuto>0 and minuto<60:
                resp = resp + ":" + horario[1]
            else:
                raise ValueError
        else: 
            raise ValueError
    else:
        raise ValueError
        
    dados = {"resp": resp, "hora":hora,"minuto":minuto}
    return dados

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

key = input("TOKEN: ") 

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
    try:
        
        dados = valida_horario(args[0])
        
        carona = dados.update({"username": "@" + update.message.chat.username, 
                               "tipo": 1,"ativo": 1})
        try:
            insere_bd(carona)
            msg = "Carona para as " + carona["resp"] + " oferecida por @" + update.message.chat.username 
            bot.send_message(chat_id=update.message.from_user.id,text=msg)
        except:
            x =1
    

    except ValueError:
        bot.send_message(chat_id=update.message.chat.id,text="Horário Inválido. Ex: /ida 7 ou /ida 7:30")


ida_handler = CommandHandler("ida", ida, pass_args=True)
dispatcher.add_handler(ida_handler)








updater.start_polling()


