from abc import ABC, abstractmethod
from messages import MSGS
from timeutil import valida_horario


class BotFeature(ABC):
    NOME = ""
    DESCRIPTION = ""

    def __init__(self, bd_cliente):
        self.bd_cliente = bd_cliente

    # Método abstrato para processar uma mensagem e retornar mensagem resposta
    @abstractmethod
    def processar(self, username, chat_id, args):
        pass


class Ida(BotFeature):
    NOME = "ida"
    DESCRIPTION = "ida_description"

    def processar(self, username, chat_id, args):
        tipo = 1
        if len(args) == 0:
            try:
                return MSGS["ida_titulo"] + self.bd_cliente.busca_bd(
                    tipo, chat_id)
            except:
                return MSGS["list_error"]
        else:
            try:
                carona = valida_horario(args[0])
                notes = " ".join(args[1:]) if len([args > 1]) else ""

                carona.update(
                    {"username": username,
                     "chat_id": chat_id, "tipo": tipo, "ativo": 1, "notes": notes})
                try:
                    self.bd_cliente.insere_bd(carona)
                    data_carona = carona["horario"].time().strftime("%X")[:5]
                    return f"Carona de ida para às {data_carona} " + \
                        f"oferecida por @{username}."
                except:
                    return MSGS["add_error"]
            except ValueError:
                return MSGS["invalid_time_error"]


class Volta(BotFeature):
    NOME = "volta"
    DESCRIPTION = "volta_description"

    def processar(self, username, chat_id, args):
        tipo = 2
        if len(args) == 0:
            try:
                msg = MSGS["volta_titulo"]
                return msg + self.bd_cliente.busca_bd(tipo, chat_id)
            except:
                return MSGS["list_error"]
        else:
            try:
                carona = valida_horario(args[0])
                notes = " ".join(args[1:]) if len([args > 1]) else ""
                carona.update(
                    {"username": username,
                     "chat_id": chat_id, "tipo": tipo, "ativo": 1, "notes": notes})
                try:
                    self.bd_cliente.insere_bd(carona)
                    data_carona = carona["horario"].time().strftime("%X")[:5]
                    return f"Carona de Volta para às {data_carona} " + \
                        f"oferecida por @{username}."
                except:
                    return MSGS["add_error"]
            except ValueError:
                return MSGS["invalid_time_error"]


class Remover(BotFeature):
    NOME = "remover"
    DESCRIPTION = "remove_description"

    def processar(self, username, chat_id, args):
        if len(args) != 1 or args[0] not in ("ida", "volta"):
            return MSGS["remove_err"]
        else:
            self.bd_cliente.desativar_bd(
                1 if args[0] == "ida" else 2, chat_id, username)
            return str.format(MSGS["removed"], args[0])


class Caronas(BotFeature):
    NOME = "caronas"
    DESCRIPTION = "caronas_description"

    def processar(self, username, chat_id, args):
        ida = self.bd_cliente.busca_bd(1, chat_id)
        volta = self.bd_cliente.busca_bd(2, chat_id)
        return MSGS["ida_titulo"] + ida + MSGS["volta_titulo"] + volta


class Start(BotFeature):
    NOME = "start"

    def processar(self, username, chat_id, args):
        return MSGS["start"]


class Help(BotFeature):
    NOME = "help"

    def processar(self, username, chat_id, features):
        msg = MSGS["help_header"]
        i = 1
        for f in features:
            if (f.NOME in ("start", "help", "sobre")):
                continue
            msg += str.format(MSGS["feature_line"], i,
                              f.NOME, MSGS.get(f.DESCRIPTION, f.DESCRIPTION))
            i += 1
        msg += MSGS["help_footer"]
        return msg


class Sobre(BotFeature):
    NOME = "sobre"

    def processar(self, username, chat_id, features):
        return MSGS["sobre"]
