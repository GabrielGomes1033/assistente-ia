import wikipedia

wikipedia.set_lang("pt")


# =========================
# PESQUISA INTELIGENTE 
# =========================

def pesquisar_google(termo):

    try:
        termo = termo.strip().lower()

        if termo == "":
            return "Você não informou o que deseja pesquisar."

        resultado = wikipedia.summary(termo, sentences=3)

        return resultado

    except wikipedia.exceptions.DisambiguationError as e:
        return f"Encontrei vários resultados. Seja mais específico, como: {e.options[:3]}"

    except wikipedia.exceptions.PageError:
        return "Não encontrei informações sobre isso."

    except Exception:
        return "Tive um problema ao pesquisar."


# =========================
# RESUMO DE TEXTO 
# =========================

def resumir_texto(texto):

    if not texto or len(texto) < 50:
        return texto

    frases = texto.split(". ")

    resumo = ". ".join(frases[:2])

    return resumo + "."
