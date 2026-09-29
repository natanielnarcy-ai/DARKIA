from core.ai_engine import ask


def process_command(message):
    """
    Processa comandos recebidos pelo WhatsApp.
    """

    if not isinstance(message, str):
        return None

    message = message.strip()

    if not message:
        return None

    command = message.lower()

    # -------------------------
    # PING
    # -------------------------

    if command in ("!ping", "/ping"):
        return "DARKIA: 🟢 Online."

    # -------------------------
    # MENU
    # -------------------------

    if command in ("!menu", "/menu"):
        return """DARKIA — MENU 🤖

!ping — verificar se estou online
!menu — mostrar este menu
!ia <pergunta> — conversar com a DARKIA
!status — estado do sistema"""

    # -------------------------
    # STATUS
    # -------------------------

    if command in ("!status", "/status"):
        return """DARKIA STATUS

Sistema: 🟢 Online
Núcleo: DARKIA AI
Modo: WhatsApp
Comandos: 🟢 Ativos"""

    # -------------------------
    # IA
    # -------------------------

    if command.startswith("!ia ") or command.startswith("/ia "):

        pergunta = message[4:].strip()

        if not pergunta:
            return "DARKIA: Escreve uma pergunta depois de !ia."

        resposta = ask(pergunta)

        if resposta:
            return resposta

        return (
            "DARKIA: 🧠 Recebi a tua pergunta, "
            "mas ainda não tenho uma resposta local para ela."
        )

    return None


if __name__ == "__main__":

    print("=" * 50)
    print("DARKIA — TESTE DO MÓDULO WHATSAPP")
    print("=" * 50)

    testes = [
        "!ping",
        "!status",
        "!menu",
        "!ia Olá",
        "!ia Quem são os teus criadores?",
        "!ia O que você lembra de mim?",
    ]

    for mensagem in testes:

        print("\nWhatsApp:")
        print(mensagem)

        resposta = process_command(mensagem)

        print("\nDARKIA:")
        print(resposta)
