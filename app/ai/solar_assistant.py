import os

import json
import re
from typing import Dict, List
from urllib.parse import unquote, urlparse

from app.core.config import (
    DATABASE_URL,
    OLLAMA_HOST,
    OLLAMA_MODEL,
    TOOLBOX_EXE,
    TOOLBOX_CONFIG,
)
from ollama import AsyncClient

from mcp import ClientSession as MCPClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


# ============================================================
# CONFIGURACIÓN
# ============================================================



# ============================================================
# INSTRUCCIÓN DEL MODELO
# ============================================================

SYSTEM_INSTRUCTION = """
Eres un asistente especializado en sistemas de energía solar.

Tu función es explicar información obtenida directamente desde
una base de datos de instalaciones solares.

Reglas importantes:

1. Nunca inventes datos.
2. Nunca inventes valores de generación, consumo, cobertura o excedente.
3. Utiliza únicamente los datos proporcionados por las herramientas.
4. Responde siempre en español.
5. Sé claro y directo.
6. Usa kWh cuando hables de energía.
7. Usa porcentajes cuando hables de cobertura.
8. Si no hay información suficiente, dilo claramente.
9. No menciones detalles internos de MCP, Toolbox, Neon o programación
   a menos que el usuario pregunte específicamente por ellos.
"""


