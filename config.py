import os

# Configuração da DARKIA
DARKIA_NAME = "DARKIA"
DARKIA_VERSION = "2.0"

# A chave NÃO fica escrita neste arquivo.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Modelo utilizado pela IA.
OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6"
)
