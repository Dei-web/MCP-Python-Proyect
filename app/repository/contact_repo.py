from sqlalchemy.orm import Session
from app.models.modelos import ClientContact
from app.schemas.client_contact import ClientContactCreate
from datetime import datetime


def create_client_contact(db: Session, data: ClientContactCreate):
    now = datetime.utcnow()  # fecha actual en UTC
    contact = ClientContact(
        clientId=data.clientId,
        phoneNumber=data.phoneNumber,
        email=data.email,
        address=data.address,
        createAt=now,
        updatedAt=now,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact
