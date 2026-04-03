def entender_intencao(comando):

    if any(p in comando for p in ["hora", "horário", "agora são"]):
        return "horario"

    if any(p in comando for p in ["data", "dia de hoje", "hoje é"]):
        return "data"

    if any(p in comando for p in ["pesquisar", "buscar", "procura"]):
        return "pesquisa"

    if any(p in comando for p in ["tocar", "coloca", "reproduz"]):
        if "rap" in comando:
            return "rap"
        if "rock" in comando:
            return "rock"
        if "sertanejo" in comando:
            return "sertanejo"

    if "tarefa" in comando or any(p in comando for p in ["adicionar", "criar", "nova"]):

        if any(p in comando for p in ["adicionar", "criar", "nova"]):
            return "add_tarefa"

        if any(p in comando for p in ["remover", "deletar", "excluir"]):
            return "remover_tarefa"

        if any(p in comando for p in ["listar", "minhas", "ver"]):
            return "listar_tarefa"
        
        if "piada" in comando:
            return "piada"

    return None