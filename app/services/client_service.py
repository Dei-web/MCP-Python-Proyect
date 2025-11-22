from sqlalchemy.orm import Session
from app.schemas.client import ClientCreate
from app.repository.client_repo import (
    create_client,
    get_client_by_id,
    get_client_by_identified,
)


class ClienteService:
    @staticmethod
    def buscar_cliente(db: Session, identified: str):
        """Busca un cliente por identificación usando el repository."""
        try:
            cliente = get_client_by_identified(db, identified)

            if cliente:
                return {
                    "status": "success",
                    "data": {
                        "id": cliente.id,
                        "fullName": cliente.fullName,
                        "fullSurname": cliente.fullSurname,
                        "identified": cliente.identified,
                        "clientState": cliente.clientState,
                        "createdAt": cliente.createdAt,
                        "updatedAt": cliente.updatedAt,
                    },
                }

            return {"status": "not_found", "message": "Cliente no encontrado"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def registrar_cliente(db: Session, data: ClientCreate):
        """Registra un nuevo cliente usando el repository."""
        try:
            # Validar existente
            existing = get_client_by_identified(db, data.identified)
            if existing:
                return {
                    "status": "exists",
                    "message": f"El cliente con identificación {data.identified} ya está registrado",
                }

            # Crear cliente en el repo
            nuevo_cliente = create_client(db, data)

            return {
                "status": "success",
                "message": "Cliente registrado exitosamente",
                "clientId": nuevo_cliente.id,
            }

        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

    @staticmethod
    def listar_clientes(db: Session):
        """Lista todos los clientes activos."""
        try:
            from app.models.modelos import Client

            clientes = db.query(Client).filter(Client.clientState == True).all()

            if not clientes:
                return {"status": "empty", "message": "No hay clientes registrados"}

            resultado = [
                {
                    "id": c.id,
                    "fullName": c.fullName,
                    "fullSurname": c.fullSurname,
                    "identified": c.identified,
                    "createdAt": c.createdAt,
                }
                for c in clientes
            ]

            return {"status": "success", "data": resultado}

        except Exception as e:
            return {"status": "error", "message": str(e)}
