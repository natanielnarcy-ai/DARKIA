import json
import os
import re
from datetime import datetime

# ============================================================
# DARKIA V2 - MEMÓRIA ESTRUTURADA
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")

# Garante que a pasta data exista
os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# ESTRUTURA PADRÃO
# ============================================================

DEFAULT_MEMORY = {
    "facts": {
        "user": {},
        "darkia": {
            "nome": "DARKIA",
            "versao": "2.0"
        },
        "creators": {
            "criador_1": {
                "nome": "BG",
                "nome_completo": "Basilua"
            },
            "criador_2": {
                "nome": "Ibram",
                "nome_completo": "Marbi"
            }
        }
    },

    "history": []
}


# ============================================================
# CARREGAR MEMÓRIA
# ============================================================

def load_memory():
    """
    Carrega a memória estruturada.
    Se o arquivo não existir ou estiver corrompido,
    cria uma memória nova.
    """

    if not os.path.exists(MEMORY_FILE):
        save_memory_file(DEFAULT_MEMORY)
        return copy_memory(DEFAULT_MEMORY)

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Garante que as estruturas principais existam
        if not isinstance(data, dict):
            data = copy_memory(DEFAULT_MEMORY)

        data.setdefault("facts", {})
        data.setdefault("history", [])

        data["facts"].setdefault("user", {})
        data["facts"].setdefault(
            "darkia",
            {
                "nome": "DARKIA",
                "versao": "2.0"
            }
        )

        data["facts"].setdefault(
            "creators",
            {
                "criador_1": {
                    "nome": "BG",
                    "nome_completo": "Basilua"
                },
                "criador_2": {
                    "nome": "Ibram",
                    "nome_completo": "Marbi"
                }
            }
        )

        return data

    except (json.JSONDecodeError, OSError):
        save_memory_file(DEFAULT_MEMORY)
        return copy_memory(DEFAULT_MEMORY)


# ============================================================
# COPIAR MEMÓRIA
# ============================================================

def copy_memory(data):
    """
    Cria uma cópia independente do dicionário.
    """

    return json.loads(json.dumps(data, ensure_ascii=False))


# ============================================================
# SALVAR ARQUIVO DE MEMÓRIA
# ============================================================

def save_memory_file(data):
    """
    Salva toda a memória no arquivo JSON.
    """

    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        return True

    except OSError as error:
        print(f"[DARKIA MEMORY] Erro ao salvar memória: {error}")
        return False


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalize_text(text):
    """
    Normaliza texto para facilitar comparações.
    """

    if not isinstance(text, str):
        return ""

    return re.sub(
        r"\s+",
        " ",
        text.strip().lower()
    )


# ============================================================
# DETECTAR FATOS DO USUÁRIO
# ============================================================

def extract_user_fact(message):
    """
    Analisa uma mensagem do usuário e tenta encontrar
    informações importantes que podem ser guardadas.

    IMPORTANTE:
    Esta função recebe apenas mensagens do USUÁRIO.
    Respostas da DARKIA nunca devem passar por aqui.
    """

    if not isinstance(message, str):
        return None

    text = message.strip()

    if not text:
        return None

    normalized = normalize_text(text)

    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    patterns = [
        r"^meu nome é\s+(.+)$",
        r"^meu nome e\s+(.+)$",
        r"^eu sou o\s+(.+)$",
        r"^eu sou a\s+(.+)$",
        r"^eu sou\s+(.+)$",
        r"^chamo-me\s+(.+)$",
        r"^me chamo\s+(.+)$"
    ]

    for pattern in patterns:
        match = re.match(pattern, text, re.IGNORECASE)

        if match:
            name = match.group(1).strip()

            # Remove pontuação final
            name = re.sub(r"[.!?]+$", "", name).strip()

            if name:
                return {
                    "category": "user",
                    "key": "nome",
                    "value": name
                }

    # --------------------------------------------------------
    # NOME ARTÍSTICO
    # --------------------------------------------------------

    artist_patterns = [
        r"^meu nome artístico é\s+(.+)$",
        r"^meu nome artistico é\s+(.+)$",
        r"^meu nome artístico e\s+(.+)$",
        r"^meu nome artistico e\s+(.+)$"
    ]

    for pattern in artist_patterns:
        match = re.match(pattern, text, re.IGNORECASE)

        if match:
            artist_name = match.group(1).strip()
            artist_name = re.sub(
                r"[.!?]+$",
                "",
                artist_name
            ).strip()

            if artist_name:
                return {
                    "category": "user",
                    "key": "nome_artistico",
                    "value": artist_name
                }

    # --------------------------------------------------------
    # PROFISSÃO / ATIVIDADE
    # --------------------------------------------------------

    activity_patterns = [
        r"^eu sou estudante$",
        r"^sou estudante$"
    ]

    for pattern in activity_patterns:
        if re.match(pattern, normalized, re.IGNORECASE):
            return {
                "category": "user",
                "key": "atividade",
                "value": "estudante"
            }

    # --------------------------------------------------------
    # NÃO FOI ENCONTRADO UM FATO
    # --------------------------------------------------------

    return None


# ============================================================
# SALVAR FATO DO USUÁRIO
# ============================================================

def save_user_fact(key, value):
    """
    Salva ou atualiza um fato do usuário.
    """

    if not key or value is None:
        return False

    memory = load_memory()

    memory["facts"]["user"][key] = {
        "value": value,
        "updated_at": datetime.now().isoformat()
    }

    return save_memory_file(memory)


