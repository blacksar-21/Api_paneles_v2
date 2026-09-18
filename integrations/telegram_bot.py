import asyncio
import httpx

from app.core.config import TELEGRAM_BOT_TOKEN, FASTAPI_BASE_URL

from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

FASTAPI_URL = f"{FASTAPI_BASE_URL}/asistente/chat"


if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "❌ No se encontró TELEGRAM_BOT_TOKEN en el archivo .env"
    )


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "☀️ ¡Hola! Soy tu Asistente de Energía Solar.\n\n"
        "Puedo ayudarte a consultar y analizar "
        "la información de las instalaciones fotovoltaicas.\n\n"

        "Puedes preguntarme, por ejemplo:\n\n"

        "• ¿Cuánta energía generó la instalación 1?\n"
        "• ¿Cuánto consumió la instalación 1?\n"
        "• ¿Cuál instalación genera más?\n"
        "• ¿Cuál tiene mejor rendimiento?\n"
        "• ¿Cuándo tuvo mayor generación la instalación 2?\n"
        "• Muéstrame todas las instalaciones.\n\n"

        "Escribe tu pregunta para comenzar. 🤖☀️"
    )


# ============================================================
# /HELP
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "🤖 COMANDOS DISPONIBLES\n\n"

        "/start - Iniciar el asistente\n"
        "/help - Mostrar ayuda\n"
        "/limpiar - Limpiar mi conversación\n\n"

        "También puedes escribir directamente "
        "cualquier pregunta sobre las instalaciones solares. ☀️"
    )


# ============================================================
# /LIMPIAR
# ============================================================

async def limpiar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user_id = update.effective_user.id

    conversation_id = f"telegram-{user_id}"

    print()
    print("=" * 60)
    print("🧹 LIMPIANDO CONVERSACIÓN")
    print("=" * 60)
    print(f"👤 Usuario: {user_id}")
    print(f"🧠 Conversation ID: {conversation_id}")
    print("=" * 60)

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.delete(
                f"{FASTAPI_BASE_URL}/asistente/chat/"
                f"{conversation_id}"
            )

        if response.status_code == 200:

            await update.message.reply_text(
                "🧹 Conversación limpiada correctamente.\n\n"
                "Puedes comenzar una nueva consulta. ☀️"
            )

            print("✅ Conversación limpiada.")

        else:

            print(
                "❌ FastAPI respondió:",
                response.status_code
            )

            print(response.text)

            await update.message.reply_text(
                "⚠️ No fue posible limpiar la conversación."
            )

    except httpx.ConnectError:

        print("❌ No se pudo conectar con FastAPI.")

        await update.message.reply_text(
            "❌ No pude conectarme con la API.\n\n"
            "Asegúrate de que FastAPI esté "
            "ejecutándose en el puerto 8000."
        )

    except httpx.TimeoutException:

        print("❌ Timeout limpiando conversación.")

        await update.message.reply_text(
            "⏳ La operación tardó demasiado.\n\n"
            "Intenta nuevamente."
        )

    except Exception as error:

        print(
            "❌ Error limpiando conversación:",
            repr(error)
        )

        await update.message.reply_text(
            "❌ Ocurrió un error al limpiar la conversación."
        )


# ============================================================
# MENSAJE DEL USUARIO
# ============================================================

async def mensaje_usuario(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    mensaje = update.message.text

    user_id = update.effective_user.id

    conversation_id = f"telegram-{user_id}"


    print()
    print("=" * 60)
    print("📩 MENSAJE RECIBIDO DESDE TELEGRAM")
    print("=" * 60)
    print(f"👤 Usuario: {user_id}")
    print(f"💬 Mensaje: {mensaje}")
    print(f"🧠 Conversation ID: {conversation_id}")
    print("=" * 60)


    mensaje_espera = await update.message.reply_text(
        "🔎 Consultando la información energética..."
    )


    try:

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                FASTAPI_URL,
                json={
                    "mensaje": mensaje,
                    "conversation_id": conversation_id
                }
            )


        if response.status_code != 200:

            print(
                "❌ FastAPI respondió:",
                response.status_code
            )

            print(response.text)

            await mensaje_espera.edit_text(
                "❌ Ocurrió un error al consultar "
                "el asistente.\n\n"
                f"Código: {response.status_code}"
            )

            return


        datos = response.json()

        respuesta = datos.get(
            "respuesta",
            "No recibí una respuesta del asistente."
        )


        await mensaje_espera.edit_text(
            respuesta
        )


        print()
        print("=" * 60)
        print("✅ RESPUESTA ENVIADA A TELEGRAM")
        print("=" * 60)
        print(respuesta)
        print("=" * 60)


    except httpx.ConnectError:

        print(
            "❌ No se pudo conectar con FastAPI."
        )

        await mensaje_espera.edit_text(
            "❌ No puedo conectarme con la API.\n\n"
            "Asegúrate de que FastAPI esté "
            "ejecutándose en el puerto 8000."
        )


    except httpx.TimeoutException:

        print(
            "❌ Timeout esperando respuesta de FastAPI."
        )

        await mensaje_espera.edit_text(
            "⏳ La consulta está tardando demasiado.\n\n"
            "Intenta nuevamente en unos segundos."
        )


    except Exception as error:

        print()
        print("=" * 60)
        print("❌ ERROR DEL BOT")
        print("=" * 60)
        print(repr(error))
        print("=" * 60)

        await mensaje_espera.edit_text(
            "❌ Ocurrió un error inesperado."
        )


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

async def main():

    print()
    print("=" * 60)
    print("       🤖 ASISTENTE DE ENERGÍA SOLAR")
    print("=" * 60)
    print()

    print("🔑 Token de Telegram encontrado.")
    print("🚀 Configurando conexión con Telegram...")
    print()


    # ========================================================
    # HTTPX REQUEST
    # ========================================================

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )


    # ========================================================
    # APPLICATION
    # ========================================================

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .request(request)
        .build()
    )


    # ========================================================
    # HANDLERS
    # ========================================================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    application.add_handler(
        CommandHandler(
            "limpiar",
            limpiar
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mensaje_usuario
        )
    )


    # ========================================================
    # INICIALIZAR APPLICATION
    # ========================================================

    print("✅ Bot configurado correctamente.")
    print()
    print("📡 Inicializando conexión con Telegram...")
    print()

    await application.initialize()

    print("✅ Telegram conectado correctamente.")
    print()


    # ========================================================
    # INICIAR APPLICATION
    # ========================================================

    await application.start()

    print("✅ Application iniciada.")
    print()


    # ========================================================
    # INICIAR POLLING MANUALMENTE
    # ========================================================

    print("📡 Iniciando recepción de mensajes...")
    print()
    print("=" * 60)
    print("🟢 BOT ACTIVO")
    print("=" * 60)
    print()
    print("💡 Abre Telegram y escribe /start")
    print()


    await application.updater.start_polling(
        poll_interval=1.0,
        timeout=30,
        drop_pending_updates=True
    )


    # ========================================================
    # MANTENER BOT ACTIVO
    # ========================================================

    try:

        while True:

            await asyncio.sleep(1)

    except (KeyboardInterrupt, asyncio.CancelledError):

        print()
        print("🛑 Deteniendo bot...")


    # ========================================================
    # DETENER POLLING
    # ========================================================

    finally:

        print("📡 Deteniendo recepción de mensajes...")

        await application.updater.stop()

        print("🛑 Deteniendo Application...")

        await application.stop()

        print("🔌 Cerrando conexión...")

        await application.shutdown()

        print()
        print("✅ Bot detenido correctamente.")


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())