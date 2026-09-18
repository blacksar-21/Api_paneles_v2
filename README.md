# API Optimización Energética de Paneles Solares

Sistema de consulta y análisis de instalaciones fotovoltaicas mediante una API REST, un asistente local con Ollama/Qwen, MCP Toolbox y Neon PostgreSQL, con integración externa con Telegram y Open WebUI.

## Arquitectura

```text
Open WebUI ───────────────┐
                          │
Telegram ──► FastAPI ──► Ollama / Qwen3 ──► MCP Toolbox ──► Neon PostgreSQL
```

### Componentes

- **FastAPI:** API REST y punto de entrada del asistente.
- **Ollama + Qwen3:** inferencia local; no se requiere OpenAI ni Gemini.
- **MCP Toolbox:** acceso del asistente a las herramientas de la base de datos.
- **Neon PostgreSQL:** almacenamiento de los datos solares.
- **Telegram:** canal conversacional externo.
- **Open WebUI:** interfaz externa para trabajar con los modelos de Ollama.

## Estructura

```text
Api_paneles/
├── app/
│   ├── ai/                 # Asistente Ollama + MCP
│   ├── api/                # Espacio para rutas futuras
│   ├── core/               # Configuración central
│   ├── database/           # SQLAlchemy
│   ├── models/             # Modelos ORM
│   ├── schemas/            # Esquemas Pydantic
│   └── main.py             # Aplicación FastAPI
├── integrations/           # Telegram y futuras integraciones
├── scripts/                # Inicialización y diagnósticos manuales
├── tests/                  # Pruebas automatizadas futuras
├── docs/                   # Documentación técnica
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuración

1. Crear un entorno virtual.
2. Instalar `requirements.txt`.
3. Copiar `.env.example` a `.env`.
4. Completar únicamente las variables necesarias.
5. Tener Ollama ejecutándose con `qwen3:1.7b`.
6. Tener disponible MCP Toolbox y su `tools.yaml`.
7. Ejecutar FastAPI.
8. Ejecutar Telegram si se necesita ese canal.

## Open WebUI

Open WebUI es una interfaz externa; no se incluye su código dentro de este repositorio. La conexión principal debe apuntar al servidor Ollama local. Si Open WebUI se ejecuta en Docker mientras Ollama corre en Windows, normalmente debe utilizarse `host.docker.internal` en lugar de `localhost`.

Consulte `docs/openwebui.md` para la configuración.
