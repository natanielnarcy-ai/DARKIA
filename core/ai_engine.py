"""
DARKIA V2
Motor de inteligência integrado com memória estruturada.

Este módulo:
- entende perguntas básicas sobre o usuário;
- consulta a memória estruturada;
- conhece os criadores da DARKIA;
- não transforma respostas da DARKIA em memórias;
- possui uma camada preparada para integração com uma IA externa.
"""

import re

from core.memory import (
    learn_from_user,
    get_user_fact,
    get_creators,
    get_user_facts,
    add_history,
)


# ============================================================
# IDENTIDADE
# ============================================================

DARKIA_NAME = "DARKIA"
DARKIA_VERSION = "2.0"


# ============================================================
# UTILITÁRIOS
# ============================================================

def normalize(text):
    """Normaliza texto para facilitar a compreensão."""

    if not isinstance(text, str):
        return ""

    text = text.strip().lower()

    # Pequena normalização de acentos
    replacements = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return re.sub(r"\s+", " ", text).strip()


# ============================================================
# FORMATAR CRIADORES
# ============================================================

def creators_text():
    """Monta uma resposta com os criadores da DARKIA."""

    creators = get_creators()

    creator_1 = creators.get("criador_1", {})
    creator_2 = creators.get("criador_2", {})

    name_1 = creator_1.get("nome", "BG")
    full_1 = creator_1.get("nome_completo", "Basilua")

    name_2 = creator_2.get("nome", "Ibram")
    full_2 = creator_2.get("nome_completo", "Marbi")

    return (
        f"Os meus criadores são {name_1} ({full_1}) "
        f"e {name_2} ({full_2}). 🤖🧠"
    )


# ============================================================
# RESPOSTA SOBRE O NOME DO USUÁRIO
# ============================================================

def user_name_response():
    """Responde usando o nome armazenado na memória."""

    name = get_user_fact("nome")

    if not name:
        artist_name = get_user_fact("nome_artistico")

        if artist_name:
            return f"O teu nome artístico é {artist_name}. 🧠"

        return (
            "Ainda não sei o teu nome. "
            "Podes dizer: 'Meu nome é ...'. 🧠"
        )

    return f"O teu nome é {name}. 🧠"


# ============================================================
# MEMÓRIA DO USUÁRIO
# ============================================================

def user_memory_response():
    """Mostra apenas fatos estruturados conhecidos."""

    facts = get_user_facts()

    if not facts:
        return (
            "Ainda não tenho informações pessoais guardadas "
            "sobre ti. 🧠"
        )

    parts = []

    if facts.get("nome"):
        parts.append(f"nome: {facts['nome']}")

    if facts.get("nome_artistico"):
        parts.append(
            f"nome artístico: {facts['nome_artistico']}"
        )

    if facts.get("atividade"):
        parts.append(
            f"atividade: {facts['atividade']}"
        )

    if not parts:
        return (
            "Tenho algumas informações guardadas, "
            "mas ainda não há fatos suficientes para mostrar."
        )

    return (
        "🧠 Estas são algumas informações que lembro sobre ti:\n"
        + "\n".join(f"• {item}" for item in parts)
    )


# ============================================================
# DETECTAR PERGUNTAS
# ============================================================

def is_name_question(text):
    """Detecta perguntas sobre o nome."""

    normalized = normalize(text)

    patterns = [
        "qual e o meu nome",
        "qual é o meu nome",
        "qual meu nome",
        "como eu me chamo",
        "como me chamo",
        "voce sabe meu nome",
        "tu sabes meu nome",
        "sabes o meu nome",
        "lembra do meu nome",
        "lembras do meu nome",
    ]

    return any(
        pattern in normalized
        for pattern in patterns
    )


def is_creator_question(text):
    """Detecta perguntas sobre os criadores."""

    normalized = normalize(text)

    patterns = [
        "quem sao os teus criadores",
        "quem são os teus criadores",
        "quem te criou",
        "quem criou voce",
        "quem criou voce",
        "quem criou a darkia",
        "quem sao seus criadores",
        "quem são seus criadores",
        "quem fez a darkia",
        "quem fez voce",
    ]

    return any(
        pattern in normalized
        for pattern in patterns
    )


def is_memory_question(text):
    """Detecta perguntas sobre o que a DARKIA lembra."""

    normalized = normalize(text)

    patterns = [
        "o que voce lembra de mim",
        "o que voce lembra sobre mim",
        "o que tu lembras de mim",
        "o que tu lembras sobre mim",
        "o que sabes sobre mim",
        "o que sabe sobre mim",
        "o que voce sabe sobre mim",
        "mostra minha memoria",
        "mostra a minha memoria",
        "minha memoria",
        "minha memória",
    ]

    return any(
        pattern in normalized
        for pattern in patterns
    )