# ============================================================
# PROCESSAR MENSAGEM DO USUÁRIO
# ============================================================

def learn_from_user(message):
    """
    Aprende somente fatos extraídos das mensagens do usuário.

    A DARKIA NÃO DEVE usar esta função para suas próprias respostas.
    """

    fact = extract_user_fact(message)

    if not fact:
        return None

    saved = save_user_fact(
        fact["key"],
        fact["value"]
    )

    if saved:
        return fact

    return None


# ============================================================
# BUSCAR FATO
# ============================================================

def get_user_fact(key):
    """
    Retorna um fato específico do usuário.
    """

    memory = load_memory()

    fact = memory["facts"]["user"].get(key)

    if isinstance(fact, dict):
        return fact.get("value")

    return fact


# ============================================================
# OBTER TODAS AS INFORMAÇÕES DO USUÁRIO
# ============================================================

def get_user_facts():
    """
    Retorna todos os fatos conhecidos sobre o usuário.
    """

    memory = load_memory()

    result = {}

    for key, value in memory["facts"]["user"].items():

        if isinstance(value, dict):
            result[key] = value.get("value")
        else:
            result[key] = value

    return result


# ============================================================
# INFORMAÇÕES SOBRE OS CRIADORES
# ============================================================

def get_creators():
    """
    Retorna os criadores oficiais da DARKIA.
    """

    memory = load_memory()

    return memory["facts"].get(
        "creators",
        {}
    )


# ============================================================
# ADICIONAR AO HISTÓRICO
# ============================================================

def add_history(role, message):
    """
    Guarda uma conversa no histórico.

    ATENÇÃO:
    Histórico NÃO é memória factual.

    role:
        user
        assistant
        system
    """

    if not message:
        return False

    if role not in ["user", "assistant", "system"]:
        return False

    memory = load_memory()

    memory["history"].append({
        "role": role,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

    # Limita o histórico para não crescer infinitamente
    memory["history"] = memory["history"][-100:]

    return save_memory_file(memory)


# ============================================================
# COMPATIBILIDADE COM CÓDIGO ANTIGO
# ============================================================

def save_memory(role, message):
    """
    Compatibilidade com versões anteriores.

    IMPORTANTE:
    - Mensagem do usuário -> histórico + tentativa de aprender fato
    - Mensagem da DARKIA -> SOMENTE histórico
    - A resposta da DARKIA NUNCA vira fato
    """

    if not message:
        return False

    if role == "user":

        add_history(
            "user",
            message
        )

        learn_from_user(message)

        return True

    if role == "assistant":

        # NÃO aprende nada da resposta da DARKIA
        return add_history(
            "assistant",
            message
        )

    if role == "system":

        return add_history(
            "system",
            message
        )

    return False


# ============================================================
# HISTÓRICO RECENTE
# ============================================================

def get_recent_memory(limit=20):
    """
    Retorna apenas o histórico recente.
    """

    memory = load_memory()

    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20

    if limit <= 0:
        return []

    return memory["history"][-limit:]


# ============================================================
# MEMÓRIA COMPLETA
# ============================================================

def get_memory():
    """
    Retorna toda a memória estruturada.
    """

    return load_memory()


# ============================================================
# LIMPAR HISTÓRICO
# ============================================================

def clear_history():
    """
    Limpa somente o histórico.

    Os fatos do usuário continuam preservados.
    """

    memory = load_memory()

    memory["history"] = []

    return save_memory_file(memory)


# ============================================================
# LIMPAR MEMÓRIA DO USUÁRIO
# ============================================================

def clear_user_memory():
    """
    Remove somente os fatos armazenados sobre o usuário.
    """

    memory = load_memory()

    memory["facts"]["user"] = {}

    return save_memory_file(memory)


# ============================================================
# APAGAR TODA A MEMÓRIA
# ============================================================

def clear_all_memory():
    """
    Apaga fatos e histórico e restaura a identidade padrão.
    """

    return save_memory_file(
        copy_memory(DEFAULT_MEMORY)
    )


# ============================================================
# RESUMO DA MEMÓRIA
# ============================================================

def memory_summary():
    """
    Cria um resumo simples da memória para a DARKIA.
    """

    memory = load_memory()

    user_facts = memory["facts"].get(
        "user",
        {}
    )

    creators = memory["facts"].get(
        "creators",
        {}
    )

    summary = {
        "usuario": {},
        "darkia": memory["facts"].get(
            "darkia",
            {}
        ),
        "criadores": creators,
        "quantidade_historico": len(
            memory.get("history", [])
        )
    }

    for key, value in user_facts.items():

        if isinstance(value, dict):
            summary["usuario"][key] = value.get(
                "value"
            )
        else:
            summary["usuario"][key] = value

    return summary


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    print("======================================")
    print(" DARKIA V2 - TESTE DA MEMÓRIA")
    print("======================================")

    # Teste de aprendizagem
    test_message = "Meu nome é BG San"

    fact = learn_from_user(test_message)

    print("\nMensagem:")
    print(test_message)

    print("\nFato detectado:")
    print(fact)

    print("\nNome armazenado:")
    print(get_user_fact("nome"))

    print("\nCriadores:")
    print(json.dumps(
        get_creators(),
        ensure_ascii=False,
        indent=4
    ))

    print("\nResumo:")
    print(json.dumps(
        memory_summary(),
        ensure_ascii=False,
        indent=4
    ))

    print("\nMemória funcionando. 🧠")
