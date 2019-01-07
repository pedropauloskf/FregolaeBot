import telegram
from telegram.ext import Updater, CommandHandler
import os
from features import Ida, Volta, Remover, Start, Caronas, Help
from messages import MSGS
# If you want to test bot without persistence
# from tests import DummyDb
from db import MongoDbClient

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


class CaronaBot():
    def __init__(self, bd_cliente):
        self.bd_cliente = bd_cliente
        self.features = [
            Caronas(self.bd_cliente), Ida(self.bd_cliente), Volta(self.bd_cliente),
            Remover(self.bd_cliente), Start(self.bd_cliente), Help(None)]
        self.init_features()

    def init_features(self):
        self.feature_handler = {}
        for f in self.features:
            self.feature_handler[f.NOME] = f
            dispatcher.add_handler(
                CommandHandler(f.NOME, self.command_handler, pass_args=True))

    def command_handler(self, bot, update, args):
        user = update.message.from_user
        if (user is None or user.username is None):
            res = MSGS["username_error"]
        else:
            name = update.message.text.replace("@"," ").split(' ')[0].replace('/', '')
            chat_id = update.message.chat.id
            try:
                arg = args if name != Help.NOME else self.features
                res = self.feature_handler[name].processar(
                    user.username, chat_id, arg)
            except:
                res = MSGS["general_error"]
        bot.send_message(
            chat_id=update.message.chat.id, text=res,
            parse_mode=telegram.ParseMode.MARKDOWN)

if __name__ == '__main__':
    MONGO = os.environ.get("FREGOLAE_MLAB")
    TOKEN = os.environ.get('FREGOLAE_TOKEN')
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    CaronaBot(MongoDbClient(MONGO))
    updater.start_polling()