# ============================================================
# SAUDAÇÕES
# ============================================================

def greeting_response(text):
    """Responde a saudações simples."""

    normalized = normalize(text)

    greetings = [
        "oi",
        "ola",
        "olá",
        "bom dia",
        "boa tarde",
        "boa noite",
        "hey",
        "hello",
    ]

    if normalized in greetings:
        return "Olá! Eu sou a DARKIA. 🤖🧠"

    return None


# ============================================================
# RESPOSTAS BÁSICAS
# ============================================================

def basic_response(text):
    """Respostas simples sem necessidade de IA externa."""

    normalized = normalize(text)

    greeting = greeting_response(text)

    if greeting:
        return greeting

    if normalized in [
        "quem e voce",
        "quem é voce",
        "quem es tu",
        "quem és tu",
    ]:
        return (
            "Eu sou a DARKIA, uma inteligência artificial "
            "em desenvolvimento. 🤖🧠"
        )

    if normalized in [
        "o que e darkia",
        "o que é darkia",
    ]:
        return (
            "Eu sou a DARKIA, uma IA criada para conversar, "
            "aprender fatos importantes sobre o usuário "
            "e evoluir com o projeto."
        )

    return None


# ============================================================
# PROCESSAR MENSAGEM
# ============================================================

def process_message(message):
    """
    Processa uma mensagem do usuário.

    A ordem é importante:
    1. Aprende fatos do usuário.
    2. Responde perguntas sobre memória.
    3. Responde identidade/criadores.
    4. Responde perguntas básicas.
    5. Caso não saiba, retorna None para que outra
       camada possa chamar uma IA externa.
    """

    if not isinstance(message, str):
        return "Não consegui entender essa mensagem."

    message = message.strip()

    if not message:
        return "Escreve alguma coisa para eu responder. 🤖"

    # --------------------------------------------------------
    # APRENDER SOMENTE A PARTIR DA MENSAGEM DO USUÁRIO
    # --------------------------------------------------------

    learned_fact = learn_from_user(message)

    # Guarda a mensagem no histórico.
    # IMPORTANTE: isto NÃO transforma a resposta da DARKIA
    # em memória factual.
    add_history("user", message)

    # --------------------------------------------------------
    # PERGUNTA: NOME
    # --------------------------------------------------------

    if is_name_question(message):
        return user_name_response()

    # --------------------------------------------------------
    # PERGUNTA: CRIADORES
    # --------------------------------------------------------

    if is_creator_question(message):
        return creators_text()

    # --------------------------------------------------------
    # PERGUNTA: MEMÓRIA
    # --------------------------------------------------------

    if is_memory_question(message):
        return user_memory_response()

    # --------------------------------------------------------
    # RESPOSTAS BÁSICAS
    # --------------------------------------------------------

    response = basic_response(message)

    if response:
        return response

    # --------------------------------------------------------
    # FATO RECÉM-APRENDIDO
    # --------------------------------------------------------

    if learned_fact:

        key = learned_fact.get("key")
        value = learned_fact.get("value")

        if key == "nome":
            return (
                f"Prazer em conhecer-te, {value}! "
                f"Vou guardar o teu nome na minha memória. 🧠"
            )

        if key == "nome_artistico":
            return (
                f"Entendido! O teu nome artístico é {value}. "
                f"Vou guardar essa informação. 🎵🧠"
            )

        if key == "atividade":
            return (
                f"Entendido! Vou lembrar que és {value}. 🧠"
            )

    # --------------------------------------------------------
    # SEM RESPOSTA LOCAL
    # --------------------------------------------------------

    return None


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def ask(message):
    """
    Interface principal do motor.

    Retorna uma resposta local quando a DARKIA
    consegue responder diretamente.

    Caso precise de uma IA externa, retorna None.
    """

    return process_message(message)


# ============================================================
# TESTE DIRETO
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("DARKIA V2 - TESTE DO AI ENGINE")
    print("=" * 50)

    tests = [
        "Meu nome é BG San",
        "Qual é o meu nome?",
        "Quem são os teus criadores?",
        "O que você lembra de mim?",
        "Olá",
    ]

    for message in tests:

        print("\nUsuário:")
        print(message)

        response = ask(message)

        print("\nDARKIA:")
        print(response)
