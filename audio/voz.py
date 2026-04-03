#!/usr/bin/env python3
"""
Síntese de voz simples e robusta com Piper TTS
Compatível com código original + melhorias modernas
"""

import os
import subprocess
import time
import sys
from pathlib import Path
from typing import Optional

# Configurações (fáceis de alterar)
MODELO = "pt_BR-faber-medium.onnx"
PIPER_PATH = "./piper/piper"
ARQUIVO_SAIDA = "voz.wav"

class VozSimples:
    """TTS simples e direto - versão PRO do seu código"""
    
    def __init__(self, modelo: str = MODELO, piper_path: str = PIPER_PATH):
        self.modelo = modelo
        self.piper = Path(piper_path)
        self.arquivo = Path(ARQUIVO_SAIDA)
        self._verificar_setup()
    
    def _verificar_setup(self):
        """Verifica se tudo está pronto"""
        erros = []
        
        if not self.piper.exists():
            erros.append(f"❌ Piper não encontrado: {self.piper}")
        
        if not Path(self.modelo).exists():
            erros.append(f"❌ Modelo não encontrado: {self.modelo}")
        
        if erros:
            print("\n".join(erros))
            print("💡 Baixe Piper: https://github.com/rhasspy/piper/releases")
            sys.exit(1)
    
    def _limpar_texto(self, texto: str) -> str:
        """Limpa texto para shell"""
        # Escapa aspas e caracteres especiais
        texto = texto.replace('"', '\\"')
        texto = texto.replace("'", "\\'")
        return texto.strip()
    
    def falar(self, texto: str, debug: bool = False) -> bool:
        """
        Fala texto (compatível com seu código original)
        
        Args:
            texto: O que falar
            debug: Mostra comandos executados
        """
        if not texto or not texto.strip():
            print("Delta: [vazio]")
            return False
        
        print(f"Delta: {texto}")
        
        try:
            # Comando Piper (seu estilo original!)
            comando = (
                f'echo "{self._limpar_texto(texto)}" | '
                f'{self.piper} -m {self.modelo} -f {self.arquivo}'
            )
            
            if debug:
                print(f"🔧 Executando: {comando}")
            
            # Executa síntese
            resultado = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if resultado.returncode != 0:
                print(f"❌ Erro Piper: {resultado.stderr[:100]}")
                return False
            
            # Toca áudio (seu estilo original!)
            if self.arquivo.exists():
                tocar_cmd = f"aplay {self.arquivo}"
                if debug:
                    print(f"🔊 Tocando: {tocar_cmd}")
                
                os.system(tocar_cmd)
                return True
            else:
                print("❌ Arquivo de áudio não gerado")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout na síntese")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Interrompido")
            return False
        except Exception as e:
            print(f"💥 Erro: {e}")
            return False
        finally:
            # Limpeza automática
            self._limpar()

    def _limpar(self):
        """Remove arquivo temporário"""
        try:
            if self.arquivo.exists():
                self.arquivo.unlink()
        except:
            pass
    
    def teste(self):
        """Teste rápido"""
        frases = [
            "Olá! Delta funcionando perfeitamente!",
            "Seu assistente de voz está pronto.",
            "Posso ajudar com qualquer coisa!"
        ]
        
        print("🎤 Testando síntese...")
        for frase in frases:
            self.falar(frase)
            time.sleep(0.5)
        print("✅ Teste concluído!")

# Instância global (DROP-IN replacement do seu código)
voz = VozSimples()

# Função EXATA do seu código original (compatibilidade 100%)
def falar(texto: str):
    voz.falar(texto)

# Comandos extras (bônus!)
def falar_debug(texto: str):
    """Fala com debug"""
    voz.falar(texto, debug=True)

def configurar(modelo_novo: str, piper_path: str = PIPER_PATH):
    """Configura novos caminhos"""
    global voz
    voz = VozSimples(modelo_novo, piper_path)

if __name__ == "__main__":
    # Teste automático
    if len(sys.argv) > 1:
        falar(" ".join(sys.argv[1:]))
    else:
        voz.teste()