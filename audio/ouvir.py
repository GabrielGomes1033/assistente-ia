import speech_recognition as sr
import numpy as np
import pyaudio
import threading
import time
from pathlib import Path
from core.logging import logger
from typing import Optional, Callable
import queue

class OuvinteVoz:
    """Reconhecimento de voz robusto e otimizado"""
    
    def __init__(self, idioma: str = "pt-BR"):
        self.recognizer = sr.Recognizer()
        self.microphone = None  # ✅ padronizado
        self.idioma = idioma
        self.ultimo_comando = ""
        self.ultimo_tempo = 0
        self.calibrado = False
        self.escutando = False
        self.audio_queue = queue.Queue()
        
        # Configurações ajustáveis
        self.TIMEOUT = 3
        self.PHRASE_LIMIT = 8
        self.SILENCE_DB = 0.5
        self.REPEAT_DELAY = 2
        
        self._inicializar_microfone()
        self.calibrar()
    
    def _inicializar_microfone(self):
        try:
            self.microphone = sr.Microphone()  # ✅ correto
            logger.info(f"✅ Microfone inicializado: {self.microphone}")
        except Exception as e:
            logger.error(f"❌ Erro microfone: {e}")
            raise
    
    def calibrar(self, duracao: float = 2.0):
        try:
            logger.info("🔧 Calibrando microfone...")
            
            with self.microphone as source:  # ✅ corrigido
                self.recognizer.adjust_for_ambient_noise(
                    source, 
                    duration=duracao
                )
            
            self.recognizer.energy_threshold = max(
                self.recognizer.energy_threshold, 
                3000
            )
            self.SILENCE_DB = self.recognizer.energy_threshold / 2000
            
            self.calibrado = True
            logger.info(f"✅ Calibrado! Threshold: {self.SILENCE_DB:.1f}dB")
            
        except Exception as e:
            logger.error(f"❌ Erro calibração: {e}")
            self.calibrado = False
    
    def _reconhecer_audio(self, audio: sr.AudioData) -> Optional[str]:
        engines = [
            ("Google", lambda: self.recognizer.recognize_google(audio, language=self.idioma)),
            ("Whisper", lambda: self.recognizer.recognize_whisper(audio, language=self.idioma)),
        ]
        
        for nome, engine in engines:
            try:
                comando = engine()
                comando = comando.lower().strip()
                
                logger.debug(f"[{nome}] {comando[:50]}...")
                
                if len(comando) >= 2 and not self._eh_repeticao(comando):
                    return comando
                    
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                logger.warning(f"[{nome}] Erro API: {e}")
                continue
            except Exception as e:
                logger.debug(f"[{nome}] Erro: {e}")
                continue
        
        return None
    
    def _eh_repeticao(self, comando: str) -> bool:
        agora = time.time()
        if comando == self.ultimo_comando and (agora - self.ultimo_tempo) < self.REPEAT_DELAY:
            return True
        self.ultimo_comando = comando
        self.ultimo_tempo = agora
        return False
    
    def ouvir(self, timeout: Optional[float] = None, callback: Optional[Callable] = None) -> str:
        if timeout is None:
            timeout = self.TIMEOUT
        
        if not self.calibrado:
            logger.warning("Microfone não calibrado!")
            self.calibrar()
        
        try:
            logger.debug("👂 Ouvindo...")
            
            with self.microphone as source:  # ✅ corrigido
                self.recognizer.pause_threshold = 0.8
                self.recognizer.non_speaking_duration = 0.5
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.PHRASE_LIMIT
                )
            
            comando = self._reconhecer_audio(audio)
            
            if comando:
                logger.info(f"🗣️ Reconhecido: '{comando}'")
                if callback:
                    callback(comando)
                return comando
            
            return ""
            
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            logger.error(f"❌ Erro ouvir: {e}")
            return ""
    
    def ouvir_continuo(self, callback: Callable, intervalo: float = 0.1):
        def loop():
            self.escutando = True
            logger.info("🔄 Escuta contínua ativada")
            
            while self.escutando:
                try:
                    comando = self.ouvir(timeout=1)
                    if comando:
                        callback(comando)
                except Exception as e:
                    logger.debug(f"Loop error: {e}")
                    time.sleep(intervalo)
            
            self.escutando = False
            logger.info("🛑 Escuta contínua parada")
        
        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        return thread
    
    def parar_continuo(self):
        self.escutando = False
    
    def get_nivel_ruido(self) -> float:
        with self.microphone as source:  # ✅ corrigido
            return self.recognizer.energy_threshold / 2000
    
    def ajustar_sensibilidade(self, db: float):
        self.recognizer.energy_threshold = db * 2000
        logger.info(f"Sensibilidade: {db:.1f}dB")


# Instância global
ouvinte = OuvinteVoz("pt-BR")

def ouvir(timeout: Optional[float] = None) -> str:
    return ouvinte.ouvir(timeout)


def processar_comando(comando: str):
    logger.info(f"📥 Comando processado: {comando}")


def testar_ouvinte():
    print("🎤 Testando Ouvinte de Voz...")
    
    comando = ouvir()
    if comando:
        print(f"✅ Reconhecido: '{comando}'")
    
    print("🔄 Escuta contínua...")
    thread = ouvinte.ouvir_continuo(processar_comando)
    time.sleep(10)
    ouvinte.parar_continuo()
    
    print("✅ Teste finalizado!")


if __name__ == "__main__":
    testar_ouvinte()