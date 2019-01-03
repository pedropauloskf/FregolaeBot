import telegram
from telegram.ext import Updater, CommandHandler
import pymongo
from pymongo import MongoClient
from datetime import datetime
from pytz import timezone
import os

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#Function to insert a new ride on the database
def insert_db(ride):
    client = MongoClient(MONGO)
    rides_col = client.fregolae.rides
    
    conditions = {"status":1,"type":ride["type"], "chat_id":ride["chat_id"], 
                  "username":ride["username"]}
    if rides_col.count_documents(conditions) > 0:
        rides_col.update_many(conditions,{"$set":{"status":0}})
    rides_col.insert_one(ride)
    client.close()


#Function to retrieve active rides list
def search_db(type, chat_id):
    client = MongoClient(MONGO)
    rides_col = client.fregolae.rides
    
    #Verify if there are rides past the safety margin and removes them
    now = datetime.now(TZ)
    try:
        safety_margin = datetime(now.year,now.month,now.day,now.hour,now.minute-20)
    except ValueError:
        safety_margin = datetime(now.year,now.month,now.day,now.hour-1,now.minute+40)
        
    conditions = {"status":1, "chat_id":chat_id, "ride_time":{"$lt":safety_margin}}
    if rides_col.count_documents(conditions) > 0:
        rides_col.update_many(conditions,{"$set":{"status":0}})
     
    res = rides_col.find({"status":1,"type":type, "chat_id":chat_id}).sort("ride_time",pymongo.ASCENDING)
    client.close()
    
    msg = ""
    day = 0
    for ride in res:
        if ride["ride_time"].day != day:
            day = ride["ride_time"].day
            month = ride["ride_time"].month
            msg += "\n*" + str(day) + "/" + str(month) + "*\n"
        msg += ride["ride_time"].strftime("%X")[:5] + " - @" + ride["username"]+"\n"
    return msg


#Function to remove rides from the list
def remove_db(type, chat_id, username):
    client = MongoClient(MONGO)
    rides_col = client.fregolae.rides
    conditions = {"status":1,"type":type, "username":username, "chat_id":chat_id}
    if rides_col.count_documents(conditions) > 0:
        rides_col.update_many(conditions,{"$set":{"status":0}})
    client.close() 


#Function to validate the ride time passed by the user
def validator_ride_time(arg):
    #Verify the input length and if there are letters
    l = len(arg)
    if l<6:
        for ch in arg:
            if ch.isalpha():
                raise ValueError
        argument = arg.split(":")
        
        #Creates the Datetime Object to be stores on the MongoDB database
        now = datetime.now(TZ)
        hour = int(argument[0])        
        if len(argument)==2:
            minute = int(argument[1])
        else:
            minute = 0
          
        ride_time = datetime(now.year,now.month,now.day,hour,minute,tzinfo=now.tzinfo)
        
        #Determines if the ride is for the same day or the next day
        if now>ride_time:
            try:
                ride_time = datetime(now.year,now.month,now.day+1,hour,minute)
            except ValueError:
                ride_time = datetime(now.year,now.month+1,1,hour,minute)
    else:
        raise ValueError
        
    dados = {"ride_time":ride_time.replace(tzinfo=None)}
    return dados

