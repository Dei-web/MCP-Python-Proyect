import json
from sqlalchemy.orm import Session
from app.schemas.appointment import AppointmentCreate
from app.models.modelos import AppointmentScheduling
from app.models.modelos import Client
from app.models.enums.appointment_state import AppointmentState
from app.repository.appointment_repo import AppointmentRepository


class AppointmentService:
    @staticmethod
    def crear_cita(db: Session, data: AppointmentCreate) -> str:
        client = db.query(Client).filter(Client.id == data.clientId).first()
        if not client:
            return json.dumps(
                {"status": "error", "message": "El cliente no existe"},
                indent=2,
                ensure_ascii=False,
            )

        cita = AppointmentScheduling(
            appointmentDate=data.appointmentDate,
            ubicacion=data.ubicacion,
            details=data.details,
            appointmentState=data.state,
            clientId=data.clientId,
            employedId=None,
        )

        cita = AppointmentRepository.create(db, cita)

        return json.dumps(
            {
                "status": "success",
                "message": "Cita creada correctamente",
                "appointmentId": cita.id,
            },
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def obtener_cita(db: Session, appointment_id: int) -> str:
        cita = AppointmentRepository.get_by_id(db, appointment_id)
        if not cita:
            return json.dumps(
                {"status": "error", "message": "Cita no encontrada"},
                indent=2,
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "id": cita.id,
                "date": str(cita.appointmentDate),
                "ubicacion": cita.ubicacion,
                "details": cita.details,
                "state": cita.appointmentState.value,
                "clientId": cita.clientId,
                "employedId": cita.employedId,
            },
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def listar_citas(db: Session) -> str:
        citas = AppointmentRepository.list(db)

        if not citas:
            return json.dumps(
                {"status": "success", "message": "No hay citas registradas"},
                indent=2,
                ensure_ascii=False,
            )

        return json.dumps(
            [
                {
                    "id": c.id,
                    "date": str(c.appointmentDate),
                    "ubicacion": c.ubicacion,
                    "state": c.appointmentState.value,
                    "clientId": c.clientId,
                }
                for c in citas
            ],
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def eliminar_cita(db: Session, appointment_id: int) -> str:
        ok = AppointmentRepository.delete(db, appointment_id)
        if not ok:
            return json.dumps(
                {"status": "error", "message": "Cita no encontrada"},
                indent=2,
                ensure_ascii=False,
            )

        return json.dumps(
            {"status": "success", "message": "Cita eliminada"},
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def obtener_citas_por_cliente(db: Session, client_id: int) -> str:
        citas = AppointmentRepository.get_all_by_id(db, client_id)

        if not citas:
            return json.dumps(
                {
                    "status": "success",
                    "message": "El cliente no tiene citas registradas",
                    "citas": [],
                },
                indent=2,
                ensure_ascii=False,
            )

        return json.dumps(
            [
                {
                    "id": c.id,
                    "date": str(c.appointmentDate),
                    "ubicacion": c.ubicacion,
                    "details": c.details,
                    "state": c.appointmentState.value,
                    "clientId": c.clientId,
                    "employedId": c.employedId,
                }
                for c in citas
            ],
            indent=2,
            ensure_ascii=False,
        )
