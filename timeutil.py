from datetime import datetime
from pytz import timezone
FUSO = timezone("America/Sao_Paulo")


# Funçao que verifica se o horário passado é válido
def valida_horario(arg):
    # Verifica se esta dentro do tamanho correto e se não há letras
    l = len(arg)
    if l >= 6:
        raise ValueError
    for ch in arg:
        if ch.isalpha():
            raise ValueError
    entrada = arg.split(":")

    # Cria objeto datetime para armazenamento no MongoDB
    time = datetime.now(FUSO)
    hora = int(entrada[0])
    if len(entrada) == 2:
        minuto = int(entrada[1])
    else:
        minuto = 0
    # objeto Datetime para armazenar carona
    horario = datetime(time.year, time.month, time.day,
                       hora, minuto, tzinfo=time.tzinfo)
    # Verifica se a carona é para o próprio dia ou para o dia seguinte
    if time > horario:
        try:
            horario = datetime(time.year, time.month,
                               time.day+1, hora, minuto)
        except ValueError:
            horario = datetime(time.year, time.month+1, 1, hora, minuto)

    dados = {"horario": horario.replace(tzinfo=None)}
    return dados
