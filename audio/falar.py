import subprocess
import time
import os
import tempfile
import threading
import re
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from core.logging import logger

# Configurações globais
MODELO_PADRAO = "pt_BR-faber-medium.onnx"
CONFIG_DIR = Path("config")
VOZES_DISPONIVEIS = {
    "faber": "pt_BR-faber-medium.onnx",
    "default": "pt_BR-faber-medium.onnx"
}

class Voz:
    """Síntese de voz profissional com Piper TTS"""
    
    def __init__(self, modelo: str = MODELO_PADRAO):
        self.modelo = modelo
        self.arquivo_temp = Path(tempfile.gettempdir()) / "delta_voz.wav"
        self.falando = False
        self._setup()
    
    def _setup(self):
        """Configuração inicial"""
        self._verificar_modelo()
        self._criar_dir_temp()
        logger.info(f"🎵 Voz inicializada: {self.modelo}")
    
    def _verificar_modelo(self):
        """Verifica modelo e sugere download"""
        if not Path(self.modelo).exists():
            logger.warning(f"❌ Modelo '{self.modelo}' não encontrado!")
            logger.info("📥 Baixe em: https://huggingface.co/rhasspy/piper-voices")
    
    def _criar_dir_temp(self):
        """Garante diretório temp"""
        self.arquivo_temp.parent.mkdir(exist_ok=True)
    
    def _limpar_texto(self, texto: str) -> str:
        """Sanitiza texto para TTS"""
        # Remove/emula emojis
        emoji_map = {
            '✅': 'ok', '❌': 'erro', '🎵': 'musica', '🧠': 'cerebro',
            '📱': 'celular', '🔥': 'fogo', '🚀': 'foguete'
        }
        
        for emoji, palavra in emoji_map.items():
            texto = texto.replace(emoji, palavra)
        
        # Limpeza técnica
        texto = re.sub(r'[\n\r\t]+', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto.strip())
        texto = texto[:500]  # Limite Piper
        
        return texto
    
    def _gerar_comando_piper(self, texto: str, velocidade: float = 1.0) -> list:
        """Gera comando Piper otimizado"""
        return [
            'echo', texto,
            '|', 'piper',
            '--model', self.modelo,
            '--output_file', str(self.arquivo_temp),
            '--length_scale', str(1.0 / velocidade),
            '--noise_scale', '0.4',
            '--noise_w', '0.8',
            '--quality', 'auto'
        ]
    
    def _reproduzir_audio(self) -> bool:
        """Reprodução cross-platform otimizada"""
        if not self.arquivo_temp.exists():
            return False
        
        players = self._get_players()
        
        for player, args in players:
            try:
                cmd = [player, *args, str(self.arquivo_temp)]
                logger.debug(f"Tocando com: {' '.join(cmd)}")
                
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                proc.wait(timeout=10)
                if proc.returncode == 0:
                    logger.debug(f"✅ Reproduzido com {player}")
                    return True
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
            except Exception as e:
                logger.debug(f"{player} falhou: {e}")
                continue
        
        logger.error("❌ Nenhum player funcionou!")
        return False
    
    def _get_players(self) -> list:
        """Players por sistema operacional"""
        import platform
        sistema = platform.system().lower()
        
        players = {
            'linux': [
                ('aplay', []),
                ('paplay', ['--stream-volume=0.8']),
                ('mpv', ['--no-video', '--audio-no-direct']),
                ('ffplay', ['-nodisp', '-autoexit']),
                ('mpg123', ['-q'])
            ],
            'darwin': [  # macOS
                ('afplay', []),
                ('say', []),  # Fallback
            ],
            'windows': [
                ('powershell', ['-c', f'(Add-Type -AssemblyName System.Speech);(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\"{self._texto_fallback()}\")'])
            ]
        }
        
        return players.get(sistema, players['linux'])
    
    def _texto_fallback(self) -> str:
        """Texto para fallback Windows"""
        try:
            with open(self.arquivo_temp, 'r') as f:
                return f.read()[:100]
        except:
            return "Erro de audio"
    
    def falar(self, texto: str, velocidade: float = 1.0, 
              esperar: bool = True, callback: Optional[Callable] = None) -> bool:
        """
        Sintetiza e fala texto
        
        Args:
            texto: Texto para falar
            velocidade: 0.5 (lento) a 2.0 (rápido)
            esperar: Aguarda terminar?
            callback: Função pós-fala
        """
        if not texto or not texto.strip():
            logger.warning("⚠️ Texto vazio")
            return False
        
        if self.falando:
            logger.debug("⏳ Já está falando...")
            return False
        
        texto_limpo = self._limpar_texto(texto)
        logger.info(f"🗣️  > {texto_limpo[:60]}...")
        
        def _falar_thread():
            self.falando = True
            sucesso = False
            
            try:
                # Gera áudio
                cmd = self._gerar_comando_piper(texto_limpo, velocidade)
                cmd_str = ' '.join(cmd)
                
                logger.debug(f"🎼 Piper: {cmd_str}")
                
                resultado = subprocess.run(
                    cmd_str,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                if resultado.returncode != 0:
                    logger.error(f"❌ Piper: {resultado.stderr[:100]}")
                elif self.arquivo_temp.exists():
                    sucesso = self._reproduzir_audio()
                
            except subprocess.TimeoutExpired:
                logger.error("⏰ Timeout síntese")
            except Exception as e:
                logger.error(f"💥 Erro voz: {e}")
            finally:
                self._limpar_temp()
                self.falando = False
                
                if callback:
                    callback(sucesso)
                
                logger.debug("✅ Fala concluída")
        
        # Thread para não bloquear
        thread = threading.Thread(target=_falar_thread, daemon=True)
        thread.start()
        
        if esperar:
            thread.join()
        
        return True
    
    def _limpar_temp(self):
        """Remove arquivo temporário"""
        try:
            if self.arquivo_temp.exists():
                self.arquivo_temp.unlink()
        except Exception:
            pass
    
    def trocar_modelo(self, novo_modelo: str) -> bool:
        """Troca modelo em runtime"""
        if Path(novo_modelo).exists():
            self.modelo = novo_modelo
            self._verificar_modelo()
            logger.info(f"🔄 Modelo trocado: {novo_modelo}")
            return True
        return False
    
    def teste(self, frases: list = None):
        """Teste completo"""
        if frases is None:
            frases = [
                "Olá! Sou seu assistente Delta.",
                "Teste de síntese funcionando perfeitamente.",
                "Posso ajudar com agenda, cálculos e muito mais!"
            ]
        
        print("🎤 Testando síntese...")
        for i, frase in enumerate(frases, 1):
            print(f"{i}/{len(frases)}: {frase[:40]}...")
            self.falar(frase)
            time.sleep(1)
        
        print("✅ Teste concluído!")

# Instância global
voz = Voz()

# Função compatível
def falar(texto: str, velocidade: float = 1.0):
    return voz.falar(texto, velocidade)

# Comandos rápidos
def falar_lento(texto: str):
    return voz.falar(texto, velocidade=0.8)

def falar_rapido(texto: str):
    return voz.falar(texto, velocidade=1.4)

if __name__ == "__main__":
    voz.teste()