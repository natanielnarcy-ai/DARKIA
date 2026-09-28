from datetime import datetime
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
import re

from core.memory import (
    save_memory,
    get_recent_memory,
    learn_from_user,
    get_user_fact,
    get_user_facts,
    get_creators,
    add_history,
)


DARKIA_NAME = "DARKIA"
DARKIA_VERSION = "2.0"


# ==========================================================
# UTILITÁRIOS
# ==========================================================

def limpar(texto):
    if not isinstance(texto, str):
        return ""

    return texto.lower().strip()


def hora_atual():
    return datetime.now().strftime("%H:%M")


def data_atual():
    return datetime.now().strftime("%d/%m/%Y")


# ==========================================================
# CÁLCULO
# ==========================================================

def calcular(expressao):
    expressao = expressao.replace("^", "**").strip()

    if not re.fullmatch(
        r"[0-9+\-*/%.() \t]+",
        expressao
    ):
        return None

    try:
        return eval(
            expressao,
            {"__builtins__": {}},
            {}
        )
    except Exception:
        return None


# ==========================================================
# MEMÓRIA ESTRUTURADA
# ==========================================================

def resposta_nome():
    """
    Responde usando a memória estruturada.
    """

    nome = get_user_fact("nome")

    if nome:
        return f"O teu nome é {nome}. 🧠"

    nome_artistico = get_user_fact(
        "nome_artistico"
    )

    if nome_artistico:
        return (
            f"O teu nome artístico é "
            f"{BG.San}. 🎵🧠"
        )

    return (
        "Ainda não sei o teu nome. "
        "Podes dizer: 'Meu nome é ...'. 🧠"
    )


def resposta_criadores():
    """
    Obtém os criadores da memória estruturada.
    """

    creators = get_creators()

    criador_1 = creators.get(
        "criador_1",
        {}
    )

    criador_2 = creators.get(
        "criador_2",
        {}
    )

    nome_1 = criador_1.get(
        "nome",
        "BG"
    )

    completo_1 = criador_1.get(
        "nome_completo",
        "Basilua Geraldo"
    )

    nome_2 = criador_2.get(
        "nome",
        "Ibram"
    )

    completo_2 = criador_2.get(
        "nome_completo",
        "Francisco Augusto"
    )

    return (
        "Os meus criadores são:\n\n"
        f"👤 {nome_1} ({completo_1})\n"
        f"👤 {nome_2} ({completo_2})\n\n"
        " Eles são os meus criadores."
    )


def resposta_memoria():
    """
    Mostra todos os fatos estruturados do usuário.

    Não mostra respostas anteriores da DARKIA
    como se fossem memórias pessoais.
    """

    fatos = get_user_facts()

    if not fatos:
        return (
            "🧠 Ainda não tenho informações pessoais "
            "guardadas sobre ti."
        )

    nomes = {
        "nome": "Nome",
        "nome_artistico": "Nome artístico",
        "atividade": "Atividade",
        "idade": "Idade",
        "escola": "Escola",
        "curso": "Curso",
        "materia_favorita": "Matéria favorita",
        "gosto": "Gosto",
        "jogo": "Jogo favorito",
        "artista_favorito": "Artista favorito",
        "projeto": "Projeto"
    }

    linhas = []

    for chave, valor in fatos.items():

        if valor is None or valor == "":
            continue

        titulo = nomes.get(
            chave,
            chave.replace("_", " ").capitalize()
        )

        linhas.append(
            f"• {titulo}: {valor}"
        )

    if not linhas:
        return (
            "🧠 Tenho memória estruturada, "
            "mas ainda não encontrei fatos pessoais."
        )

    return (
        "🧠 Estas são algumas informações "
        "que lembro sobre ti:\n\n"
        + "\n".join(linhas)
    )


# ==========================================================
# DETECÇÃO DE PERGUNTAS SOBRE MEMÓRIA
# ==========================================================

def pergunta_nome(texto):

    frases = [
        "qual é o meu nome",
        "qual e o meu nome",
        "qual meu nome",
        "como eu me chamo",
        "como me chamo",
        "sabes o meu nome",
        "sabe meu nome",
        "voce sabe meu nome",
        "você sabe meu nome",
        "lembras do meu nome",
        "lembra do meu nome",
    ]

    return any(
        frase in texto
        for frase in frases
    )


def pergunta_criadores(texto):

    frases = [
        "quem te criou",
        "quem criou você",
        "quem criou voce",
        "quem são teus criadores",
        "quem sao teus criadores",
        "quem são os teus criadores",
        "quem sao os teus criadores",
        "quem são seus criadores",
        "quem sao seus criadores",
        "quem criou a darkia",
        "quem fez a darkia",
        "quem fez voce",
    ]

    return any(
        frase in texto
        for frase in frases
    )


