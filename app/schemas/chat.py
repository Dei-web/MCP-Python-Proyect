from pydantic import BaseModel
from typing import Optional, List


# Modelos Pydantic
class MensajeRequest(BaseModel):
    mensaje: str
    conversacion_id: Optional[str] = None


class MensajeResponse(BaseModel):
    respuesta: str
    conversacion_id: str
    herramientas_usadas: List[dict] = []
    cita_creada: bool = False
    datos_cita: Optional[dict] = None