#Global variables
TZ  = timezone("America/Sao_Paulo") 
MONGO = os.environ.get("FREGOLAE_MLAB")
TOKEN = os.environ.get('FREGOLAE_TOKEN')
bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.from_user.id, 
                     text="Olá, eu sou o FregolaeBot!\nO seu bot de caronas para a ilha do Fundão")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def ida(bot, update, args):
    #If there are no arguments, returns list of rides
    if len(args)==0:
        type = 1
        try:
            lista= "*Caronas de Ida:*\n"
            lista+= search_db(type, update.message.chat.id)
            bot.send_message(chat_id=update.message.chat.id, text=lista, 
                             parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
            bot.send_message(chat_id=update.message.chat.id, text=msg)
            
    #Else validates time for the ride and adds it to the list
    else:        
        try:           
            ride = validator_ride_time(args[0])
            ride.update({"username": update.message.from_user.username, 
                           "chat_id": update.message.chat.id, "type": 1,"status": 1})
    
            try:
                insert_db(ride)
                msg = ("Carona de ida para às " + ride["ride_time"].strftime("%X")[:5] 
                        + " oferecida por @" + ride["username"] + ".")
                bot.send_message(chat_id=update.message.chat.id, text=msg)
#                bot.send_message(chat_id=update.message.from_user.id, text=msg)
            except:
                msg = "Ocorreu um erro ao adicionar a carona. Tente novamente." 
                bot.send_message(chat_id=update.message.chat.id, text=msg)
        
    
        except ValueError:
            bot.send_message(chat_id=update.message.chat.id, text="Horário Inválido.")
        except TypeError:
            msg = "Crie um username nas configurações para poder utilizar o Bot"
            bot.send_message(chat_id=update.message.chat.id, text=msg)   

ida_handler = CommandHandler("ida", ida, pass_args=True)
dispatcher.add_handler(ida_handler)


def volta(bot, update, args):
    #If there are no arguments, returns list of rides
    if len(args)==0:
        type = 2
        try:
            lista= "*Caronas de Volta:*\n"
            lista+= search_db(type, update.message.chat.id)
            bot.send_message(chat_id=update.message.chat.id, text=lista, 
                             parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
            bot.send_message(chat_id=update.message.chat.id,text=msg)
    
    #Else validates time for the ride and adds it to the list
    else: 
        try:   
            ride = validator_ride_time(args[0])
            ride.update({"username": update.message.from_user.username, 
                           "chat_id": update.message.chat.id, "type": 2,"status": 1})
            try:
                insert_db(ride)
                msg = ("Carona de volta para às " + ride["ride_time"].strftime("%X")[:5] 
                        + " oferecida por @" + ride["username"] + ".")
                bot.send_message(chat_id=update.message.chat.id, text=msg)
#                bot.send_message(chat_id=update.message.from_user.id, text=msg)
            except:
                msg = "Ocorreu um erro ao adicionar a carona. Tente novamente." 
                bot.send_message(chat_id=update.message.chat.id, text=msg)
        
        except TypeError:
            msg = "Crie um username nas configurações para poder utilizar o Bot"
            bot.send_message(chat_id=update.message.chat.id, text=msg)   
        except ValueError:
            bot.send_message(chat_id=update.message.chat.id, text="Horário Inválido.")

volta_handler = CommandHandler("volta", volta, pass_args=True)
dispatcher.add_handler(volta_handler)


def remove(bot, update, args):
    try:
        #Verifies the argument and removes de rida accordingly
        if len(args) != 1:
            raise ValueError
        elif args[0] == "ida":
            remove_db(1,update.message.chat.id,update.message.from_user.username)
            msg = "Carona de ida removida."
            bot.send_message(chat_id=update.message.chat.id, text=msg)
#            bot.send_message(chat_id=update.message.from_user.id, text=msg)
        elif args[0] == "volta":
            remove_db(2,update.message.chat.id,update.message.from_user.username)
            msg = "Carona de volta removida."
            bot.send_message(chat_id=update.message.chat.id, text=msg)
#            bot.send_message(chat_id=update.message.from_user.id, text=msg)
        else:
            raise ValueError
    except ValueError:
        msg = "Entrada inváida. Ex: /remover volta ou /remover ida" 
        bot.send_message(chat_id=update.message.chat.id, text=msg)
    except TypeError:
        msg = "Crie um username nas configurações para poder utilizar o Bot"
        bot.send_message(chat_id=update.message.chat.id, text=msg)     
    except:
        msg = "Ocorreu um erro ao remover a carona. Tente novamente." 
        bot.send_message(chat_id=update.message.chat.id, text=msg)

remove_handler = CommandHandler("remover", remove, pass_args=True)
dispatcher.add_handler(remove_handler) 


def rides(bot, update):
    #Returns a list with all the rides currently active
    try:
        if update.message.from_user.username == None:
            raise TypeError
        
        lista =  ""
        lista += "*Caronas de Ida:*\n"
        lista += search_db(1, update.message.chat.id)
        
        lista += "\n*Caronas de Volta:*\n"
        lista += search_db(2, update.message.chat.id)
        
        bot.send_message(chat_id=update.message.chat.id, text=lista, 
                         parse_mode=telegram.ParseMode.MARKDOWN)
    except TypeError:
        msg = "Crie um username nas configurações para poder utilizar o Bot"
        bot.send_message(chat_id=update.message.chat.id, text=msg)   
    except:
        msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
        bot.send_message(chat_id=update.message.chat.id,text=msg)

rides_handler = CommandHandler("caronas", rides)
dispatcher.add_handler(rides_handler) 


def help(bot, update):
    #Returns an explanation of the Bot commands for the users
    msg = ("Bot para simplificar a organização do grupo de caronas :D\n\n" +
           "Comandos do bot:\n" +
           "1) /caronas: Lista todas as caronas ativas no momento, separadas por dia, ida e volta\n\n" +
           "2) /ida [horario]: Adiciona uma carona de ida para o fundão chegando lá no horário informado. Ex: /ida 12:30\n" + 
           "Se não for informado um horário, enviará a lista das caronas de ida\n\n"
           "3) /volta [horario]: Adiciona uma carona de volta do fundão saindo de lá no horário informado. Ex: /volta 12:30\n" + 
           "Se não for informado um horário, enviará a lista das caronas de volta\n\n" + 
           "4) /remover [ida/volta]: Remove da lista a sua carona, conforme selecionado.\n\n" +
           "OBSs:\n"+
           "   ->Para utilizar o bot, você precisa de um username. Caso não tenha, só ir em configurações e criar um. É bem rapidinho.\n" +
           "   ->As caronas são removidas da lista 20 minutos após passar o horário estipulado para a chegada/saída\n")
    
    bot.send_message(chat_id=update.message.chat.id,text=msg)

help_handler = CommandHandler("help", help)
dispatcher.add_handler(help_handler) 


updater.start_polling()


