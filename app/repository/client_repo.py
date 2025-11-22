from re import fullmatch
from sqlalchemy.orm import Session, identity
from app.schemas.client import ClientCreate, ClientResponse
from app.models.modelos import Client
from datetime import datetime


def create_client(db: Session, data: ClientCreate):
    client = Client(
        fullName=data.fullName,
        fullSurname=data.fullSurname,
        identified=data.identified,
        updatedAt=datetime.utcnow(),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client_by_id(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()


def get_client_by_identified(db: Session, identified: str):
    return db.query(Client).filter(Client.identified == identified).first()
