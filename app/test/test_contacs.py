from app.services.client_contact import ClientContactService
from app.db.config import get_db
from app.schemas.client_contact import ClientContactCreate
import json


def test_create_cliente_contact():
    db = next(get_db())

    data = ClientContactCreate(
        clientId=2,  # Debe existir en la DB
        phoneNumber="1234567890",
        email="test@example.com",
        address="Calle Falsa 123",
    )

    resp = ClientContactService.crear_contacto(db, data)
    resp_dict = json.loads(resp)

    assert resp_dict["status"] == "success"
    assert "contactId" in resp_dict
