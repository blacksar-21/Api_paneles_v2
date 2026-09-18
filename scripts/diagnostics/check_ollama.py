import asyncio
from ollama import AsyncClient


async def main():
    client = AsyncClient(host="http://127.0.0.1:11434")

    print("Conectando con Ollama...")

    respuesta = await client.list()

    print("\n✅ Conexión correcta con Ollama")
    print("\nModelos disponibles:")

    for modelo in respuesta.models:
        print(f"  ✓ {modelo.model}")


asyncio.run(main())