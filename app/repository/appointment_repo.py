from sqlalchemy.orm import Session
from app.models.modelos import AppointmentScheduling


class AppointmentRepository:
    @staticmethod
    def create(db: Session, appointment: AppointmentScheduling):
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def get_by_id(db: Session, appointment_id: int):
        return (
            db.query(AppointmentScheduling)
            .filter(AppointmentScheduling.id == appointment_id)
            .first()
        )

    @staticmethod
    def list(db: Session):
        return db.query(AppointmentScheduling).all()

    @staticmethod
    def delete(db: Session, appointment_id: int):
        cita = AppointmentRepository.get_by_id(db, appointment_id)
        if not cita:
            return None
        db.delete(cita)
        db.commit()
        return True

    @staticmethod
    def get_all_by_id(db: Session, id_u: int):
        return (
            db.query(AppointmentScheduling)
            .filter(AppointmentScheduling.id == id_u)
            .all()
        )
