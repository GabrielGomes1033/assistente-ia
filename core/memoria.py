import json
import os
import re
import difflib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.logging import logger
import Levenshtein  # pip install python-Levenshtein

# 📁 Configuração
PASTA_DATA = Path("data")
ARQUIVO_MEMORIA = PASTA_DATA / "memoria.json"

class Memoria:
    """Sistema de memória persistente e inteligente"""
    
    MAX_ITENS = 1000  # Limite de memória
    SIMILARIDADE_MIN = 0.6  # 60% para busca fuzzy
    
    def __init__(self):
        self._garantir_estrutura()
    
    def _garantir_estrutura(self):
        """Cria estrutura inicial"""
        PASTA_DATA.mkdir(exist_ok=True)
        if not ARQUIVO_MEMORIA.exists():
            self._salvar({})
    
    def _carregar(self) -> Dict:
        """Carrega memória com validação"""
        try:
            if not ARQUIVO_MEMORIA.exists():
                return {}
            
            with open(ARQUIVO_MEMORIA, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            # Valida e atualiza estrutura
            memoria = {}
            for chave, valor in dados.items():
                if isinstance(valor, dict):
                    memoria[chave] = self._normalizar_item(valor)
                else:
                    memoria[chave] = {
                        'valor': valor,
                        'data_aprendizado': datetime.now().isoformat(),
                        'usos': 0
                    }
            
            logger.debug(f"Memória carregada: {len(memoria)} itens")
            return memoria
            
        except Exception as e:
            logger.error(f"Erro carregando memória: {e}")
            return {}
    
    def _salvar(self, memoria: Dict):
        """Salva memória de forma segura"""
        try:
            # Limpa itens antigos/inativos
            memoria_limpa = {
                k: v for k, v in memoria.items() 
                if v.get('usos', 0) > 0 or (datetime.now() - datetime.fromisoformat(v['data_aprendizado'])).days < 90
            }
            
            with open(ARQUIVO_MEMORIA, 'w', encoding='utf-8') as f:
                json.dump(memoria_limpa, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Memória salva: {len(memoria_limpa)} itens")
            
        except Exception as e:
            logger.error(f"Erro salvando memória: {e}")
    
    def _normalizar_item(self, item: Dict) -> Dict:
        """Padroniza estrutura de item"""
        return {
            'valor': item.get('valor', ''),
            'data_aprendizado': item.get('data_aprendizado', datetime.now().isoformat()),
            'usos': item.get('usos', 0),
            'categoria': item.get('categoria', 'geral')
        }
    
    def _extrair_chave_valor(self, comando: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrai chave e valor de 'X é Y'"""
        # Padrões melhorados
        padroes = [
            r'(.*?)\s+(?:é|significa|quer dizer)\s+(.*)',  # "nome é João"
            r'(?:defina|definição de)\s+(.*?)\s+(?:como|é)\s+(.*)',  # "defina amor como sentimento"
        ]
        
        comando = comando.lower().strip()
        for padrao in padroes:
            match = re.match(padrao, comando)
            if match:
                chave, valor = match.groups()
                return chave.strip(), valor.strip()
        
        return None, None
    
    def _busca_fuzzy(self, termo: str, memoria: Dict) -> List[Tuple[str, float, str]]:
        """Busca aproximada com pontuação"""
        resultados = []
        
        termo_limpo = re.sub(r'[^a-záàâãéèêíïóôõöúç]', '', termo.lower())
        
        for chave, item in memoria.items():
            chave_limpa = re.sub(r'[^a-záàâãéèêíïóôõöúç]', '', chave.lower())
            
            # Distância Levenshtein
            similaridade = Levenshtein.ratio(termo_limpo, chave_limpa)
            
            # Substring
            if termo_limpo in chave_limpa or chave_limpa in termo_limpo:
                similaridade = max(similaridade, 0.8)
            
            if similaridade >= self.SIMILARIDADE_MIN:
                resultados.append((chave, similaridade, item['valor']))
        
        # Ordena por similaridade
        return sorted(resultados, key=lambda x: x[1], reverse=True)
    
    # =========================
    # API PÚBLICA
    # =========================
    
    def aprender(self, comando: str) -> str:
        """Aprende novo fato"""
        chave, valor = self._extrair_chave_valor(comando)
        
        if not chave or not valor:
            return "O que você quer que eu aprenda? Diga algo como 'nome é João' ou 'capital do Brasil é Brasília'"
        
        memoria = self._carregar()
        
        # Normaliza chave
        chave = chave.strip().title()
        
        # Evita duplicatas
        if chave in memoria and memoria[chave]['valor'].lower() == valor.lower():
            return f"👌 Eu já sabia que {chave} é {valor}"
        
        # Aprende
        memoria[chave] = {
            'valor': valor,
            'data_aprendizado': datetime.now().isoformat(),
            'usos': 1,
            'categoria': self._detectar_categoria(valor)
        }
        
        # Limita tamanho
        if len(memoria) > self.MAX_ITENS:
            memoria = dict(list(memoria.items())[-self.MAX_ITENS:])
        
        self._salvar(memoria)
        return f"🧠 Aprendido! Agora sei que **{chave}** é **{valor}** 🎯"
    
    def lembrar(self, comando: str) -> str:
        """Lembra informação salva"""
        memoria = self._carregar()
        
        if not memoria:
            return "Minha memória está vazia 😅 Me ensine algo primeiro!"
        
        # Remove prefixos
        termo = re.sub(r'^(?:qual é|quem é|o que é|me diga|diga|)\s+', '', comando).strip().lower()
        
        if not termo:
            return "O que você quer que eu lembre?"
        
        # Busca exata
        if termo.title() in memoria:
            item = memoria[termo.title()]
            item['usos'] += 1
            self._salvar(memoria)
            return f"📚 **{termo.title()}** é **{item['valor']}** (usado {item['usos']}x)"
        
        # Busca fuzzy
        resultados = self._busca_fuzzy(termo, memoria)
        
        if resultados:
            melhor = resultados[0]
            chave, similaridade, valor = melhor
            memoria[chave]['usos'] += 1
            self._salvar(memoria)
            
            conf = "🔍" if similaridade < 0.9 else "✅"
            return f"{conf} **{chave}** é **{valor}** (confiança: {similaridade:.0%})"
        
        return f"❓ Não lembro de '{termo}'. Me ensine com 'lembre que {termo} é [resposta]'"
    
    def listar_memoria(self, limite: int = 10) -> str:
        """Lista itens da memória"""
        memoria = self._carregar()
        
        if not memoria:
            return "Memória vazia!"
        
        itens = sorted(memoria.items(), key=lambda x: x[1]['usos'], reverse=True)[:limite]
        
        resposta = f"🧠 Memória ({len(memoria)} itens):\n"
        for chave, item in itens:
            uso = f" ({item['usos']}x)" if item['usos'] > 1 else ""
            resposta += f"• {chave}: {item['valor'][:50]}...{uso}\n"
        
        return resposta
    
    def _detectar_categoria(self, texto: str) -> str:
        """Detecta categoria automática"""
        texto = texto.lower()
        if any(palavra in texto for palavra in ['capital', 'país', 'cidade', 'estado']):
            return 'geografia'
        elif any(palavra in texto for palavra in ['nome', 'quem', 'pessoa']):
            return 'pessoas'
        return 'geral'
    
    def esquecendo(self, chave: str) -> str:
        """Remove item da memória"""
        memoria = self._carregar()
        chave = chave.title()
        
        if chave in memoria:
            del memoria[chave]
            self._salvar(memoria)
            return f"🗑️ Esqueci {chave}"
        
        return f"Não lembro de {chave}"

# Instância global
memoria = Memoria()

# Compatibilidade com código antigo
def aprender(comando: str) -> str:
    return memoria.aprender(comando)

def lembrar(comando: str) -> str:
    return memoria.lembrar(comando)

# Teste completo
def testar_memoria():
    print("🧠 Testando Memória Inteligente...")
    
    print(aprender("capital do Brasil é Brasília"))
    print(aprender("nome do criador é João Silva"))
    print(aprender("linguagem favorita é Python"))
    
    print(lembrar("capital do Brasil"))
    print(lembrar("capital Brasil"))  # Fuzzy search!
    print(lembrar("criador"))
    
    print(memoria.listar_memoria(5))
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    testar_memoria()