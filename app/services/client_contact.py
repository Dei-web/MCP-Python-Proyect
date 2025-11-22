import json
from sqlalchemy.orm import Session
from app.schemas.client_contact import ClientContactCreate
from app.models.modelos import ClientContact
from app.repository.contact_repo import create_client_contact


class ClientContactService:
    @staticmethod
    def crear_contacto(db: Session, data: ClientContactCreate) -> str:
        """Crea un dato de contacto para un cliente."""
        try:
            contacto = create_client_contact(db, data)

            return json.dumps(
                {
                    "status": "success",
                    "message": "Contacto registrado correctamente",
                    "contactId": contacto.id,
                    "clientId": contacto.clientId,
                },
                indent=2,
                ensure_ascii=False,
            )

        except Exception as e:
            db.rollback()
            return f"Error creando contacto: {str(e)}"

    @staticmethod
    def obtener_contacto(db: Session, contact_id: int) -> str:
        """Obtiene un contacto por ID."""
        try:
            contacto = (
                db.query(ClientContact).filter(ClientContact.id == contact_id).first()
            )

            if not contacto:
                return json.dumps(
                    {"status": "error", "message": "Contacto no encontrado"},
                    indent=2,
                    ensure_ascii=False,
                )

            data = {
                "id": contacto.id,
                "phoneNumber": contacto.phoneNumber,
                "email": contacto.email,
                "address": contacto.address,
                "clientId": contacto.clientId,
                "createdAt": str(contacto.createAt),
                "updatedAt": str(contacto.updatedAt),
            }

            return json.dumps(data, indent=2, ensure_ascii=False)

        except Exception as e:
            return f"Error obteniendo contacto: {str(e)}"

    @staticmethod
    def listar_contactos(db: Session, client_id: int) -> str:
        """
        Lista contactos.
        Si `client_id` viene, filtra por cliente.
        """
        try:
            query = db.query(ClientContact)

            if client_id:
                query = query.filter(ClientContact.clientId == client_id)

            contactos = query.all()

            if not contactos:
                return json.dumps(
                    {"status": "success", "message": "No hay contactos registrados"},
                    indent=2,
                    ensure_ascii=False,
                )

            resultado = [
                {
                    "id": c.id,
                    "phoneNumber": c.phoneNumber,
                    "email": c.email,
                    "address": c.address,
                    "clientId": c.clientId,
                }
                for c in contactos
            ]

            return json.dumps(resultado, indent=2, ensure_ascii=False)

        except Exception as e:
            return f"Error listando contactos: {str(e)}"

    @staticmethod
    def eliminar_contacto(db: Session, contact_id: int) -> str:
        """Elimina un contacto por ID."""
        try:
            contacto = (
                db.query(ClientContact).filter(ClientContact.id == contact_id).first()
            )

            if not contacto:
                return json.dumps(
                    {"status": "error", "message": "El contacto no existe"},
                    indent=2,
                    ensure_ascii=False,
                )

            db.delete(contacto)
            db.commit()

            return json.dumps(
                {"status": "success", "message": "Contacto eliminado exitosamente"},
                indent=2,
                ensure_ascii=False,
            )

        except Exception as e:
            db.rollback()
            return f"Error eliminando contacto: {str(e)}"
