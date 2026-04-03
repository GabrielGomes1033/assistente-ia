# coding: utf-8
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os

# =========================
# CONFIGURAÇÃO DO TTS
# =========================
engine = pyttsx3.init()

# Lista vozes do sistema
voices = engine.getProperty('voices')
pt_br_voice = None
for voice in voices:
    if "pt" in voice.id or "brazil" in voice.name.lower():
        pt_br_voice = voice.id
        break

if pt_br_voice:
    engine.setProperty('voice', pt_br_voice)
else:
    print("⚠️ Nenhuma voz pt-BR encontrada, usando padrão do sistema")

# Ajustes para voz mais natural
engine.setProperty("rate", 150)   # um pouco mais devagar
engine.setProperty("volume", 0.9) # volume natural

def falar(texto):
    print("Delta:", texto)
    engine.say(texto)
    engine.runAndWait()

# =========================
# FUNÇÃO DE COMANDO DE VOZ
# =========================
def ouvir():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Ouvindo...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        comando = r.recognize_google(audio, language="pt-BR")
        print("Você disse:", comando)
        return comando.lower()
    except sr.UnknownValueError:
        falar("Não entendi o que você disse.")
        return ""
    except sr.RequestError:
        falar("Erro ao acessar o serviço de reconhecimento.")
        return ""

# =========================
# FUNÇÕES DE COMANDOS
# =========================
def comando_horario():
    agora = datetime.datetime.now()
    falar(f"Agora são {agora.hour} horas e {agora.minute} minutos")

def comando_data():
    hoje = datetime.datetime.now()
    falar(f"Hoje é dia {hoje.day} do mês {hoje.month} de {hoje.year}")

def abrir_site(site):
    if "youtube" in site:
        webbrowser.open("https://www.youtube.com")
        falar("Abrindo YouTube")
    elif "google" in site:
        webbrowser.open("https://www.google.com")
        falar("Abrindo Google")
    elif "github" in site:
        webbrowser.open("https://www.github.com")
        falar("Abrindo GitHub")
    else:
        falar("Não conheço esse site.")

def comando_sistema(texto):
    if "reiniciar" in texto:
        falar("Reiniciando o sistema")
        os.system("sudo reboot")
    elif "desligar" in texto:
        falar("Desligando o sistema")
        os.system("sudo poweroff")
    else:
        falar("Comando de sistema não reconhecido.")

# =========================
# PERGUNTAS E RESPOSTAS SIMPLES
# =========================
respostas_simples = {
    "qual é seu nome": "Meu nome é Delta, sua assistente virtual.",
    "como você está": "Estou bem, obrigada por perguntar!",
    "o que você faz": "Eu posso responder perguntas, abrir sites, informar a hora e a data.",
    "me diga uma piada": "O que o zero disse para o oito? Belo cinto!",
    "você gosta de trabalhar": "Claro, mas às vezes acho que mereço férias... rs",
    "quem é você": "Sou a Delta, sua assistente inteligente e levemente irônica.",
    "abra o youtube": "youtube",
    "abra o google": "google",
    "Delta qual é a data de hoje": "data",
    "Delta qual é a hora": "horário",
}

# =========================
# COMANDOS DE ATIVAÇÃO/DESATIVAÇÃO
# =========================
comandos_ativar = ["ativar delta", "ok delta", "olá delta", "acorda bebe"]
comandos_desativar = ["desativar delta", "tchau delta", "até logo delta"]

# =========================
# LOOP PRINCIPAL
# =========================
delta_ativa = False
falar("Assistente Delta iniciada")

while True:
    comando = ouvir()
    
    # Verifica ativação ou desativação
    if any(c in comando for c in comandos_ativar):
        delta_ativa = True
        falar("Delta ativada")
        continue
    elif any(c in comando for c in comandos_desativar):
        delta_ativa = False
        falar("Delta desativada")
        continue
    
    # Se Delta não estiver ativa, ignora outros comandos
    if not delta_ativa:
        continue
    
    # Comandos quando Delta estiver ativa
    if comando in respostas_simples:
        resposta = respostas_simples[comando]
        # Executa funções especiais
        if resposta == "youtube":
            abrir_site("youtube")
        elif resposta == "google":
            abrir_site("google")
        elif resposta == "data":
            comando_data()
        elif resposta == "horário":
            comando_horario()
        else:
            falar(resposta)
    elif "reiniciar" in comando or "desligar" in comando:
        comando_sistema(comando)
    elif "sair" in comando or "tchau" in comando:
        falar("Encerrando a Delta. Até logo!")
        break
    elif comando != "":
        falar("Comando não reconhecido.")
