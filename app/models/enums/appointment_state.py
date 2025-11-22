import enum


class AppointmentState(enum.Enum):
    ASIGNADA = "ASIGNADA"
    COMPLETADA = "COMPLETADA"
    PENDIENTE = "PENDIENTE"
    CANCELADA = "CANCELADA"
