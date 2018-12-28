import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import pymongo
from pymongo import MongoClient

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def insere_bd(carona):
    client = MongoClient()
    caronas_col = client.fregolae.caronas
    caronas_col.insert_one(carona)
    client.close()

def busca_bd(tipo, chat_id):
    client = MongoClient()
    caronas_col = client.fregolae.caronas
    res = caronas_col.find({"ativo":1,"tipo":tipo, "chat_id":chat_id})
    client.close()
    
    msg = ""
    for carona in res:
        msg += carona["resp"] + " - " + carona["username"]+"\n"
    return msg
    
def valida_horario(arg):
    l = len(arg)
    if l<6:
        for ch in arg:
            if ch.isalpha():
                raise ValueError
        horario = arg.split(":")
        
        
        hora = int(horario[0])        
        if len(horario)==2:
            minuto = int(horario[1]) 
        else:
            minuto = 0
        if hora>=0 and hora<24:
            if hora<10:
                resp = "0" +  str(hora)
            else:
                resp = str(hora)
            if minuto>=0 and minuto<60:
                if minuto!=0:
                    resp = resp + ":" + horario[1]
                else:
                    resp = resp + ":00"
            else:
                raise ValueError
        else: 
            raise ValueError
    else:
        raise ValueError
        
    dados = {"resp": resp, "hora":hora,"minuto":minuto}
    return dados


key = input("TOKEN: ") 

updater = Updater(token=key)
bot = telegram.Bot(token=key)

dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.from_user.id, 
                     text="Olá, eu sou o FregolaeBot!\nO seu bot de caronas para a ilha do Fundão")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def ida(bot, update, args):
    
    if len(args)==0:
        tipo = 1
        try:
            lista= "**Caronas de Ida:**\n\n"
            lista+= busca_bd(tipo, update.message.chat.id)
            bot.send_message(chat_id=update.message.chat.id,text=lista)
        except:
            msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
            bot.send_message(chat_id=update.message.chat.id,text=msg)
    
    else:        
        try:           
            carona = valida_horario(args[0])
            carona.update({"username": "@" + update.message.chat.username, 
                           "chat_id": update.message.chat.id, "tipo": 1,"ativo": 1})
    
            try:
                insere_bd(carona)
                msg = "Carona de ida para as " + carona["resp"] + " oferecida por @" + update.message.chat.username 
                bot.send_message(chat_id=update.message.from_user.id,text=msg)
            except:
                msg = "Ocorreu um erro ao adicionar a carona. Tente novamente." 
                bot.send_message(chat_id=update.message.chat.id,text=msg)
        
    
        except ValueError:
            bot.send_message(chat_id=update.message.chat.id,text="Horário Inválido. Ex: /ida 7 ou /ida 7:30")


ida_handler = CommandHandler("ida", ida, pass_args=True)
dispatcher.add_handler(ida_handler)



def volta(bot, update, args):
    
    if len(args)==0:
        tipo = 2
        try:
            lista= "**Caronas de Volta:**\n\n"
            lista+= busca_bd(tipo, update.message.chat.id)
            bot.send_message(chat_id=update.message.chat.id,text=lista)
        except:
            msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
            bot.send_message(chat_id=update.message.chat.id,text=msg)
    
    else: 
        try:   
            carona = valida_horario(args[0])
            carona.update({"username": "@" + update.message.chat.username, 
                           "chat_id": update.message.chat.id, "tipo": 2,"ativo": 1})
            try:
                insere_bd(carona)
                msg = "Carona de volta para as " + carona["resp"] + " oferecida por @" + update.message.chat.username 
                bot.send_message(chat_id=update.message.from_user.id,text=msg)
            except:
                msg = "Ocorreu um erro ao adicionar a carona. Tente novamente." 
                bot.send_message(chat_id=update.message.chat.id,text=msg)
        
    
        except ValueError:
            bot.send_message(chat_id=update.message.chat.id,text="Horário Inválido.")


volta_handler = CommandHandler("volta", volta, pass_args=True)
dispatcher.add_handler(volta_handler)

updater.start_polling()


