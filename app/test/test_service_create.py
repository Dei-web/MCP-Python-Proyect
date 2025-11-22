from datetime import datetime
from sqlalchemy.orm import Session
from app.models.enums import appointment_state
from app.services.citas_service import AppointmentService
from app.schemas.appointment import AppointmentCreate
from app.models.modelos import Client
from app.db.config import get_db


def test_crear_cita():
    db: Session = next(get_db())

    # Asegurarse de que el cliente exista
    cliente = db.query(Client).filter(Client.identified == "123456789").first()
    if not cliente:
        cliente = Client(fullName="Alex", fullSurname="Perez", identified="123456789")
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # Crear la cita
    data = AppointmentCreate(
        appointmentDate=datetime.now(),
        ubicacion="Taller Central",
        details="Cambio de vida ",
        clientId=2,
    )

    resp = AppointmentService.crear_cita(db, data)

    assert "success" in resp
    assert "appointmentId" in resp
