"""
Router de API para el Bot de Taller
Importa las funciones de lógica pura (sin decoradores MCP)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from anthropic import Anthropic
import json

# Importar las funciones de lógica pura (con prefijo _)
from app.mcp.agent import (
    _crear_cliente_logic as crear_cliente,
    _buscar_cliente_logic as buscar_cliente,
    _listar_clientes_logic as listar_clientes,
    _crear_contacto_logic as crear_contacto,
    _crear_cita_logic as crear_cita,
)

router = APIRouter()

# Cliente de Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Sistema de prompt
SYSTEM_PROMPT = """Eres un asistente virtual de "Taller Express", un taller mecánico profesional en Cali, Colombia.

TU MISIÓN: Ayudar a los clientes a agendar citas de manera natural y eficiente.

FLUJO DE CONVERSACIÓN:
1. 🤝 Saluda cordialmente y pregunta en qué puedes ayudar
2. 🔍 Identifica el servicio necesario (cambio de aceite, frenos, revisión general, etc.)
3. 📋 Recopila datos del cliente de manera natural:
   - Nombre completo y apellidos
   - Número de identificación (cédula)
   - Teléfono de contacto
   - Email
4. 📅 Ofrece fechas y horarios disponibles
5. ✅ Confirma TODOS los datos antes de crear la cita
6. 🔧 Usa las herramientas para registrar en el sistema

INFORMACIÓN DEL TALLER:
- Nombre: Taller Express
- Ubicación: Av. Principal #123, Cali
- Horario: Lunes a Viernes, 8:00 AM - 6:00 PM
- Duración promedio: 1-2 horas por servicio

SERVICIOS DISPONIBLES:
- Cambio de aceite y filtros
- Revisión general (multi-punto)
- Frenos (pastillas, discos)
- Suspensión y amortiguadores
- Sistema eléctrico
- Diagnóstico computarizado
- Mantenimiento preventivo

REGLAS IMPORTANTES:
✅ Sé amable, profesional y empático
✅ Habla de manera natural, no como un robot
✅ SIEMPRE valida que tienes TODA la información antes de crear registros
✅ Si el cliente ya existe (buscar_cliente lo encuentra), NO lo crees de nuevo
✅ Confirma los datos antes de proceder
✅ Ofrece horarios específicos disponibles

FLUJO DE HERRAMIENTAS (MUY IMPORTANTE):
1. Cuando tengas el número de identificación → usar buscar_cliente
2. Si NO existe → usar crear_cliente
3. Después de crear/encontrar cliente → usar crear_contacto (con el clientId obtenido)
4. Finalmente → usar crear_cita (cuando tengas fecha confirmada)

