numeros = {
    "zero": "0",
    "um": "1",
    "dois": "2",
    "três": "3",
    "tres": "3",
    "quatro": "4",
    "cinco": "5",
    "seis": "6",
    "sete": "7",
    "oito": "8",
    "nove": "9",
    "dez": "10"
}

operacoes = {
    "mais": "+",
    "menos": "-",
    "vezes": "*",
    "multiplicado por": "*",
    "dividido por": "/"
}


def traduzir_comando(comando):
    comando = comando.lower()

    for palavra, numero in numeros.items():
        comando = comando.replace(palavra, numero)

    for palavra, op in operacoes.items():
        comando = comando.replace(palavra, op)

    return comando


def calcular(comando):
    try:
        comando = traduzir_comando(comando)

        conta = comando.replace("calcular", "").replace("quanto é", "").strip()

        resultado = eval(conta)

        return resultado

    except:
        return None