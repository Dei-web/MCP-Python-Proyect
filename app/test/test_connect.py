from app.db.config import get_db
from sqlalchemy import text


def test_connection():
    try:
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        print("Conexión exitosa:", result.scalar())
    except Exception as e:
        print("Error al conectar:", str(e))


if __name__ == "__main__":
    test_connection()
