import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot
from telegram.request import HTTPXRequest


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def main():

    print("=" * 60)
    print("🧪 PRUEBA DIRECTA DE PYTHON-TELEGRAM-BOT")
    print("=" * 60)

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    bot = Bot(
        token=TOKEN,
        request=request
    )

    print()
    print("📡 Intentando conectar con Telegram...")
    print()

    try:

        me = await bot.get_me()

        print("✅ CONEXIÓN EXITOSA")
        print()
        print(f"🤖 Nombre: {me.first_name}")
        print(f"👤 Usuario: @{me.username}")
        print()
        print("=" * 60)

    except Exception as error:

        print("❌ ERROR")
        print()
        print(repr(error))
        print()
        print("=" * 60)

    finally:

        await request.shutdown()


if __name__ == "__main__":
    asyncio.run(main())