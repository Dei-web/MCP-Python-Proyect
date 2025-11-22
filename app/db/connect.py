import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    def validate(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL no está definida en el archivo .env")

        if not self.DATABASE_URL.startswith("postgresql://"):
            raise ValueError("DATABASE_URL debe comenzar con 'postgresql://'")


settings = Settings()
