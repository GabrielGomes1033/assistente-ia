from audio.ouvir import ouvir
from audio.voz import falar
from core.comandos import *
from core.agenda import *
from core.memoria import *
from core.calculadora import calcular
from core.logging import logger

from inteligencia.respostas import respostas_simples
from inteligencia.pesquisa import *
from inteligencia.personalidade import estilizar_resposta, set_modo
from inteligencia.intencao import entender_intencao

import random
import time
import sys

palavras_ativacao = ["delta", "assistente"]

def limpar_comando(comando):
    """Remove palavras de ativação do comando"""
    for palavra in palavras_ativacao:
        comando = comando.replace(palavra, "")
    return comando.strip()

def processar_comando(comando):
    """Processa comandos por prioridade"""
    
    # Modos (maior prioridade)
    if comando.startswith("ativar ultron"):
        set_modo("ultron")
        return "Modo Ultron ativado."
    
    elif comando.startswith("ativar t8000"):
        set_modo("t8000")
        return "Modo T-8000 ativado."
    
    elif comando.startswith("ativar overlord"):
        set_modo("overlord")
        return "Modo Overlord ativado."
    
    elif comando.startswith("modo normal"):
        set_modo("normal")
        return "Modo normal ativado."
    
    # Comando sair
    if any(p in comando for p in ["sair", "encerrar", "tchau", "até logo"]):
        return estilizar_resposta("Encerrando assistente. Até logo!", comando)
    
    # Intenção detectada
    intencao = entender_intencao(comando)
    
    intencoes = {
        "horario": comando_horario(),
        "data": comando_data(),
        "add_tarefa": adicionar_tarefa(comando),
        "listar_tarefa": listar_tarefas(),
        "remover_tarefa": remover_tarefa(comando),
        "pesquisa": "Pesquisando...",
        "piada": random.choice([
            "Por que o computador foi ao médico? Porque estava com vírus.",
            "Programador não tem problemas, só bugs.",
            "Tentei rodar meu código... ele rodou de mim.",
            "Bug não é erro, é feature surpresa."
        ])
    }
    
    if intencao in intencoes:
        return estilizar_resposta(intencoes[intencao], comando)
    
    # Calculadora
    if any(p in comando for p in ["calcular", "quanto é", "mais", "menos", "vezes", "dividido"]):
        resultado = calcular(comando)
        if resultado:
            return estilizar_resposta(f"O resultado é {resultado}", comando)
        return estilizar_resposta("Não consegui fazer o cálculo. Tente de novo.", comando)
    
    # Respostas simples
    for pergunta, respostas in respostas_simples.items():
        if pergunta in comando:
            return estilizar_resposta(random.choice(respostas), comando)
    
    # Resposta padrão
    return estilizar_resposta("Não entendi o comando. Pode repetir?", comando)

def main():
    """Loop principal do assistente"""
    falar("🧠 Assistente iniciada. Diga 'Delta' ou 'Assistente' para ativar.")
    logger.info("Assistente iniciada")
    
    while True:
        try:
            comando = ouvir()
            
            if not comando or comando.strip() == "":
                continue
                
            comando = comando.lower().strip()
            
            # Verifica ativação
            if not any(palavra in comando for palavra in palavras_ativacao):
                continue
            
            comando_limpo = limpar_comando(comando)
            logger.info(f"Comando processado: {comando_limpo}")
            
            resposta = processar_comando(comando_limpo)
            
            if "Encerrando" in resposta:
                falar(resposta)
                logger.info("Assistente encerrada pelo usuário")
                break
            else:
                falar(resposta)
                
        except KeyboardInterrupt:
            falar("🛑 Encerrando por comando do usuário.")
            logger.info("Assistente interrompida pelo usuário (Ctrl+C)")
            break
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            falar("Desculpe, ocorreu um erro. Tente novamente.")

if __name__ == "__main__":
    main()