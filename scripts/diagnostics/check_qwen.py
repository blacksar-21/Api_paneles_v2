import asyncio
from ollama import AsyncClient


async def main():
    client = AsyncClient(host="http://127.0.0.1:11434")

    print("🤖 Probando Qwen3 1.7B...\n")

    respuesta = await client.chat(
        model="qwen3:1.7b",
        messages=[
            {
                "role": "user",
                "content": "Responde solamente: OK"
            }
        ],
        think=False,
        stream=False,
        options={
            "temperature": 0.1,
            "num_ctx": 2048
        }
    )

    print("Respuesta de Qwen:")
    print(respuesta.message.content)


asyncio.run(main())