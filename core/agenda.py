import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from core.logging import logger

# 📁 Configuração de caminhos
PASTA_DATA = Path("data")
ARQUIVO_AGENDA = PASTA_DATA / "agenda.json"

class Agenda:
    """Gerenciador completo de tarefas com persistência JSON"""
    
    def __init__(self):
        self._garantir_estrutura()
    
    def _garantir_estrutura(self):
        """Cria pastas e arquivo inicial se necessário"""
        PASTA_DATA.mkdir(exist_ok=True)
        
        if not ARQUIVO_AGENDA.exists():
            self._salvar([])
    
    def _carregar(self) -> List[Dict]:
        """Carrega tarefas do JSON com validação"""
        try:
            if not ARQUIVO_AGENDA.exists():
                return []
            
            with open(ARQUIVO_AGENDA, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            # Valida e corrige estrutura
            tarefas = []
            for item in dados:
                if isinstance(item, dict) and 'texto' in item:
                    tarefas.append(self._normalizar_tarefa(item))
                elif isinstance(item, str):
                    tarefas.append({'texto': item, 'id': len(tarefas)+1, 'data': None})
            
            logger.debug(f"Carregadas {len(tarefas)} tarefas")
            return tarefas
            
        except (json.JSONDecodeError, PermissionError) as e:
            logger.error(f"Erro ao carregar agenda: {e}")
            return []
    
    def _salvar(self, tarefas: List[Dict]):
        """Salva tarefas no JSON"""
        try:
            with open(ARQUIVO_AGENDA, 'w', encoding='utf-8') as f:
                json.dump(tarefas, f, ensure_ascii=False, indent=2)
            logger.debug(f"Salvas {len(tarefas)} tarefas")
        except Exception as e:
            logger.error(f"Erro ao salvar agenda: {e}")
    
    def _normalizar_tarefa(self, tarefa: Dict) -> Dict:
        """Normaliza estrutura da tarefa"""
        return {
            'id': tarefa.get('id', 0),
            'texto': tarefa.get('texto', ''),
            'data_criacao': tarefa.get('data_criacao', datetime.now().isoformat()),
            'data': tarefa.get('data'),  # Data de vencimento opcional
            'concluida': tarefa.get('concluida', False)
        }
    
    def _parse_data(self, texto: str) -> Optional[datetime]:
        """Extrai data do texto (amanhã, sexta, 15/10)"""
        texto = texto.lower()
        
        # Hoje/amanhã
        if 'amanhã' in texto:
            return datetime.now() + timedelta(days=1)
        if 'hoje' in texto:
            return datetime.now()
        
        # Dias da semana
        dias = {
            'segunda': 0, 'terça': 1, 'quarta': 2, 'quinta': 3,
            'quinta-feira': 3, 'sexta': 4, 'sábado': 5, 'domingo': 6
        }
        for dia, num in dias.items():
            if dia in texto:
                hoje = datetime.now().weekday()
                dias_a_frente = (num - hoje) % 7
                if dias_a_frente == 0:
                    dias_a_frente = 7
                return datetime.now() + timedelta(days=dias_a_frente)
        
        # Data numérica dd/mm
        padrao = r'(\d{1,2})/(\d{1,2})'
        match = re.search(padrao, texto)
        if match:
            dia, mes = int(match.group(1)), int(match.group(2))
            try:
                return datetime(datetime.now().year, mes, dia)
            except ValueError:
                pass
        
        return None
    
    # =========================
    # OPERAÇÕES PÚBLICAS
    # =========================
    
    def adicionar_tarefa(self, comando: str) -> str:
        """Adiciona nova tarefa"""
        tarefas = self._carregar()
        
        texto = re.sub(r'(?:adicionar|criar|nova)\s+tarefa\s+', '', comando, flags=re.IGNORECASE).strip()
        if not texto:
            return "Qual é a tarefa que você quer adicionar?"
        
        # Extrai data opcional
        data = self._parse_data(texto)
        if data:
            texto = re.sub(r'\b(amanhã|hoje|segunda|terça|quarta|quinta|sexta|sábado|domingo|\d{1,2}/\d{1,2})\b', '', texto).strip()
        
        nova_tarefa = {
            'id': len(tarefas) + 1,
            'texto': texto,
            'data_criacao': datetime.now().isoformat(),
            'data': data.isoformat() if data else None,
            'concluida': False
        }
        
        tarefas.append(nova_tarefa)
        self._salvar(tarefas)
        
        data_str = f" para {data.strftime('%d/%m')} " if data else " "
        return f"✅ Tarefa '{texto[:50]}...' adicionada{data_str}"
    
    def listar_tarefas(self, filtro: str = "todas") -> str:
        """Lista tarefas com filtros"""
        tarefas = self._carregar()
        nao_concluidas = [t for t in tarefas if not t['concluida']]
        
        if not tarefas:
            return "🎉 Você não tem tarefas pendentes!"
        
        if filtro == "hoje":
            hoje = datetime.now().date()
            tarefas_hoje = [t for t in nao_concluidas if t.get('data') and 
                           datetime.fromisoformat(t['data']).date() == hoje]
            if not tarefas_hoje:
                return "Nenhuma tarefa para hoje."
            return self._formatar_lista(tarefas_hoje, "hoje")
        
        return self._formatar_lista(nao_concluidas, "pendentes")
    
    def _formatar_lista(self, tarefas: List[Dict], titulo: str) -> str:
        """Formata lista de tarefas"""
        if not tarefas:
            return f"Nenhuma tarefa {titulo}."
        
        resposta = f"📋 Você tem {len(tarefas)} tarefa{'s' if len(tarefas) > 1 else ''} {titulo}:"
        
        for tarefa in tarefas:
            status = "✅" if tarefa['concluida'] else "⭕"
            data_str = f" ({datetime.fromisoformat(tarefa['data']).strftime('%d/%m')})" if tarefa.get('data') else ""
            resposta += f"\n{status} {tarefa['id']}: {tarefa['texto']}{data_str}"
        
        return resposta
    
    def remover_tarefa(self, comando: str) -> str:
        """Remove tarefa por número ou texto"""
        tarefas = self._carregar()
        nao_concluidas = [t for t in tarefas if not t['concluida']]
        
        if not nao_concluidas:
            return "Não há tarefas para remover."
        
        # Tenta extrair número
        numeros = re.findall(r'\b(\d+)\b', comando)
        if numeros:
            try:
                num = int(numeros[0])
                idx = next((i for i, t in enumerate(tarefas) if t['id'] == num), None)
                if idx is not None:
                    tarefa = tarefas.pop(idx)
                    self._salvar(tarefas)
                    return f"🗑️ Tarefa {num} removida: '{tarefa['texto'][:30]}...'"
            except ValueError:
                pass
        
        # Busca por texto
        texto = re.sub(r'(?:remover|deletar|excluir)\s+tarefa\s+', '', comando, flags=re.IGNORECASE).strip()
        for i, tarefa in enumerate(tarefas):
            if texto.lower() in tarefa['texto'].lower():
                removida = tarefas.pop(i)
                self._salvar(tarefas)
                return f"🗑️ Tarefa removida: '{removida['texto'][:30]}...'"
        
        return "Não encontrei essa tarefa. Diga 'listar tarefas' primeiro."
    
    def limpar_agenda(self) -> str:
        """Remove todas as tarefas"""
        self._salvar([])
        return "🧹 Agenda limpa! Todas as tarefas foram removidas."
    
    def concluir_tarefa(self, numero: int) -> str:
        """Marca tarefa como concluída"""
        tarefas = self._carregar()
        tarefa = next((t for t in tarefas if t['id'] == numero), None)
        
        if not tarefa:
            return f"Tarefa {numero} não encontrada."
        
        tarefa['concluida'] = True
        self._salvar(tarefas)
        return f"🎉 Tarefa {numero} marcada como concluída: '{tarefa['texto'][:30]}...'"

# Instância global
agenda = Agenda()

# Funções compatíveis (para código existente)
def adicionar_tarefa(comando: str) -> str:
    return agenda.adicionar_tarefa(comando)

def listar_tarefas() -> str:
    return agenda.listar_tarefas()

def remover_tarefa(comando: str) -> str:
    return agenda.remover_tarefa(comando)

def limpar_agenda() -> str:
    return agenda.limpar_agenda()

# Teste
def testar_agenda():
    print("🧪 Testando Agenda...")
    print(adicionar_tarefa("adicionar tarefa comprar leite amanhã"))
    print(adicionar_tarefa("adicionar tarefa reunião sexta"))
    print(listar_tarefas())
    print("✅ Testes OK!")

if __name__ == "__main__":
    testar_agenda()