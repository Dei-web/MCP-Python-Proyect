from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class AppointmentState(str, Enum):
    ASIGNADA = "ASIGNADA"
    COMPLETADA = "COMPLETADA"
    PENDIENTE = "PENDIENTE"
    CANCELADA = "CANCELADA"


class AppointmentBase(BaseModel):
    appointmentDate: datetime | str
    ubicacion: str
    details: Optional[str] = None
    state: AppointmentState = AppointmentState.ASIGNADA  # ⚡ valor por defecto


class AppointmentCreate(AppointmentBase):
    clientId: int
    employedId: Optional[int] = None


class AppointmentResponse(AppointmentBase):
    id: int

    model_config = {
        "from_attributes": True  # ⚡ Pydantic v2
    }
