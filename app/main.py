# import os
# from fastapi import FastAPI
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from openai import OpenAI
# from app.db.config import get_db
# from app.schemas.client import ClientCreate
# from app.schemas.client_contact import ClientContactCreate
# from app.schemas.appointment import AppointmentCreate, AppointmentState
# from app.services.client_service import ClienteService
# from app.services.client_contact import ClientContactService
# from app.services.citas_service import AppointmentService
#
# app = FastAPI(
#     title="Sistema de Gestión de Citas con IA (OpenAI)",
#     description="API para gestionar clientes, contactos y citas usando GPT-4.1",
#     version="1.0.0",
# )
#
#
# # ==================== MODELO PARA CHAT ====================
# class ChatRequest(BaseModel):
#     message: str
#     conversation_history: list = []
#
#
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
#
# # ==================== ENDPOINT ====================
# @app.post("/chat", tags=["IA"])
# async def chat_with_ai(request: ChatRequest):
#     """
#     Interactúa con GPT para gestionar clientes, contactos y citas.
#     """
#
#     # Definición de funciones (herramientas)
#     tools = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "crear_cliente",
#                 "description": "Registra un nuevo cliente en el sistema",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "fullName": {"type": "string"},
#                         "fullSurname": {"type": "string"},
#                         "identified": {"type": "string"},
#                     },
#                     "required": ["fullName", "fullSurname", "identified"],
#                 },
#             },
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "buscar_cliente",
#                 "description": "Busca un cliente por su identificación",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {"identified": {"type": "string"}},
#                     "required": ["identified"],
#                 },
#             },
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "listar_clientes",
#                 "description": "Lista todos los clientes registrados",
#                 "parameters": {"type": "object", "properties": {}},
#             },
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "crear_contacto",
#                 "description": "Crea un contacto para un cliente",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "clientId": {"type": "integer"},
#                         "phoneNumber": {"type": "string"},
#                         "email": {"type": "string"},
#                         "address": {"type": "string"},
#                     },
#                     "required": ["clientId", "phoneNumber", "email"],
#                 },
#             },
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "crear_cita",
#                 "description": "Crea una cita para un cliente",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "clientId": {"type": "integer"},
#                         "appointmentDate": {"type": "string"},
#                         "ubicacion": {"type": "string"},
#                         "details": {"type": "string"},
#                         "state": {
#                             "type": "string",
#                             "enum": [
#                                 "ASIGNADA",
#                                 "COMPLETADA",
#                                 "PENDIENTE",
#                                 "CANCELADA",
#                             ],
#                         },
#                         "employedId": {"type": "integer"},
#                     },
#                     "required": ["clientId", "appointmentDate", "ubicacion"],
#                 },
#             },
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "listar_citas_cliente",
#                 "description": "Lista todas las citas de un cliente",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {"clientId": {"type": "integer"}},
#                     "required": ["clientId"],
#                 },
#             },
#         },
#     ]
#
#     # Construcción del historial
#     messages = request.conversation_history + [
#         {"role": "user", "content": request.message}
#     ]
#
#     # Llamada inicial
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         tools=tools,
#         tool_choice="auto",
#     )
#
#     msg = response.choices[0].message
#
#     # Si GPT quiere usar herramientas
#     while msg.tool_calls:
#         tool_messages = []
#
#         for tool_call in msg.tool_calls:
#             tool_name = tool_call.function.name
#             tool_args = eval(tool_call.function.arguments)
#
#             result = execute_tool(tool_name, tool_args)
#
#             tool_messages.append(
#                 {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}
#             )
#
#         messages.append({"role": "assistant", "content": msg})
#
#         messages.extend(tool_messages)
#
#         # Nueva llamada
#         response = client.chat.completions.create(
#             model="gpt-4.1",
#             messages=messages,
#             tools=tools,
#         )
#         msg = response.choices[0].message
#
#     # Cuando ya no hay más tool_calls
#     return {
#         "response": msg.content,
#         "conversation_history": messages + [{"role": "assistant", "content": msg}],
#     }
#
#
# # ==================== EJECUCIÓN DE HERRAMIENTAS ====================
# def execute_tool(tool_name: str, tool_input: dict):
#     db = next(get_db())
#     try:
#         if tool_name == "crear_cliente":
#             data = ClientCreate(**tool_input)
#             return ClienteService.registrar_cliente(db, data)
#
#         elif tool_name == "buscar_cliente":
#             return ClienteService.buscar_cliente(db, tool_input["identified"])
#
#         elif tool_name == "listar_clientes":
#             return ClienteService.listar_clientes(db)
#
#         elif tool_name == "crear_contacto":
#             data = ClientContactCreate(**tool_input)
#             return ClientContactService.crear_contacto(db, data)
#
#         elif tool_name == "crear_cita":
#             if "state" in tool_input:
#                 tool_input["state"] = AppointmentState(tool_input["state"])
#
#             data = AppointmentCreate(**tool_input)
#             return AppointmentService.crear_cita(db, data)
#
#         elif tool_name == "listar_citas_cliente":
#             return AppointmentService.obtener_citas_por_cliente(
#                 db, tool_input["clientId"]
#             )
#
#         return {"error": f"Herramienta {tool_name} no encontrada"}
#
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         db.close()
