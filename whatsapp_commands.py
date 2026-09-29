def process_command(message):
    message = message.strip()

    if message == "!ping":
        return "DARKIA: 🟢 Online."

    if message == "!menu":
        return (
            "🤖 DARKIA — MENU\n\n"
            "!ping — Verificar se a DARKIA está online\n"
            "!menu — Mostrar este menu\n"
            "!ia <pergunta> — Falar com a IA\n"
            "!status — Ver estado do sistema"
        )

    if message == "!status":
        return (
            "🟢 Sistema online\n"
            "🧠 Núcleo DARKIA AI\n"
            "📱 Modo WhatsApp\n"
            "⚡ Comandos ativos"
        )

    return None
