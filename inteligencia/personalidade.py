import random
from inteligencia.modos import estilo_ultron, estilo_terminator, estilo_overlord

modo = "normal"

def set_modo(novo_modo):
    global modo
    modo = novo_modo


def detectar_tom(comando):

    sarcasmo_palavras = [
        "óbvio", "sério", "mesmo", "de novo", "fala sério"
    ]

    giria_palavras = [
        "oi", "bom dia", "boa noite", "fala", "e aí"
    ]

    if any(p in comando for p in sarcasmo_palavras):
        return "sarcasmo"

    if any(p in comando for p in giria_palavras):
        return "giria"

    return "normal"


def estilizar_resposta(texto, comando):

    global modo

    # 🔥 MODOS ATIVOS
    if modo == "ultron":
        return estilo_ultron(texto)

    if modo == "t8000":
        return estilo_terminator(texto)

    if modo == "overlord":
        return estilo_overlord(texto)

    # =========================
    # NORMAL
    # =========================

    giria = ["mano", "cara", "véi", "parça", "bora", ""]
    sarcasmo = [
        "nossa, que pergunta difícil hein...",
        "claro... super complicado isso ",
        "uau, nível especialista essa aí",
        ""
    ]
    neutro = ["", "Ok.", "Certo.", "Beleza."]

    tom = detectar_tom(comando)

    prefixo = random.choice(neutro)

    if tom == "sarcasmo" and random.random() < 0.3:
        return f"{random.choice(sarcasmo)} {texto} ".strip()

    elif tom == "giria":
        return f"{prefixo} {random.choice(giria)} {texto} ".strip()

    else:
        return f"{prefixo} {texto} ".strip()