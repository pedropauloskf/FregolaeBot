from abc import ABC, abstractmethod
from messages import MSGS
from timeutil import valida_horario


class BotFeature(ABC):
    def __init__(self, bd_cliente):
        self.bd_cliente = bd_cliente

    # Método abstrato para processar uma mensagem e retornar mensagem resposta
    @abstractmethod
    def processar(self, username, chat_id, args):
        pass


class Ida(BotFeature):
    NOME = "ida"
    DESCRIPTION = \
        " [horario]: Adiciona uma carona de ida para o fundão chegando " + \
        "lá no horário informado. Ex: /ida 12:30\nSe não for informado " + \
        "um horário, enviará a lista das caronas de ida\n\n"

    def processar(self, username, chat_id, args):
        if len(args) == 0:
            tipo = 1
            try:
                msg = MSGS["ida_titulo"] + self.bd_cliente.busca_bd(
                    tipo, chat_id)
            except:
                return MSGS["list_error"]
        else:
            try:
                carona = valida_horario(args[0])
                carona.update(
                    {"username": username,
                     "chat_id": chat_id, "tipo": 1, "ativo": 1})
                try:
                    self.bd_cliente.insere_bd(carona)
                    data_carona = carona["horario"].time().strftime("%X")[:5]
                    return f"Carona de ida para às {data_carona} " + \
                        "oferecida por @{username}."
                except:
                    return MSGS["add_error"]
            except ValueError:
                return MSGS["invalid_time_error"]


class Volta(BotFeature):
    NOME = "volta"
    DESCRIPTION = \
        " [horario]: Adiciona uma carona de volta para o fundão" + \
        " saindo de lá no horário informado. Ex: /volta 12:30\nSe" + \
        " não for informado um horário, enviará a lista das" + \
        " caronas de volta\n\n"

    def processar(self, username, chat_id, args):
        if len(args) == 0:
            tipo = 2
            try:
                msg = "*Caronas de Volta:*\n"
                msg += self.bd_cliente.busca_bd(tipo, chat_id)
            except:
                return MSGS["list_error"]
        else:
            try:
                carona = valida_horario(args[0])
                carona.update(
                    {"username": username,
                     "chat_id": chat_id, "tipo": tipo, "ativo": 1})
                try:
                    self.bd_cliente.insere_bd(carona)
                    data_carona = carona["horario"].time().strftime("%X")[:5]
                    return f'Carona de Volta para às " +"{data_carona} " + \
                        "oferecida por @{username}.'
                except:
                    return MSGS["add_error"]
            except ValueError:
                return MSGS["invalid_time_error"]


class Remover(BotFeature):
    NOME = "remover"
    DESCRIPTION = " [ida/volta]: Remove da lista a sua carona, " + \
        "conforme selecionado.\n\n"

    def processar(self, username, chat_id, args):
        if len(args) != 1 or args[0] not in ("ida", "volta"):
            return MSGS["remove_err"]
        else:
            self.bd_cliente.desativar_bd(
                1 if args[0] == "ida" else 0, chat_id, username)
            return str.format(MSGS["removed"], args[0])


class Caronas(BotFeature):
    NOME = "caronas"
    DESCRIPTION = " : Lista todas as caronas ativas no momento, separadas" + \
        " por dia, ida e volta\n\n"

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
            if (f.NOME in ("start", "help")):
                continue
            msg += str.format(MSGS["feature_line"], i, f.NOME, f.DESCRIPTION)
            i += 1
        msg += MSGS["help_footer"]
        return msg