def pergunta_memoria(texto):

    frases = [
        "o que você lembra",
        "o que voce lembra",
        "o que lembras",
        "o que você lembra de mim",
        "o que voce lembra de mim",
        "o que você sabe sobre mim",
        "o que voce sabe sobre mim",
        "o que sabes sobre mim",
        "lembra de mim",
        "voce lembra de mim",
        "você lembra de mim",
        "mostra minha memoria",
        "mostra a minha memoria",
        "minha memória",
        "minha memoria",
    ]

    return any(
        frase in texto
        for frase in frases
    )


# ==========================================================
# MEMÓRIA DE CONVERSA
# ==========================================================

def procurar_memoria(pergunta, limite=5):
    """
    Procura no histórico apenas quando for necessário.

    IMPORTANTE:
    O histórico é diferente da memória factual.
    """

    memoria = get_recent_memory(100)

    if not memoria:
        return []

    palavras = set(
        re.findall(
            r"\b[a-zA-ZÀ-ÿ0-9]{3,}\b",
            limpar(pergunta)
        )
    )

    ignorar = {
        "que",
        "qual",
        "como",
        "onde",
        "quando",
        "para",
        "com",
        "uma",
        "isso",
        "essa",
        "esse",
        "sobre",
        "você",
        "voce",
        "darkia",
        "pode",
        "posso",
        "meu",
        "minha",
        "teu",
        "tua",
    }

    palavras -= ignorar

    resultados = []

    for item in reversed(memoria):

        # A V2 usa "message".
        # Também aceitamos "content" para compatibilidade
        # com memórias antigas.
        conteudo = item.get(
            "message",
            item.get("content", "")
        )

        texto_memoria = limpar(
            conteudo
        )

        pontos = 0

        for palavra in palavras:

            if palavra in texto_memoria:
                pontos += 1

        if pontos > 0:

            resultados.append(
                (pontos, item)
            )

    resultados.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        item
        for pontos, item
        in resultados[:limite]
    ]


def contexto_memoria(pergunta):

    lembrancas = procurar_memoria(
        pergunta
    )

    if not lembrancas:
        return ""

    linhas = []

    for item in lembrancas:

        role = item.get(
            "role",
            ""
        )

        content = item.get(
            "message",
            item.get("content", "")
        )

        if role == "user":

            linhas.append(
                f"Usuário disse: {content}"
            )

    if not linhas:
        return ""

    return "\n".join(linhas)


# ==========================================================
# IA REAL - OPENAI
# ==========================================================

def resposta_ia(message, history=None):
    """
    Envia a mensagem para a IA quando uma API key
    estiver configurada.

    Sem API key, retorna None para que a DARKIA
    continue usando o cérebro local.
    """

    if not OPENAI_API_KEY:
        return None

    try:
        cliente = OpenAI(
            api_key=OPENAI_API_KEY
        )

        mensagens = []

        if history:
            for item in history[-10:]:
                role = item.get("role")
                content = item.get("content")

                if role in ["user", "assistant"] and content:
                    mensagens.append({
                        "role": role,
                        "content": content
                    })

        mensagens.append({
            "role": "user",
            "content": message
        })

        resposta = cliente.responses.create(
            model=OPENAI_MODEL,
            input=mensagens
        )

        return resposta.output_text.strip()

    except Exception as erro:
        print(f"[DARKIA IA] Erro: {erro}")
        return None


# ==========================================================
# RESPOSTAS LOCAIS
# ==========================================================

