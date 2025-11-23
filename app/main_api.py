from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.bot_router import router

app = FastAPI(
    title="Taller Express Bot API",
    description="API REST para el bot de agendamiento de citas",
    version="1.0.0",
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas del bot
app.include_router(router, prefix="/api", tags=["Bot"])


@app.get("/")
def root():
    return {
        "message": "Taller Express Bot API",
        "endpoints": {
            "chat": "POST /api/chat",
            "reset": "POST /api/reset/{conversacion_id}",
            "conversaciones": "GET /api/conversaciones",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