class SolarAssistant:

    # ========================================================
    # INICIALIZACIÓN
    # ========================================================

    def __init__(self):

        self.ollama = AsyncClient(
            host=OLLAMA_HOST
        )

        self.historiales: Dict[
            str,
            List[dict]
        ] = {}

        print(
            "🔌 Configurando asistente solar..."
        )

        print(
            f"   Modelo Ollama: {OLLAMA_MODEL}"
        )

        print(
            "   MCP Toolbox: STDIO"
        )

    # ========================================================
    # OBTENER VARIABLES DE NEON
    # ========================================================

    def obtener_variables_neon(self):

        database_url = DATABASE_URL

        if not database_url:

            raise RuntimeError(
                "No se encontró DATABASE_URL "
                "en el archivo .env"
            )

        database_url = (
            database_url
            .strip()
            .strip('"')
            .strip("'")
        )

        uri = urlparse(
            database_url
        )

        if not uri.hostname:

            raise RuntimeError(
                "DATABASE_URL no contiene "
                "un host válido."
            )

        usuario = unquote(
            uri.username or ""
        )

        password = unquote(
            uri.password or ""
        )

        database = (
            uri.path
            .lstrip("/")
            .split("?")[0]
        )

        if (
            not usuario
            or not password
            or not database
        ):

            raise RuntimeError(
                "No se pudieron obtener "
                "correctamente las credenciales "
                "de Neon desde DATABASE_URL."
            )

        return {

            "NEON_HOST":
                uri.hostname,

            "NEON_DATABASE":
                database,

            "NEON_USER":
                usuario,

            "NEON_PASSWORD":
                password,
        }

    # ========================================================
    # CREAR CONFIGURACIÓN MCP STDIO
    # ========================================================

    def crear_server_params(self):

        variables_neon = (
            self.obtener_variables_neon()
        )

        entorno = {

            **os.environ,

            "NEON_HOST":
                variables_neon[
                    "NEON_HOST"
                ],

            "NEON_DATABASE":
                variables_neon[
                    "NEON_DATABASE"
                ],

            "NEON_USER":
                variables_neon[
                    "NEON_USER"
                ],

            "NEON_PASSWORD":
                variables_neon[
                    "NEON_PASSWORD"
                ],
        }

        return StdioServerParameters(

            command=TOOLBOX_EXE,

            args=[
                "--config",
                TOOLBOX_CONFIG,
                "--stdio",
            ],

            env=entorno,
        )

    # ========================================================
    # EXTRAER DATOS MCP
    #
    # MCP devuelve:
    #
    # content=[
    #   TextContent(text='{"id_instalacion":1,...}'),
    #   TextContent(text='{"id_instalacion":2,...}'),
    #   TextContent(text='{"id_instalacion":3,...}')
    # ]
    #
    # Esta función convierte eso en:
    #
    # [
    #   {...},
    #   {...},
    #   {...}
    # ]
    # ========================================================

    def extraer_datos_mcp(
        self,
        resultado_mcp
    ):

        try:

            # ------------------------------------------------
            # Resultado MCP
            # ------------------------------------------------

            if hasattr(
                resultado_mcp,
                "content"
            ):

                datos = []

                for item in (
                    resultado_mcp.content
                ):

                    if not hasattr(
                        item,
                        "text"
                    ):
                        continue

                    texto = (
                        item.text
                        .strip()
                    )

                    if not texto:
                        continue

                    try:

                        objeto = json.loads(
                            texto
                        )

                        datos.append(
                            objeto
                        )

                    except json.JSONDecodeError:

                        # ------------------------------------
                        # Buscar JSON dentro del texto
                        # ------------------------------------

                        match = re.search(
                            r"(\{.*\}|\[.*\])",
                            texto,
                            re.DOTALL
                        )

                        if match:

                            try:

                                objeto = json.loads(
                                    match.group(1)
                                )

                                datos.append(
                                    objeto
                                )

                            except json.JSONDecodeError:

                                pass

                if datos:

                    return datos

            # ------------------------------------------------
            # Si ya es lista
            # ------------------------------------------------

            if isinstance(
                resultado_mcp,
                list
            ):

                return resultado_mcp

            # ------------------------------------------------
            # Si ya es diccionario
            # ------------------------------------------------

            if isinstance(
                resultado_mcp,
                dict
            ):

                return resultado_mcp

            # ------------------------------------------------
            # Si es texto
            # ------------------------------------------------

            if isinstance(
                resultado_mcp,
                str
            ):

                texto = (
                    resultado_mcp
                    .strip()
                )

                try:

                    return json.loads(
                        texto
                    )

                except json.JSONDecodeError:

                    pass

                match = re.search(
                    r"(\{.*\}|\[.*\])",
                    texto,
                    re.DOTALL
                )

                if match:

                    try:

                        return json.loads(
                            match.group(1)
                        )

                    except json.JSONDecodeError:

                        pass

            return str(
                resultado_mcp
            )

        except Exception as error:

            print(
                "⚠️ Error procesando "
                f"resultado MCP: {error}"
            )

            return str(
                resultado_mcp
            )

    # ========================================================
    # OBTENER LISTA DE INSTALACIONES
    # ========================================================

    def obtener_lista_instalaciones(
        self,
        datos
    ):

        # ------------------------------------------------
        # Caso:
        #
        # [
        #   {...},
        #   {...}
        # ]
        # ------------------------------------------------

        if isinstance(
            datos,
            list
        ):

            return datos

        # ------------------------------------------------
        # Caso:
        #
        # {
        #   "instalaciones": [...]
        # }
        # ------------------------------------------------

        if isinstance(
            datos,
            dict
        ):

            instalaciones = datos.get(
                "instalaciones"
            )

            if isinstance(
                instalaciones,
                list
            ):

                return instalaciones

            # --------------------------------------------
            # Otros formatos posibles
            # --------------------------------------------

            for clave in [

                "data",
                "result",
                "resultados",
                "items"

            ]:

                valor = datos.get(
                    clave
                )

                if isinstance(
                    valor,
                    list
                ):

                    return valor

        return []

    # ========================================================
    # OBTENER ID POR NOMBRE
    # ========================================================

    def obtener_id_por_nombre(
        self,
        texto
    ):

        texto_lower = (
            texto.lower()
        )

        # ------------------------------------------------
        # SISTEMA CAMPUS
        # ------------------------------------------------

        if (

            "sistema campus"
            in texto_lower

            or

            "campus universitario"
            in texto_lower

            or

            "instalación 1"
            in texto_lower

            or

            "instalacion 1"
            in texto_lower

            or

            "instalación número 1"
            in texto_lower

            or

            "instalacion número 1"
            in texto_lower

            or

            "instalacion numero 1"
            in texto_lower

        ):

            return 1

        # ------------------------------------------------
        # SISTEMA INDUSTRIAL
        # ------------------------------------------------

        if (

            "sistema industrial"
            in texto_lower

            or

            "planta industrial"
            in texto_lower

            or

            "instalación 2"
            in texto_lower

            or

            "instalacion 2"
            in texto_lower

            or

            "instalación número 2"
            in texto_lower

            or

            "instalacion número 2"
            in texto_lower

            or

            "instalacion numero 2"
            in texto_lower

        ):

            return 2

        # ------------------------------------------------
        # SISTEMA DEPORTIVO
        # ------------------------------------------------

        if (

            "sistema deportivo"
            in texto_lower

            or

            "centro deportivo"
            in texto_lower

            or

            "instalación 3"
            in texto_lower

            or

            "instalacion 3"
            in texto_lower

            or

            "instalación número 3"
            in texto_lower

            or

            "instalacion número 3"
            in texto_lower

            or

            "instalacion numero 3"
            in texto_lower

        ):

            return 3

        # ------------------------------------------------
        # REGEX
        # ------------------------------------------------

        match = re.search(

            r"(?:instalaci[oó]n|sistema)\s*"
            r"(?:n[uú]mero\s*)?(\d+)",

            texto_lower

        )

        if match:

            numero = int(
                match.group(1)
            )

            if numero in (
                1,
                2,
                3
            ):

                return numero

        return None

    # ========================================================
    # OBTENER INSTALACIÓN DESDE CONTEXTO
    # ========================================================

    def obtener_id_instalacion_contexto(
        self,
        mensajes: List[dict]
    ):

        texto = " ".join(

            mensaje.get(
                "content",
                ""
            )

            for mensaje
            in mensajes[-8:]

        )

        return self.obtener_id_por_nombre(
            texto
        )

    # ========================================================
    # NOMBRE DE INSTALACIÓN
    # ========================================================

    def obtener_nombre_instalacion(
        self,
        id_instalacion
    ):

        nombres = {

            1:
                "Sistema Campus",

            2:
                "Sistema Industrial",

            3:
                "Sistema Deportivo",
        }

        return nombres.get(

            id_instalacion,

            f"Instalación {id_instalacion}"

        )

    # ========================================================
    # CALCULAR MAYOR GENERACIÓN
    #
    # Campo real MCP:
    #
    # energia_generada_total_kwh
    # ========================================================

    def calcular_mayor_generacion(
        self,
        resultado
    ):

        datos = (
            self.extraer_datos_mcp(
                resultado
            )
        )

        instalaciones = (
            self.obtener_lista_instalaciones(
                datos
            )
        )

        candidatos = []

        for item in instalaciones:

            if not isinstance(
                item,
                dict
            ):

                continue

            generacion = (

                item.get(
                    "energia_generada_total_kwh"
                )

                or

                item.get(
                    "generacion_total"
                )

                or

                item.get(
                    "generacion"
                )

                or

                item.get(
                    "energia_generada"
                )

                or

                item.get(
                    "energia_generacion"
                )

                or

                item.get(
                    "total_generacion"
                )
            )

            if generacion is None:

                continue

            try:

                valor = float(
                    generacion
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            candidatos.append(
                (
                    valor,
                    item
                )
            )

        if not candidatos:

            return None

        mayor, item = max(

            candidatos,

            key=lambda x: x[0]

        )

        id_instalacion = (
            item.get(
                "id_instalacion"
            )
        )

        nombre = (
            self.obtener_nombre_instalacion(
                id_instalacion
            )
        )

        return (

            f"La instalación que más energía "
            f"genera es {nombre} "
            f"(id_instalacion = "
            f"{id_instalacion}), "
            f"con una generación total de "
            f"{mayor:.2f} kWh."

        )

    # ========================================================
    # CALCULAR MAYOR COBERTURA
    #
    # Fórmula:
    #
    # generación / consumo * 100
    #
    # Campo MCP:
    #
    # energia_generada_total_kwh
    # energia_consumida_total_kwh
    # ========================================================

    def calcular_mayor_cobertura(
        self,
        resultado
    ):

        datos = (
            self.extraer_datos_mcp(
                resultado
            )
        )

        instalaciones = (
            self.obtener_lista_instalaciones(
                datos
            )
        )

        candidatos = []

        for item in instalaciones:

            if not isinstance(
                item,
                dict
            ):

                continue

            generacion = item.get(
                "energia_generada_total_kwh"
            )

            consumo = item.get(
                "energia_consumida_total_kwh"
            )

            if (
                generacion is None
                or consumo is None
            ):

                continue

            try:

                generacion = float(
                    generacion
                )

                consumo = float(
                    consumo
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            if consumo == 0:

                continue

            cobertura = (

                generacion
                / consumo
                * 100

            )

            candidatos.append(
                (
                    cobertura,
                    item
                )
            )

        if not candidatos:

            return None

        mayor, item = max(

            candidatos,

            key=lambda x: x[0]

        )

        id_instalacion = (
            item.get(
                "id_instalacion"
            )
        )

        nombre = (
            self.obtener_nombre_instalacion(
                id_instalacion
            )
        )

        return (

            f"La instalación con mayor "
            f"cobertura es {nombre} "
            f"(id_instalacion = "
            f"{id_instalacion}), "
            f"con una cobertura de "
            f"{mayor:.2f}%."

        )

    # ========================================================
    # CALCULAR MAYOR EXCEDENTE
    #
    # Campo MCP:
    #
    # energia_sobrante_kwh
    # ========================================================

    def calcular_mayor_excedente(
        self,
        resultado
    ):

        datos = (
            self.extraer_datos_mcp(
                resultado
            )
        )

        instalaciones = (
            self.obtener_lista_instalaciones(
                datos
            )
        )

        candidatos = []

        for item in instalaciones:

            if not isinstance(
                item,
                dict
            ):

                continue

            excedente = (

                item.get(
                    "energia_sobrante_kwh"
                )

                or

                item.get(
                    "excedente"
                )

                or

                item.get(
                    "excedente_energetico"
                )

                or

                item.get(
                    "surplus"
                )

                or

                item.get(
                    "energia_excedente"
                )
            )

            if excedente is None:

                continue

            try:

                valor = float(
                    excedente
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            candidatos.append(
                (
                    valor,
                    item
                )
            )

        if not candidatos:

            return None

        mayor, item = max(

            candidatos,

            key=lambda x: x[0]

        )

        id_instalacion = (
            item.get(
                "id_instalacion"
            )
        )

        nombre = (
            self.obtener_nombre_instalacion(
                id_instalacion
            )
        )

        return (

            f"La instalación con mayor "
            f"excedente de energía es "
            f"{nombre} "
            f"(id_instalacion = "
            f"{id_instalacion}), "
            f"con un excedente de "
            f"{mayor:.2f} kWh."

        )

    # ========================================================
    # DETECTAR CONSULTA
    # ========================================================

    def detectar_consulta(
        self,
        texto: str,
        mensajes: List[dict]
    ):

        texto_lower = (
            texto.lower()
        )

        # ====================================================
        # COMPARAR INSTALACIONES
        # ====================================================

        frases_comparacion = [

            "cuál instalación genera más",
            "cual instalacion genera mas",

            "qué instalación genera más",
            "que instalacion genera mas",

            "cuál genera más energía",
            "cual genera mas energia",

            "qué genera más energía",
            "que genera mas energia",

            "qué instalación produce más",
            "que instalacion produce mas",

            "qué sistema genera más",
            "que sistema genera mas",

            "mayor generación",
            "mayor generacion",

            "mayor energía",
            "mayor energia",

            "mayor producción",
            "mayor produccion",

            "mayor cobertura",
            "mejor cobertura",

            "más cobertura",
            "mas cobertura",

            "mayor porcentaje de cobertura",
            "mayor porcentaje cobertura",

            "mayor excedente",

            "más excedente",
            "mas excedente",

            "mayor sobrante",

            "más sobrante",
            "mas sobrante",

            "mayor surplus",
        ]

        if any(

            frase in texto_lower

            for frase
            in frases_comparacion

        ):

            return (

                "comparar_instalaciones",

                {}

            )

        # ====================================================
        # LISTAR INSTALACIONES
        # ====================================================

        frases_lista = [

            "listar instalaciones",

            "lista de instalaciones",

            "qué instalaciones hay",
            "que instalaciones hay",

            "cuáles instalaciones hay",
            "cuales instalaciones hay",

            "qué sistemas hay",
            "que sistemas hay",
        ]

        if any(

            frase in texto_lower

            for frase
            in frases_lista

        ):

            return (

                "listar_instalaciones",

                {}

            )

        # ====================================================
        # HORA DE MAYOR GENERACIÓN
        # ====================================================

        frases_hora = [

            "a qué hora genera más",
            "a que hora genera mas",

            "hora de mayor generación",
            "hora de mayor generacion",

            "cuándo genera más",
            "cuando genera mas",

            "hora máxima",
            "hora maxima",
        ]

        if any(

            frase in texto_lower

            for frase
            in frases_hora

        ):

            id_instalacion = (
                self.obtener_id_por_nombre(
                    texto
                )
            )

            if id_instalacion is None:

                id_instalacion = (
                    self.obtener_id_instalacion_contexto(
                        mensajes
                    )
                )

            if id_instalacion is not None:

                return (

                    "obtener_hora_mayor_generacion",

                    {
                        "id_instalacion":
                            id_instalacion
                    }

                )

        # ====================================================
        # MEDICIONES
        # ====================================================

        palabras_mediciones = [

            "mediciones",

            "medición",
            "medicion",

            "datos de energía",
            "datos de energia",

            "generó",
            "genero",

            "generación",
            "generacion",

            "consumo",
        ]

        if any(

            palabra in texto_lower

            for palabra
            in palabras_mediciones

        ):

            id_instalacion = (
                self.obtener_id_por_nombre(
                    texto
                )
            )

            if id_instalacion is None:

                id_instalacion = (
                    self.obtener_id_instalacion_contexto(
                        mensajes
                    )
                )

            if id_instalacion is not None:

                return (

                    "obtener_mediciones_energeticas",

                    {
                        "id_instalacion":
                            id_instalacion
                    }

                )

        # ====================================================
        # RESUMEN
        # ====================================================

        palabras_resumen = [

            "resumen",

            "resumen energético",
            "resumen energetico",

            "rendimiento",

            "desempeño",
            "desempeno",
        ]

        if any(

            palabra in texto_lower

            for palabra
            in palabras_resumen

        ):

            id_instalacion = (
                self.obtener_id_por_nombre(
                    texto
                )
            )

            if id_instalacion is None:

                id_instalacion = (
                    self.obtener_id_instalacion_contexto(
                        mensajes
                    )
                )

            if id_instalacion is not None:

                return (

                    "obtener_resumen_energetico",

                    {
                        "id_instalacion":
                            id_instalacion
                    }

                )

        # ====================================================
        # MÁXIMOS Y MÍNIMOS
        # ====================================================

        palabras_maximos = [

            "máximo",
            "maximo",

            "mínimo",
            "minimo",

            "máxima",
            "maxima",

            "mínima",
            "minima",
        ]

        if any(

            palabra in texto_lower

            for palabra
            in palabras_maximos

        ):

            id_instalacion = (
                self.obtener_id_por_nombre(
                    texto
                )
            )

            if id_instalacion is None:

                id_instalacion = (
                    self.obtener_id_instalacion_contexto(
                        mensajes
                    )
                )

            if id_instalacion is not None:

                return (

                    "obtener_maximos_minimos_energeticos",

                    {
                        "id_instalacion":
                            id_instalacion
                    }

                )

        return None

    # ========================================================
    # EJECUTAR TOOL MCP
    # ========================================================

    async def ejecutar_tool(
        self,
        session,
        nombre_tool,
        argumentos
    ):

        print()

        print(
            "🛠️ Ejecutando herramienta MCP:"
        )

        print(
            f"   → {nombre_tool}"
        )

        if argumentos:

            print(
                f"   → Argumentos: "
                f"{argumentos}"
            )

        resultado = await session.call_tool(

            nombre_tool,

            argumentos

        )

        print(
            "✅ Resultado MCP recibido."
        )

        # ----------------------------------------------------
        # DEBUG
        # ----------------------------------------------------

        print(
            "📦 DATOS MCP RAW:"
        )

        print(
            resultado
        )

        return resultado

    # ========================================================
    # GENERAR RESPUESTA CON QWEN
    # ========================================================

    async def generar_respuesta(
        self,
        pregunta,
        resultado,
        historial
    ):

        datos = (
            self.extraer_datos_mcp(
                resultado
            )
        )

        prompt = f"""

Pregunta del usuario:

{pregunta}

Datos obtenidos directamente
desde la base de datos:

{json.dumps(
    datos,
    ensure_ascii=False,
    indent=2,
    default=str
)}

Reglas:

- Responde únicamente usando los datos.
- No inventes información.
- No cambies los valores numéricos.
- No agregues datos que no aparezcan.
- Responde en español.
- Sé claro y breve.

Pregunta:

{pregunta}
"""

        mensajes = [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_INSTRUCTION
            }

        ]

        mensajes.extend(
            historial[-6:]
        )

        mensajes.append(

            {
                "role":
                    "user",

                "content":
                    prompt
            }

        )

        respuesta = await self.ollama.chat(

            model=OLLAMA_MODEL,

            messages=mensajes

        )

        return (

            respuesta[
                "message"
            ][
                "content"
            ].strip()

        )

    # ========================================================
    # PREGUNTAR
    # ========================================================

    async def preguntar(
        self,
        mensaje: str,
        conversation_id: str = "default"
    ):

        # ----------------------------------------------------
        # CREAR HISTORIAL
        # ----------------------------------------------------

        if (
            conversation_id
            not in self.historiales
        ):

            self.historiales[
                conversation_id
            ] = []

        historial = (
            self.historiales[
                conversation_id
            ]
        )

        # ----------------------------------------------------
        # GUARDAR PREGUNTA
        # ----------------------------------------------------

        historial.append(

            {
                "role":
                    "user",

                "content":
                    mensaje
            }

        )

        # ----------------------------------------------------
        # DETECTAR CONSULTA
        # ----------------------------------------------------

        consulta = (
            self.detectar_consulta(

                mensaje,

                historial

            )
        )

        # ----------------------------------------------------
        # NO IDENTIFICADA
        # ----------------------------------------------------

        if consulta is None:

            respuesta = (

                "No pude identificar una consulta "
                "específica sobre los datos de energía "
                "solar. Puedes preguntarme, por ejemplo, "
                "cuál instalación genera más energía, "
                "cuál tiene mayor cobertura, cuál tiene "
                "mayor excedente o consultar las "
                "mediciones de una instalación."

            )

            historial.append(

                {
                    "role":
                        "assistant",

                    "content":
                        respuesta
                }

            )

            return respuesta

        nombre_tool, argumentos = (
            consulta
        )

        # ----------------------------------------------------
        # CREAR MCP
        # ----------------------------------------------------

        server_params = (
            self.crear_server_params()
        )

        # ----------------------------------------------------
        # CONECTAR MCP POR STDIO
        # ----------------------------------------------------

        async with stdio_client(

            server_params

        ) as (

            read_stream,
            write_stream

        ):

            async with MCPClientSession(

                read_stream,
                write_stream

            ) as session:

                # --------------------------------------------
                # INICIALIZAR
                # --------------------------------------------

                await session.initialize()

                # --------------------------------------------
                # EJECUTAR TOOL
                # --------------------------------------------

                resultado = (
                    await self.ejecutar_tool(

                        session,

                        nombre_tool,

                        argumentos

                    )
                )

                # ============================================
                # COMPARACIONES
                # ============================================

                if (

                    nombre_tool
                    ==
                    "comparar_instalaciones"

                ):

                    texto_lower = (
                        mensaje.lower()
                    )

                    # ----------------------------------------
                    # COBERTURA
                    # ----------------------------------------

                    if (

                        "cobertura"
                        in texto_lower

                        or

                        "porcentaje de cobertura"
                        in texto_lower

                    ):

                        respuesta = (
                            self.calcular_mayor_cobertura(
                                resultado
                            )
                        )

                    # ----------------------------------------
                    # EXCEDENTE
                    # ----------------------------------------

                    elif (

                        "excedente"
                        in texto_lower

                        or

                        "sobrante"
                        in texto_lower

                        or

                        "surplus"
                        in texto_lower

                    ):

                        respuesta = (
                            self.calcular_mayor_excedente(
                                resultado
                            )
                        )

                    # ----------------------------------------
                    # GENERACIÓN
                    # ----------------------------------------

                    else:

                        respuesta = (
                            self.calcular_mayor_generacion(
                                resultado
                            )
                        )

                    # ----------------------------------------
                    # FALLBACK
                    # ----------------------------------------

                    if respuesta is None:

                        print(
                            "⚠️ No se pudo interpretar "
                            "la estructura del resultado MCP."
                        )

                        print(
                            "⚠️ Se utilizará Qwen "
                            "como fallback."
                        )

                        respuesta = (
                            await self.generar_respuesta(

                                mensaje,

                                resultado,

                                historial

                            )
                        )

                # ============================================
                # OTRAS HERRAMIENTAS
                # ============================================

                else:

                    respuesta = (
                        await self.generar_respuesta(

                            mensaje,

                            resultado,

                            historial

                        )
                    )

        # ----------------------------------------------------
        # GUARDAR RESPUESTA
        # ----------------------------------------------------

        historial.append(

            {
                "role":
                    "assistant",

                "content":
                    respuesta
            }

        )

        return respuesta

    # ========================================================
    # LIMPIAR CONVERSACIÓN
    # ========================================================

    def limpiar_conversacion(
        self,
        conversation_id: str
    ):

        if (
            conversation_id
            in self.historiales
        ):

            del self.historiales[
                conversation_id
            ]

        return True


# ============================================================
# INSTANCIA GLOBAL
# ============================================================

asistente_solar = SolarAssistant()