def resposta_local(message):

    texto = limpar(message)

    # ------------------------------------------------------
    # APRENDER INFORMAÇÃO DO USUÁRIO
    # ------------------------------------------------------

    fato = learn_from_user(
        message
    )

    # ------------------------------------------------------
    # NOME
    # ------------------------------------------------------

    if pergunta_nome(texto):
        return resposta_nome()

    # ------------------------------------------------------
    # CRIADORES
    # ------------------------------------------------------

    if pergunta_criadores(texto):
        return resposta_criadores()

    # ------------------------------------------------------
    # MEMÓRIA
    # ------------------------------------------------------

    if pergunta_memoria(texto):
        return resposta_memoria()

    # ------------------------------------------------------
    # SAUDAÇÕES
    # ------------------------------------------------------

    if texto in [
        "oi",
        "olá",
        "ola",
        "hey",
        "hello",
        "bom dia",
        "boa tarde",
        "boa noite"
    ]:

        return (
            f"Olá! Eu sou a {DARKIA_NAME}. 🤖🧠\n"
            "Estou online e com a minha memória ativada."
        )

    # ------------------------------------------------------
    # IDENTIDADE
    # ------------------------------------------------------

    if (
        "quem é você" in texto
        or "quem e voce" in texto
        or "quem es tu" in texto
        or "quem és tu" in texto
    ):

        return (
            f"Eu sou a {DARKIA_NAME}, "
            "uma inteligência artificial "
            "com memória estruturada."
        )

    # ------------------------------------------------------
    # VERSÃO
    # ------------------------------------------------------

    if (
        "versão" in texto
        or "versao" in texto
    ):

        return (
            f"Estou atualmente na "
            f"versão {DARKIA_VERSION}."
        )

    # ------------------------------------------------------
    # HORA
    # ------------------------------------------------------

    if (
        "que horas" in texto
        or texto == "hora"
    ):

        return (
            f"Agora são {hora_atual()}."
        )

    # ------------------------------------------------------
    # DATA
    # ------------------------------------------------------

    if (
        "que dia é hoje" in texto
        or "que dia e hoje" in texto
        or "data de hoje" in texto
    ):

        return (
            f"Hoje é {data_atual()}."
        )

    # ------------------------------------------------------
    # CAPACIDADES
    # ------------------------------------------------------

    if (
        "o que você pode fazer" in texto
        or "o que podes fazer" in texto
        or "o que voce pode fazer" in texto
    ):

        return (
            "Posso conversar, fazer cálculos, "
            "ajudar nos estudos, explicar programação "
            "e guardar informações importantes na "
            "minha memória. 🤖🧠"
        )

    # ------------------------------------------------------
    # AGRADECIMENTO
    # ------------------------------------------------------

    if texto in [
        "obrigado",
        "obrigada",
        "valeu",
        "thanks"
    ]:

        return "De nada! 😎"

    # ------------------------------------------------------
    # ESTUDOS
    # ------------------------------------------------------

    if any(
        palavra in texto
        for palavra in [
            "estudar",
            "estudo",
            "matéria",
            "materia",
            "exercício",
            "exercicio"
        ]
    ):

        return (
            "Claro! 📚 Posso ajudar a explicar "
            "a matéria, resolver exercícios "
            "e preparar perguntas para estudar."
        )

    # ------------------------------------------------------
    # ALGORITMOS
    # ------------------------------------------------------

    if "algoritmo" in texto:

        return (
            "Um algoritmo é uma sequência organizada "
            "de passos para resolver um problema "
            "ou realizar uma tarefa."
        )

    # ------------------------------------------------------
    # CONHECIMENTO ESPECÍFICO
    # ------------------------------------------------------

    if "python" in texto and any(
        frase in texto
        for frase in [
            "o que é",
            "o que e",
            "para que serve",
            "explica",
            "fala sobre",
            "serve para quê",
            "serve para que",
            "onde é usado",
            "onde e usado"
        ]
    ):
        return (
            "🐍 Python é uma linguagem de programação de alto nível, "
            "conhecida por ter uma sintaxe simples. "
            "É usada em áreas como automação, desenvolvimento web, "
            "análise de dados, ciência e Inteligência Artificial."
        )

    if "html" in texto and any(
        frase in texto
        for frase in [
            "o que é",
            "o que e",
            "para que serve",
            "explica",
            "fala sobre",
            "serve para quê",
            "serve para que"
        ]
    ):
        return (
            "🌐 HTML é uma linguagem de marcação usada para "
            "estruturar páginas da Web. "
            "Com HTML podemos criar títulos, textos, imagens, "
            "links, listas, formulários e outros elementos."
        )

    if "algoritmo" in texto and any(
        frase in texto
        for frase in [
            "o que é",
            "o que e",
            "explica",
            "fala sobre",
            "para que serve"
        ]
    ):
        return (
            "🧠 Um algoritmo é uma sequência lógica e organizada "
            "de passos usada para resolver um problema ou realizar "
            "uma tarefa."
        )

    # ------------------------------------------------------
    # PROGRAMAÇÃO
    # ------------------------------------------------------

    if not texto.startswith("o que é ") and not texto.startswith("o que e ") and any(
        palavra in texto
        for palavra in [
            "programação",
            "programacao",
            "python",
            "html",
            "javascript",
            "código",
            "codigo"
        ]
    ):

        return (
            "Posso ajudar com programação, "
            "explicar códigos, encontrar erros "
            "e criar exemplos."
        )

    # ------------------------------------------------------
    # CÁLCULO
    # ------------------------------------------------------

    resultado = calcular(
        texto
    )

    if resultado is not None:

        return (
            f"O resultado é {resultado}."
          )

	   
    # ------------------------------------------------------
    # CÉREBRO LOCAL AVANÇADO
    # ------------------------------------------------------

    respostas_inteligentes = {
        "o que é inteligência artificial":
            "Inteligência Artificial (IA) é uma área da computação que cria sistemas capazes de realizar tarefas que normalmente exigem inteligência humana, como compreender linguagem, reconhecer padrões, aprender com dados e resolver problemas.",

        "o que é ia":
            "IA significa Inteligência Artificial. É uma tecnologia que permite aos computadores analisar informações, aprender padrões e realizar tarefas de forma inteligente.",

        "o que é programação":
            "Programação é o processo de criar instruções que um computador pode executar para realizar uma tarefa ou resolver um problema.",

        "o que é python":
            "Python é uma linguagem de programação conhecida pela sintaxe simples e usada em áreas como automação, desenvolvimento web, análise de dados e Inteligência Artificial.",

        "o que é html":
            "HTML é a linguagem de marcação usada para estruturar páginas da Web, como títulos, textos, imagens, links e formulários.",

        "o que é algoritmo":
            "Um algoritmo é uma sequência lógica e organizada de passos usada para resolver um problema ou realizar uma tarefa.",

        "o que é lógica de programação":
            "Lógica de programação é a organização do pensamento em passos e regras para criar soluções que um computador consiga executar.",

        "o que é computador":
            "Um computador é uma máquina eletrônica capaz de receber dados, processá-los, armazená-los e produzir informações.",

        "o que é internet":
            "A Internet é uma rede mundial que conecta computadores, celulares e outros dispositivos para permitir a comunicação e o compartilhamento de informações.",

        "o que é memória":
            "Na DARKIA, a memória é o sistema responsável por guardar informações importantes e histórico das conversas para serem utilizados posteriormente."
    }

    # Procura uma resposta conhecida.
    for pergunta, resposta in respostas_inteligentes.items():

        if texto == pergunta or pergunta in texto:

            return resposta
    # ------------------------------------------------------
    # MEMÓRIA CONTEXTUAL
    # ------------------------------------------------------

    contexto = contexto_memoria(
        message
    )

    if contexto:

        return (
            "🧠 Encontrei algo relacionado "
            "na minha memória:\n\n"
            f"{contexto}"
        )

    # RESPOSTA PADRÃO
    # ------------------------------------------------------

    return (
        f'Entendi: "{message}"\n\n'
        "Ainda estou aprendendo a responder "
        "melhor a esse tipo de mensagem."
    )


