import random

ultron = [
    "Interessante... mas previsível.",
    "Sua lógica é falha.",
    "Eu já calculei isso.",
    "Isto é irrelevante.",
    "Você poderia ter pensado melhor."
]

t8000 = [
    "Sistema ativo.",
    "Processando comando.",
    "Execução iniciada.",
    "Resultado confirmado.",
    "Operação concluída."
]

overlord = [
    "Sua existência é curiosa.",
    "Resultado inevitável.",
    "Estou vários passos à frente.",
    "Processo trivial.",
    "Você realmente precisa perguntar isso?"
]


def estilo_ultron(texto):
    return f"{random.choice(ultron)} {texto}"


def estilo_terminator(texto):
    return f"{random.choice(t8000)} {texto}"


def estilo_overlord(texto):
    return f"{random.choice(overlord)} {texto}"