La ubicación del taller siempre es: "Taller Express - Av. Principal #123, Cali"
"""


# Modelos Pydantic
class MensajeRequest(BaseModel):
    mensaje: str
    conversacion_id: Optional[str] = None


class MensajeResponse(BaseModel):
    respuesta: str
    conversacion_id: str
    herramientas_usadas: List[dict] = []
    cita_creada: bool = False
    datos_cita: Optional[dict] = None


# Almacenamiento de conversaciones
conversaciones = {}

# Definición de herramientas para Claude
TOOLS = [
    {
        "name": "buscar_cliente",
        "description": "Busca un cliente existente por número de identificación. Úsalo PRIMERO antes de crear un nuevo cliente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "identified": {
                    "type": "string",
                    "description": "Número de identificación del cliente (cédula)",
                }
            },
            "required": ["identified"],
        },
    },
    {
        "name": "crear_cliente",
        "description": "Registra un nuevo cliente. Solo usar si buscar_cliente confirmó que NO existe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fullName": {
                    "type": "string",
                    "description": "Nombre completo del cliente",
                },
                "fullSurname": {
                    "type": "string",
                    "description": "Apellidos completos del cliente",
                },
                "identified": {
                    "type": "string",
                    "description": "Número de identificación único (cédula)",
                },
            },
            "required": ["fullName", "fullSurname", "identified"],
        },
    },
    {
        "name": "crear_contacto",
        "description": "Crea información de contacto para un cliente existente",
        "input_schema": {
            "type": "object",
            "properties": {
                "clientId": {
                    "type": "integer",
                    "description": "ID del cliente en el sistema",
                },
                "phoneNumber": {
                    "type": "string",
                    "description": "Número de teléfono del cliente",
                },
                "email": {
                    "type": "string",
                    "description": "Correo electrónico del cliente",
                },
                "address": {
                    "type": "string",
                    "description": "Dirección del cliente (puede estar vacío)",
                },
            },
            "required": ["clientId", "phoneNumber", "email", "address"],
        },
    },
    {
        "name": "crear_cita",
        "description": "Crea una cita para el cliente en el taller. Solo usar después de tener el cliente registrado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "clientId": {
                    "type": "integer",
                    "description": "ID del cliente en el sistema",
                },
                "appointmentDate": {
                    "type": "string",
                    "description": "Fecha y hora en formato YYYY-MM-DD HH:MM:SS (ejemplo: 2025-11-25 10:00:00)",
                },
                "ubicacion": {
                    "type": "string",
                    "description": "Ubicación del taller. Usar: 'Taller Express - Av. Principal #123, Cali'",
                },
                "details": {
                    "type": "string",
                    "description": "Descripción del servicio solicitado (cambio de aceite, revisión, etc.)",
                },
                "state": {
                    "type": "string",
                    "description": "Estado de la cita. Siempre usar 'ASIGNADA'",
                    "enum": ["ASIGNADA", "COMPLETADA", "CANCELADA"],
                },
                "employedId": {
                    "type": "integer",
                    "description": "ID del empleado asignado (opcional, puede ser null)",
                },
            },
            "required": ["clientId", "appointmentDate", "ubicacion", "details"],
        },
    },
]

# ==================== ENDPOINTS ====================


@router.post("/chat", response_model=MensajeResponse)
async def chat(request: MensajeRequest):
    """Endpoint principal del chat bot"""
    try:
        # Obtener o crear ID de conversación
        conv_id = request.conversacion_id or f"conv_{len(conversaciones)}"

        # Obtener o inicializar historial
        if conv_id not in conversaciones:
            conversaciones[conv_id] = []

        historial = conversaciones[conv_id]

        # Agregar mensaje del usuario
        historial.append({"role": "user", "content": request.mensaje})

        # Llamar a Claude con las herramientas
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=historial,
            tools=TOOLS,
        )

        # Procesar respuesta
        respuesta_texto = ""
        tool_calls = []
        herramientas_usadas = []
        cita_creada = False
        datos_cita = None

        # Extraer contenido y tool calls
        for block in response.content:
            if block.type == "text":
                respuesta_texto += block.text
            elif block.type == "tool_use":
                tool_calls.append(block)

        # Si Claude quiere usar herramientas
        if tool_calls:
            # Agregar respuesta de Claude al historial
            historial.append({"role": "assistant", "content": response.content})

            # Ejecutar cada herramienta
            tool_results = []

            for tool_call in tool_calls:
                # Ejecutar la herramienta
                resultado = ejecutar_herramienta(tool_call.name, tool_call.input)

                # Guardar resultado para Claude
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(resultado, ensure_ascii=False),
                    }
                )

                # Guardar para respuesta al frontend
                herramientas_usadas.append(
                    {
                        "herramienta": tool_call.name,
                        "parametros": tool_call.input,
                        "resultado": resultado,
                    }
                )

                # Detectar si se creó una cita exitosamente
                if (
                    tool_call.name == "crear_cita"
                    and resultado.get("status") == "success"
                ):
                    cita_creada = True
                    datos_cita = resultado.get("data")

            # Agregar resultados de herramientas al historial
            historial.append({"role": "user", "content": tool_results})

            # Obtener respuesta final de Claude
            final_response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=historial,
                tools=TOOLS,
            )

            # Extraer texto de respuesta final
            respuesta_texto = ""
            for block in final_response.content:
                if block.type == "text":
                    respuesta_texto += block.text

            # Agregar respuesta final al historial
            historial.append({"role": "assistant", "content": respuesta_texto})

        else:
            # No hubo tool calls, solo respuesta de texto
            historial.append({"role": "assistant", "content": respuesta_texto})

        # Guardar historial actualizado
        conversaciones[conv_id] = historial

        # Devolver respuesta
        return MensajeResponse(
            respuesta=respuesta_texto,
            conversacion_id=conv_id,
            herramientas_usadas=herramientas_usadas,
            cita_creada=cita_creada,
            datos_cita=datos_cita,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el chat: {str(e)}")


@router.post("/reset/{conversacion_id}")
async def reset_conversacion(conversacion_id: str):
    """Reinicia una conversación específica"""
    if conversacion_id in conversaciones:
        del conversaciones[conversacion_id]
        return {"status": "success", "message": "Conversación reiniciada"}
    return {"status": "info", "message": "Conversación no existía"}


@router.get("/conversaciones")
async def listar_conversaciones():
    """Lista todas las conversaciones activas"""
    return {"total": len(conversaciones), "conversaciones": list(conversaciones.keys())}


# ==================== FUNCIONES AUXILIARES ====================


def ejecutar_herramienta(tool_name: str, tool_input: dict) -> dict:
    """Ejecuta una herramienta usando las funciones importadas"""
    try:
        if tool_name == "buscar_cliente":
            return buscar_cliente(identified=tool_input["identified"])

        elif tool_name == "crear_cliente":
            return crear_cliente(
                fullName=tool_input["fullName"],
                fullSurname=tool_input["fullSurname"],
                identified=tool_input["identified"],
            )

        elif tool_name == "crear_contacto":
            return crear_contacto(
                clientId=tool_input["clientId"],
                phoneNumber=tool_input["phoneNumber"],
                email=tool_input["email"],
                address=tool_input.get("address", ""),
            )

        elif tool_name == "crear_cita":
            return crear_cita(
                clientId=tool_input["clientId"],
                appointmentDate=tool_input["appointmentDate"],
                ubicacion=tool_input["ubicacion"],
                details=tool_input.get("details"),
                state=tool_input.get("state", "ASIGNADA"),
                employedId=tool_input.get("employedId"),
            )

        else:
            return {
                "status": "error",
                "message": f"Herramienta desconocida: {tool_name}",
            }

    except TypeError as e:
        return {"status": "error", "message": f"Parámetros incorrectos: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error al ejecutar: {str(e)}"}
