# Assistente IA

Uma assistente pessoal de inteligência artificial desenvolvida em **Python**, capaz de ouvir comandos de voz, responder perguntas, executar cálculos, gerenciar agenda e interagir com o usuário de forma personalizada.

---

## Funcionalidades

- 🎤 **Reconhecimento de voz** com `SpeechRecognition`  
- 🗣️ **Síntese de fala** com `pyttsx3`  
- 🧮 **Calculadora segura** (expressões avaliadas com segurança)  
- 📅 **Agenda e lembretes**  
- 🔍 **Pesquisa na internet** com `requests` + `BeautifulSoup`  
- 🤖 **Personalidade customizável**  
- 📂 **Gerenciamento de playlists e comandos multimídia**  

---

## Instalação.

1. Clone o repositório:

git clone https://github.com/GabrielGomes1033/assistente-ia.git
cd assistente-ia


2. Crie e ative um ambiente virtual:


python3 -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows


3. Instale as dependências:


pip install -r requirements.txt


**No Linux**, se der erro com PyAudio:

sudo apt install portaudio19-dev python3-pyaudio

---

## Uso

Execute o script principal:


python main.py

Você pode também utilizar módulos diretamente:

from audio.ouvir import ouvir
from audio.voz import falar
from core.calculadora import calcular

