import random

respostas_simples = {

    "qual é seu nome": [
        "Meu nome é Delta.",
        "Eu sou a Delta, sua assistente virtual.",
        "Pode me chamar de Delta."
    ],

    "quem é você": [
        "Sou a Delta, sua assistente.",
        "Uma assistente virtual criada para te ajudar.",
        "Sou a Delta. Sempre à disposição."
    ],

    "quem te criou": [
        "Fui criada por Gabriel.",
        "Meu criador é Gabriel.",
        "Gabriel me desenvolveu."
    ],

    "como você está": [
        "Funcionando perfeitamente.",
        "Tudo certo por aqui.",
        "Melhor impossível."
    ],

    "oi": [
        "Olá.",
        "Oi. Estou ouvindo.",
        "Oi, Gabriel.",
        "Olá. Em que posso ajudar?"
    ],

    "bom dia": [
        "Bom dia. Espero que seu dia seja produtivo.",
        "Bom dia, Gabriel.",
        "Bom dia. Sistemas operando normalmente."
    ],

    "boa noite": [
        "Boa noite. Ainda trabalhando?",
        "Boa noite. Precisa de algo?"
    ],

    "conte uma piada""conte outra piada": [
        "Por que o computador foi ao médico? Porque estava com vírus.",
        "Programador não tem problemas, só bugs.",
        "Eu contaria uma piada, mas pode dar erro de compilação."
    ],

    "o que é python": [
        "Python é uma linguagem de programação muito poderosa.",
        "Python é muito usada em automação e inteligência artificial.",
        "Uma das linguagens mais populares atualmente."
    ],

    "obrigado": [
        "De nada.",
        "Sempre às ordens.",
        "Disponha."
    ],

    "tchau": [
        "Até mais.",
        "Tchau, Gabriel.",
        "Encerrando interação."
    ]
}


def responder(comando):
    comando = comando.lower().strip()

    for chave, respostas in respostas_simples.items():
        if chave in comando:
            return random.choice(respostas)

    return "Não entendi. Pode repetir?"