import webbrowser
import datetime
import re
import os
import random
import subprocess
import platform
from pathlib import Path
from core.logging import logger
from sympy import sympify, SympifyError
from typing import Optional, List

# =========================
# CONFIGURAÇÕES GLOBAIS
# =========================
SITES_RAPIDOS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "github": "https://github.com",
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "twitter": "https://twitter.com",
    "netflix": "https://netflix.com"
}

PLAYLIST_DIR = Path("playlists")
MUSICA_EXTENSOES = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

# Detecta sistema operacional
SO = platform.system().lower()

# =========================
# ABRIR SITES (MELHORADO)
# =========================
def abrir_site(nome: str) -> str:
    """Abre sites rapidamente"""
    nome = nome.lower().strip()
    
    if nome in SITES_RAPIDOS:
        webbrowser.open(SITES_RAPIDOS[nome])
        logger.info(f"Abrindo {nome}")
        return f"Abrindo {nome}!"
    
    # Busca por URL
    if nome.startswith(("http://", "https://")):
        webbrowser.open(nome)
        return f"Abrindo {nome}"
    
    # Pesquisa Google
    query = nome.replace(" ", "+")
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Pesquisando '{nome}' no Google"

# =========================
# HORÁRIO E DATA (MELHORADO)
# =========================
def comando_horario(formato="curto") -> str:
    """Retorna horário atual"""
    agora = datetime.datetime.now()
    
    formatos = {
        "curto": f"Agora são {agora.strftime('%H:%M')}",
        "completo": f"Agora são {agora.strftime('%H:%M:%S')} do dia {agora.strftime('%d/%m/%Y')}",
        "digital": f"São {agora.strftime('%Hh%M')}"
    }
    
    return formatos.get(formato, formatos["curto"])

def comando_data(formato="por_extenso") -> str:
    """Retorna data atual"""
    meses = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    
    hoje = datetime.datetime.now()
    
    formatos = {
        "por_extenso": f"Hoje é {hoje.day} de {meses[hoje.month-1]} de {hoje.year}",
        "numerico": f"Hoje é {hoje.strftime('%d/%m/%Y')}",
        "semana": f"Hoje é {hoje.strftime('%A, %d de %B de %Y')}"
    }
    
    return formatos.get(formato, formatos["por_extenso"])

# =========================
# CALCULADORA ULTRA SEGURA
# =========================
def calcular(texto: str) -> Optional[float]:
    """Calculadora segura com SymPy"""
    try:
        if not texto or len(texto.strip()) < 2:
            return None
            
        # Normaliza texto
        texto = texto.lower().strip()
        
        # Substituições melhoradas
        substituicoes = {
            "mais": "+", "somar": "+", "adicionar": "+",
            "menos": "-", "subtrair": "-", "tirar": "-",
            "vezes": "*", "multiplicar": "*", "multiplicado": "*",
            "dividido": "/", "dividir": "/", "divisão": "/",
            "raiz de": "sqrt(", "raiz quadrada": "sqrt(",
            "quanto é": "", "calcule": "", "calcula": "",
            "por cento": "/100", "%": "/100"
        }
        
        for pt, en in substituicoes.items():
            texto = re.sub(rf'\b{pt}\b', en, texto)
        
        # Extrai apenas números e operadores
        expressao = re.sub(r'[^0-9+\-*/().\s]', '', texto)
        expressao = re.sub(r'\s+', '', expressao)
        
        if not expressao or len(expressao) < 2:
            return None
        
        # Validações de segurança
        if re.search(r'[a-zA-Z]', expressao) or expressao.count('(') != expressao.count(')'):
            return None
        
        logger.debug(f"Calculando: {expressao}")
        resultado = float(sympify(expressao).evalf())
        
        # Formatação inteligente
        if resultado.is_integer():
            return int(resultado)
        return round(resultado, 6)
        
    except SympifyError as e:
        logger.error(f"Erro SymPy: {e}")
        return None
    except (ValueError, ZeroDivisionError, OverflowError):
        logger.error("Erro matemático (divisão por zero ou overflow)")
        return None
    except Exception as e:
        logger.error(f"Erro cálculo: {e}")
        return None

# =========================
# MÚSICA E PLAYLIST (SUPER MELHORADA)
# =========================
def listar_playlists() -> List[str]:
    """Lista todas as playlists disponíveis"""
    if not PLAYLIST_DIR.exists():
        return []
    
    playlists = []
    for pasta in PLAYLIST_DIR.iterdir():
        if pasta.is_dir():
            musicas = sum(1 for f in pasta.iterdir() if f.suffix.lower() in MUSICA_EXTENSOES)
            playlists.append(f"{pasta.name} ({musicas} músicas)")
    
    return playlists

def tocar_playlist(nome: str, modo="random") -> str:
    """Toca música de playlist"""
    nome = nome.lower().strip()
    
    # Lista playlists se não especificada
    if nome in ["listar", "playlists", "todas"]:
        playlists = listar_playlists()
        if not playlists:
            return "Nenhuma playlist encontrada. Crie a pasta 'playlists/'"
        return "Playlists disponíveis: " + "; ".join(playlists)
    
    pasta = PLAYLIST_DIR / nome
    if not pasta.exists():
        return f"Playlist '{nome}' não encontrada. Diga 'playlists' para listar."
    
    # Lista músicas válidas
    musicas = [
        f for f in pasta.iterdir() 
        if f.is_file() and f.suffix.lower() in MUSICA_EXTENSOES
    ]
    
    if not musicas:
        return f"Nenhuma música válida em '{nome}'. Use .mp3, .wav, .flac, etc."
    
    # Escolhe música
    if modo == "random":
        musica = random.choice(musicas)
    else:
        musica = musicas[0]  # Primeira
    
    return _reproduzir_musica(musica)

def _reproduzir_musica(musica: Path) -> str:
    """Reproduz música com player apropriado"""
    try:
        nome_musica = musica.name
        
        # Players por SO
        players = {
            "linux": ["xdg-open", "mpv", "vlc", "cvlc"],
            "darwin": ["open", "afplay"],  # macOS
            "windows": ["start", musica]   # Windows usa 'start'
        }
        
        player_cmd = players.get(SO, players["linux"])
        
        for cmd in player_cmd:
            try:
                if SO == "windows":
                    subprocess.Popen(cmd, shell=True)
                else:
                    subprocess.Popen([cmd, str(musica)], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                logger.info(f"🎵 Tocando: {nome_musica}")
                return f"Tocando '{nome_musica}'"
            except (FileNotFoundError, subprocess.SubprocessError):
                continue
        
        return f"Player não encontrado para '{nome_musica}'"
        
    except Exception as e:
        logger.error(f"Erro música {musica}: {e}")
        return "Erro ao reproduzir música"

# =========================
# TESTES
# =========================
def testar_comandos():
    """Testa todos os comandos"""
    print("🧪 Testando comandos...")
    
    print("📅 Data:", comando_data())
    print("🕐 Horário:", comando_horario())
    print("🧮 15 + 23 * 2 =", calcular("15 mais 23 vezes 2"))
    
    print("🎵 Playlists:", listar_playlists())
    print("🌐 YouTube:", abrir_site("youtube"))
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    testar_comandos()