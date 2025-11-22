import json
from datetime import datetime
from fastmcp import FastMCP
from app.db.config import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentState
from app.services.citas_service import AppointmentService
from app.services.client_service import ClienteService
from app.schemas.client import ClientCreate
from app.services.client_contact import ClientContactService
from app.schemas.client_contact import ClientContactCreate

agent = FastMCP("Sistema de Gestión de Citas")

# ==================== FUNCIONES DE LÓGICA (SIN DECORADORES) ====================
# Estas funciones son "puras" y pueden ser importadas en otros módulos


def _crear_cliente_logic(fullName: str, fullSurname: str, identified: str) -> dict:
    """Lógica para crear un nuevo cliente"""
    db = next(get_db())
    try:
        data = ClientCreate(
            fullName=fullName, fullSurname=fullSurname, identified=identified
        )
        response = ClienteService.registrar_cliente(db, data)
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def _buscar_cliente_logic(identified: str) -> dict:
    """Lógica para buscar un cliente por identificación"""
    db = next(get_db())
    try:
        response = ClienteService.buscar_cliente(db, identified)
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def _listar_clientes_logic() -> dict:
    """Lógica para listar todos los clientes activos"""
    db = next(get_db())
    try:
        response = ClienteService.listar_clientes(db)
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def _crear_contacto_logic(
    clientId: int, phoneNumber: str, email: str, address: str = ""
) -> dict:
    """Lógica para crear un contacto para un cliente"""
    db = next(get_db())
    try:
        data = ClientContactCreate(
            clientId=clientId, phoneNumber=phoneNumber, email=email, address=address
        )
        response = ClientContactService.crear_contacto(db, data)
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def _crear_cita_logic(
    clientId: int,
    appointmentDate: str,
    ubicacion: str,
    details: str | None = None,
    state: str = "ASIGNADA",
    employedId: int | None = None,
) -> dict:
    """Lógica para crear una nueva cita"""
    db = next(get_db())
    try:
        data = AppointmentCreate(
            clientId=clientId,
            appointmentDate=appointmentDate,
            ubicacion=ubicacion,
            details=details,
            state=AppointmentState(state),
            employedId=employedId,
        )
        result = AppointmentService.crear_cita(db, data)
        return json.loads(result)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


# ==================== HERRAMIENTAS MCP (CON DECORADORES) ====================
# Estas son las herramientas para FastMCP/Claude Desktop


@agent.tool(
    description="Registra un nuevo cliente en el sistema. Requiere: fullName, fullSurname, identified"
)
def crear_cliente(fullName: str, fullSurname: str, identified: str) -> dict:
    """Crea un nuevo cliente"""
    return _crear_cliente_logic(fullName, fullSurname, identified)


@agent.tool(description="Busca un cliente por su número de identificación")
def buscar_cliente(identified: str) -> dict:
    """Busca un cliente por identificación"""
    return _buscar_cliente_logic(identified)


@agent.tool(description="Lista todos los clientes registrados en el sistema")
def listar_clientes() -> dict:
    """Lista todos los clientes activos"""
    return _listar_clientes_logic()


@agent.tool(
    description="Crea un contacto para un cliente. Requiere: clientId, phoneNumber, email, address (opcional)"
)
def crear_contacto(
    clientId: int, phoneNumber: str, email: str, address: str = ""
) -> dict:
    """Crea un contacto para un cliente"""
    return _crear_contacto_logic(clientId, phoneNumber, email, address)


@agent.tool(
    description="Crea una cita para un cliente. Requiere: clientId, appointmentDate (YYYY-MM-DD HH:MM:SS), ubicacion, details (opcional), state (opcional), employedId (opcional)"
)
def crear_cita(
    clientId: int,
    appointmentDate: str,
    ubicacion: str,
    details: str | None = None,
    state: str = "ASIGNADA",
    employedId: int | None = None,
) -> dict:
    """Crea una nueva cita"""
    return _crear_cita_logic(
        clientId, appointmentDate, ubicacion, details, state, employedId
    )
