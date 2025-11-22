from app.models.modelos import Client
from app.schemas.client import ClientCreate
from app.services.client_service import ClienteService
from app.db.config import get_db
import json


def test_create_cliente():
    db = next(get_db())

    data = ClientCreate(fullName="Juan", fullSurname="Pérez", identified="123456")

    resp = ClienteService.registrar_cliente(db, data)
    assert resp["status"] == "success"
    assert "clientId" in resp
