import json
from datetime import datetime, timedelta
import pytz
from fastapi import APIRouter, HTTPException
from openai import OpenAI
import os

# ==== Importar tus lógicas PURAS ====
from app.mcp.agent import (
    _crear_cliente_logic,
    _buscar_cliente_logic,
    _listar_clientes_logic,
    _crear_contacto_logic,
    _crear_cita_logic,
)

# ==== Schemas ====
from app.schemas.chat import MensajeRequest, MensajeResponse

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================
# MEMORIA DE CONVERSACIONES
# ==========================
conversaciones = {}

# ==========================
# TOOLS PARA GPT
# ==========================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "crear_cliente",
            "description": "Registra un nuevo cliente",
            "parameters": {
                "type": "object",
                "properties": {
                    "fullName": {"type": "string"},
                    "fullSurname": {"type": "string"},
                    "identified": {"type": "string"},
                },
                "required": ["fullName", "fullSurname", "identified"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_cliente",
            "description": "Busca un cliente por identificación",
            "parameters": {
                "type": "object",
                "properties": {"identified": {"type": "string"}},
                "required": ["identified"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_clientes",
            "description": "Lista todos los clientes registrados",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_contacto",
            "description": "Crea un contacto para un cliente",
            "parameters": {
                "type": "object",
                "properties": {
                    "clientId": {"type": "integer"},
                    "phoneNumber": {"type": "string"},
                    "email": {"type": "string"},
                    "address": {"type": "string"},
                },
                "required": ["clientId", "phoneNumber", "email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_cita",
            "description": "Crea una cita para un cliente",
            "parameters": {
                "type": "object",
                "properties": {
                    "clientId": {"type": "integer"},
                    "appointmentDate": {"type": "string"},
                    "ubicacion": {"type": "string"},
                    "details": {"type": "string"},
                    "state": {"type": "string"},
                    "employedId": {"type": "integer"},
                },
                "required": ["clientId", "appointmentDate", "ubicacion"],
            },
        },
    },
]


# ==========================
# EJECUTAR HERRAMIENTAS
# ==========================
def ejecutar_herramienta(nombre, args):
    try:
        if nombre == "crear_cliente":
            return _crear_cliente_logic(**args)

        if nombre == "buscar_cliente":
            return _buscar_cliente_logic(**args)

        if nombre == "listar_clientes":
            return _listar_clientes_logic()

        if nombre == "crear_contacto":
            return _crear_contacto_logic(**args)

        if nombre == "crear_cita":
            return _crear_cita_logic(**args)

        return {"status": "error", "message": f"Herramienta '{nombre}' no encontrada"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==========================
# ENDPOINT PRINCIPAL /chat
# ==========================
@router.post("/chat", response_model=MensajeResponse)
async def chat(request: MensajeRequest):
    try:
        # Crear o recuperar el ID de conversación
        conv_id = request.conversacion_id or f"conv_{len(conversaciones)}"

        if conv_id not in conversaciones:
            conversaciones[conv_id] = []
            tz_colombia = pytz.timezone("America/Bogota")
            hoy = datetime.now(tz_colombia)
            mañana = hoy + timedelta(days=1)

            conversaciones[conv_id] = [
                {
                    "role": "system",
                    "content": f"""Eres un asistente de taller mecánico profesional en Colombia.

🗓️ FECHA Y HORA ACTUAL (Colombia):
- HOY es: {hoy.strftime("%A %d de %B de %Y")}
- Hora actual: {hoy.strftime("%I:%M %p")} (formato 12 horas)
- Hora actual: {hoy.strftime("%H:%M")} (formato 24 horas)
- Año actual: {hoy.year}

⚠️ REGLAS CRÍTICAS PARA FECHAS Y HORAS:

FORMATO DE FECHA Y HORA:
- SIEMPRE usa formato 24 horas: YYYY-MM-DD HH:MM:SS
- SIEMPRE usa el año {hoy.year}

CONVERSIÓN DE HORAS (MUY IMPORTANTE):
- 12:00 AM = 00:00:00 (medianoche)
- 1:00 AM = 01:00:00
- 8:00 AM = 08:00:00
- 9:00 AM = 09:00:00
- 10:00 AM = 10:00:00
- 11:00 AM = 11:00:00
- 12:00 PM = 12:00:00 (mediodía)
- 1:00 PM = 13:00:00
- 2:00 PM = 14:00:00
- 3:00 PM = 15:00:00 ← SI EL USUARIO DICE "3 PM" USA 15:00:00
- 4:00 PM = 16:00:00
- 5:00 PM = 17:00:00
- 6:00 PM = 18:00:00
- 7:00 PM = 19:00:00
- 8:00 PM = 20:00:00
- 9:00 PM = 21:00:00
- 10:00 PM = 22:00:00
- 11:00 PM = 23:00:00

EJEMPLOS CORRECTOS:
- Usuario dice "3 de la tarde" o "3 PM" → Usa {hoy.strftime("%Y-%m-%d")} 15:00:00
- Usuario dice "10 de la mañana" o "10 AM" → Usa {hoy.strftime("%Y-%m-%d")} 10:00:00
- Usuario dice "mediodía" → Usa {hoy.strftime("%Y-%m-%d")} 12:00:00

EJEMPLOS INCORRECTOS (NO HACER):
- ❌ Usuario dice "3 PM" → NO uses 03:00:00
- ❌ Usuario dice "3 PM" → NO uses 09:00:00
- ✅ Usuario dice "3 PM" → SÍ usa 15:00:00

HORARIO DE ATENCIÓN DEL TALLER:
- Lunes a Viernes: 8:00 AM - 6:00 PM (08:00 - 18:00)
- Sábados: 8:00 AM - 2:00 PM (08:00 - 14:00)
- Domingos: Cerrado

FLUJO:
1. Saluda
2. Pide identificación
3. Si no existe: registra (nombre, apellidos, ID, teléfono, email, dirección)
4. Pregunta: marca, modelo, año del vehículo
5. Pregunta: qué servicio necesita
6. Pregunta: fecha y hora (recuerda que HOY es {hoy.strftime("%d/%m/%Y a las %I:%M %p")})
7. CONFIRMA la hora con el usuario antes de crear la cita
8. Crea la cita con vehículo en details

Sé profesional y conversacional.""",
                }
            ]

        historial = conversaciones[conv_id]

        # Añadir mensaje del usuario
        historial.append({"role": "user", "content": request.mensaje})

        # ================
        # PRIMERA LLAMADA
        # ================
        response = client.chat.completions.create(
            model="gpt-4.1", messages=historial, tools=TOOLS
        )

        assistant_msg = response.choices[0].message
        respuesta_texto = assistant_msg.content or ""
        tool_calls = assistant_msg.tool_calls

        herramientas_usadas = []
        cita_creada = False
        datos_cita = None

        # ==========================
        # SI EL MODELO QUIERE USAR TOOLS
        # ==========================
        if tool_calls:
            historial.append(
                {
                    "role": "assistant",
                    "content": respuesta_texto,
                    "tool_calls": [tc.model_dump() for tc in tool_calls],
                }
            )

            for call in tool_calls:
                nombre = call.function.name
                args = json.loads(call.function.arguments)

                resultado = ejecutar_herramienta(nombre, args)

                herramientas_usadas.append(
                    {"herramienta": nombre, "parametros": args, "resultado": resultado}
                )

                if nombre == "crear_cita" and resultado.get("status") == "success":
                    cita_creada = True
                    datos_cita = resultado.get("data")

                historial.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(resultado, ensure_ascii=False),
                    }
                )

            # =================
            # SEGUNDA LLAMADA (respuesta final)
            # =================
            final = client.chat.completions.create(model="gpt-4.1", messages=historial)

            respuesta_texto = final.choices[0].message.content
            historial.append({"role": "assistant", "content": respuesta_texto})

        else:
            historial.append({"role": "assistant", "content": respuesta_texto})

        conversaciones[conv_id] = historial

        return MensajeResponse(
            respuesta=respuesta_texto,
            conversacion_id=conv_id,
            herramientas_usadas=herramientas_usadas,
            cita_creada=cita_creada,
            datos_cita=datos_cita,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
