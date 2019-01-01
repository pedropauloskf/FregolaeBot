import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import pymongo
from pymongo import MongoClient
from datetime import datetime
import os

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#Funçao para inserir uma nova carona no banco de dados
def insere_bd(carona):
    client = MongoClient()
    caronas_col = client.fregolae.caronas
    
    conditions = {"ativo":1,"tipo":carona["tipo"], "chat_id":carona["chat_id"], 
                  "username":carona["username"]}
    if caronas_col.count_documents(conditions) > 0:
        caronas_col.update_many(conditions,{"$set":{"ativo":0}})
    caronas_col.insert_one(carona)
    client.close()


#Funçao para recuperar a lista de caronas ativas
def busca_bd(tipo, chat_id):
    client = MongoClient()
    caronas_col = client.fregolae.caronas
    
    #Verifica se tem caronas para antes do horário atual ainda ativas e remove-as
    time = datetime.now()
    try:
        if time.hour == 23:
            margem = datetime(time.year,time.month,time.day+1,0,0)
        else:
            margem = datetime(time.year,time.month,time.day,time.hour,time.minute+20)
    except ValueError:
        margem = datetime(time.year,time.month,time.day,time.hour+1,time.minute-40)
    conditions = {"ativo":1, "chat_id":chat_id, "horario":{"$lt":margem}}
    if caronas_col.count_documents(conditions) > 0:
        caronas_col.update_many(conditions,{"$set":{"ativo":0}})
    
    
    res = caronas_col.find({"ativo":1,"tipo":tipo, "chat_id":chat_id}).sort("horario",pymongo.ASCENDING)
    client.close()
    
    msg = ""
    dia = 0
    for carona in res:
        if carona["horario"].day != dia:
            dia = carona["horario"].day
            mes = carona["horario"].month
            msg += "\n*" + str(dia) + "/" + str(mes) + "*\n"
        msg += carona["horario"].time().strftime("%X")[:5] + " - " + carona["username"]+"\n"
    return msg


#Funçao para desativar caronas
def desativar_bd(tipo, username, chat_id):
    client = MongoClient()
    caronas_col = client.fregolae.caronas
    conditions = {"ativo":1,"tipo":tipo, "username":username, "chat_id":chat_id}
    if caronas_col.count_documents(conditions) > 0:
        caronas_col.update_many(conditions,{"$set":{"ativo":0}})
        

#Funçao que verifica se o horário passado é válido
def valida_horario(arg):
    #Verifica se esta dentro do tamanho correto e se não há letras
    l = len(arg)
    if l<6:
        for ch in arg:
            if ch.isalpha():
                raise ValueError
        entrada = arg.split(":")
        
        #Cria objeto datetime para armazenamento no MongoDB
        time = datetime.now()
        hora = int(entrada[0])        
        if len(entrada)==2:
            minuto = int(entrada[1])
        else:
            minuto = 0
        #objeto Datetime para armazenar carona    
        horario = datetime(time.year,time.month,time.day,hora,minuto)
        #Verifica se a carona é para o próprio dia ou para o dia seguinte
        if time>horario:
            try:
                horario = datetime(time.year,time.month,time.day+1,hora,minuto)
            except ValueError:
                horario = datetime(time.year,time.month+1,1,hora,minuto)

    else:
        raise ValueError
        
    dados = {"horario":horario}
    return dados


key = os.environ.get('FREGOLAE_TOKEN')
bot = telegram.Bot(token=key)
updater = Updater(token=key)
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
            lista= "*Caronas de Ida:*\n"
            lista+= busca_bd(tipo, update.message.chat.id)
            bot.send_message(chat_id=update.message.chat.id, text=lista, 
                             parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
            bot.send_message(chat_id=update.message.chat.id, text=msg)
    
    else:        
        try:           
            carona = valida_horario(args[0])
            carona.update({"username": "@" + update.message.from_user.username, 
                           "chat_id": update.message.chat.id, "tipo": 1,"ativo": 1})
    
            try:
                insere_bd(carona)
                msg = ("Carona de ida para às " + carona["horario"].time().strftime("%X")[:5] 
                        + " oferecida por " + carona["username"] + ".")
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
    
    if len(args)==0:
        tipo = 2
        try:
            lista= "*Caronas de Volta:*\n"
            lista+= busca_bd(tipo, update.message.chat.id)
            bot.send_message(chat_id=update.message.chat.id, text=lista, 
                             parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
            bot.send_message(chat_id=update.message.chat.id,text=msg)
    
    else: 
        try:   
            carona = valida_horario(args[0])
            carona.update({"username": "@" + update.message.from_user.username, 
                           "chat_id": update.message.chat.id, "tipo": 2,"ativo": 1})
            try:
                insere_bd(carona)
                msg = ("Carona de volta para às " + carona["horario"].time().strftime("%X")[:5] 
                        + " oferecida por " + carona["username"] + ".")
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


def remover(bot, update, args):
    try:
        if len(args) != 1:
            raise ValueError
        elif args[0] == "ida":
            desativar_bd(1,update.message.chat.id,update.message.from_user.username)
            msg = "Carona de ida removida."
            bot.send_message(chat_id=update.message.chat.id, text=msg)
#            bot.send_message(chat_id=update.message.from_user.id, text=msg)
        elif args[0] == "volta":
            desativar_bd(2,update.message.chat.id,update.message.from_user.username)
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

remover_handler = CommandHandler("remover", remover, pass_args=True)
dispatcher.add_handler(remover_handler) 


def caronas(bot, update):
    try:
        if update.message.from_user.username == None:
            raise TypeError
        
        lista =  ""
        lista += "*Caronas de Ida:*\n"
        lista += busca_bd(1, update.message.chat.id)
        
        lista += "\n*Caronas de Volta:*\n"
        lista += busca_bd(2, update.message.chat.id)
        
        bot.send_message(chat_id=update.message.chat.id, text=lista, 
                         parse_mode=telegram.ParseMode.MARKDOWN)
    except TypeError:
        msg = "Crie um username nas configurações para poder utilizar o Bot"
        bot.send_message(chat_id=update.message.chat.id, text=msg)   
    except:
        msg = "Ocorreu um erro ao buscar a lista. Tente novamente." 
        bot.send_message(chat_id=update.message.chat.id,text=msg)

caronas_handler = CommandHandler("caronas", caronas)
dispatcher.add_handler(caronas_handler) 


def help(bot, update):
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


