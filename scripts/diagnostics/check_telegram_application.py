import asyncio
import os

from dotenv import load_dotenv
from telegram.request import HTTPXRequest
from telegram.ext import Application


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def main():

    print("=" * 60)
    print("🧪 PRUEBA DE APPLICATION")
    print("=" * 60)

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    application = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .build()
    )

    print()
    print("1️⃣ Application creada")
    print("2️⃣ Inicializando...")
    print()

    try:

        await application.initialize()

        print("✅ INITIALIZE EXITOSO")
        print()

        print("3️⃣ Cerrando...")

        await application.shutdown()

        print("✅ SHUTDOWN EXITOSO")

    except Exception as error:

        print("❌ ERROR:")
        print(repr(error))

        try:
            await application.shutdown()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())