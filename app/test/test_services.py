from app.services.client_service import ClienteService
from app.db.config import get_db


def test_buscar_cliente():
    db = next(get_db())

    data = "123456789"

    resp = ClienteService.buscar_cliente(db, data)

    assert "success" in resp