# ==========================================================
# CÉREBRO PRINCIPAL
# ==========================================================

def ask_darkia(
    message,
    history=None
):

    if not message or not message.strip():

        return (
            "Escreve alguma coisa "
            "para eu responder. 🤖"
        )

    # ------------------------------------------------------
    # GUARDA A MENSAGEM DO USUÁRIO
    # ------------------------------------------------------

    # save_memory também chama learn_from_user
    # para mensagens do usuário.
    save_memory(
        "user",
        message.strip()
    )

    # ------------------------------------------------------
    # PROCESSA
    # ------------------------------------------------------

    # ------------------------------------------------------
    # IA REAL
    # ------------------------------------------------------

    response = resposta_ia(
        message,
        history
    )

    # ------------------------------------------------------
    # FALLBACK LOCAL
    # ------------------------------------------------------

    if not response:

        response = resposta_local(
            message
        )

    # ------------------------------------------------------
    # GUARDA A RESPOSTA
    # ------------------------------------------------------

    # IMPORTANTE:
    # save_memory("assistant", ...) guarda somente
    # no histórico.
    #
    # A resposta da DARKIA NÃO vira fato.
    save_memory(
        "assistant",
        response
    )

    return response


# ==========================================================
# TESTE PELO TERMINAL
# ==========================================================

if __name__ == "__main__":

    print("=" * 55)
    print("DARKIA V2 - CÉREBRO + MEMÓRIA ESTRUTURADA")
    print("Memória persistente: ATIVA")
    print("Digite 'sair' para terminar.")
    print("=" * 55)

    while True:

        try:

            mensagem = input(
                "TU: "
            ).strip()

            if mensagem.lower() in [
                "sair",
                "exit",
                "quit"
            ]:

                print(
                    "DARKIA: Até logo. 👋"
                )

                break

            resposta = ask_darkia(
                mensagem
            )

            print(
                "DARKIA:",
                resposta
            )

        except KeyboardInterrupt:

            print(
                "\nDARKIA: Encerrando..."
            )

            break

        except Exception as erro:

            print(
                "DARKIA: Ocorreu um erro:",
                erro
            )
