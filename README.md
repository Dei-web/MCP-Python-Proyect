# 🤖 Taller Express Bot

Bot inteligente para agendamiento de citas en taller mecánico usando Claude AI.

## 📋 Características

- ✅ Conversación natural con clientes
- ✅ Registro automático de clientes nuevos
- ✅ Búsqueda de clientes existentes
- ✅ Creación de citas con confirmación
- ✅ Integración con base de datos PostgreSQL
- ✅ Dos modos de operación: **API REST** y **MCP (Claude Desktop)**

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repo>
cd taller-express-bot
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz:
```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:password@localhost:5432/taller_db

# API Key de Anthropic (solo para modo API)
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 5. Crear la base de datos
```bash
# Ejecutar migraciones o crear tablas manualmente
psql -U usuario -d taller_db -f schema.sql
```

---

## 🎯 Modos de Uso

### **Modo 1: API REST** (Para aplicaciones web/móvil)

#### Iniciar el servidor
```bash
python main_api.py
```

El servidor estará disponible en `http://localhost:8000`

#### Endpoints disponibles:

**1. Chat con el bot**
```bash
POST /api/chat
Content-Type: application/json

{
  "mensaje": "Hola, necesito una cita para cambio de aceite",
  "conversacion_id": "conv_123" // opcional
}
```

**Respuesta:**
```json
{
  "respuesta": "¡Hola! Con gusto te ayudo...",
  "conversacion_id": "conv_123",
  "herramientas_usadas": [...],
  "cita_creada": false,
  "datos_cita": null
}
```

**2. Reiniciar conversación**
```bash
POST /api/reset/conv_123
```

**3. Listar conversaciones activas**
```bash
GET /api/conversaciones
```

#### Ejemplo de uso con curl:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Quiero agendar una cita para revisión general"
  }'
```

---

### **Modo 2: MCP (Claude Desktop)** (Para uso directo en Claude)

#### 1. Configurar Claude Desktop

Edita el archivo de configuración de Claude Desktop:

**macOS/Linux:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### 2. Agregar configuración del servidor MCP

```json
{
  "mcpServers": {
    "taller-express-bot": {
      "command": "python",
      "args": [
        "/ruta/completa/a/tu/proyecto/server.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://usuario:password@localhost:5432/taller_db",
        "PYTHONPATH": "/ruta/completa/a/tu/proyecto"
      }
    }
  }
}
```

**⚠️ IMPORTANTE:** Reemplaza las rutas con las rutas absolutas reales de tu sistema.

#### 3. Reiniciar Claude Desktop

Cierra completamente Claude Desktop y vuelve a abrirlo.

#### 4. Verificar conexión

En Claude Desktop, deberías ver el icono 🔨 indicando que el servidor MCP está conectado.

#### 5. Usar el bot

Simplemente chatea con Claude:
```
"Hola, necesito agendar una cita para cambio de aceite el próximo martes a las 10am"
```

Claude usará automáticamente las herramientas del bot para:
- Buscar si eres cliente existente
- Crear tu registro si eres nuevo
- Registrar tu información de contacto
- Crear la cita en el sistema

---

## 🛠️ Estructura del Proyecto

```
taller-express-bot/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── bot_router.py          # API REST endpoints
│   ├── mcp/
│   │   └── agent.py                # Definición de herramientas MCP
│   ├── db/
│   │   ├── config.py               # Configuración SQLAlchemy
│   │   └── connect.py              # Conexión a DB
│   ├── models/
│   │   └── modelos.py              # Modelos SQLAlchemy
│   ├── schemas/
│   │   ├── client.py
│   │   ├── client_contact.py
│   │   └── appointment.py
│   ├── repository/
│   │   ├── client_repo.py
│   │   ├── contact_repo.py
│   │   └── appointment_repo.py
│   └── services/
│       ├── client_service.py
│       ├── client_contact.py
│       └── citas_service.py
├── server.py                       # Servidor MCP
├── main_api.py                     # Servidor API REST
├── requirements.txt
├── .env
└── README.md
```

---

## 🧪 Testing

```bash
# Probar conexión a base de datos
python -m app.test.test_connect

# Probar creación de cliente
python -m app.test.test_client_create

# Probar creación de contacto
python -m app.test.test_contacs

# Probar creación de cita
python -m app.test.test_service_create
```

---

## 🔧 Herramientas Disponibles

El bot tiene acceso a 4 herramientas principales:

1. **buscar_cliente(identified: str)**
   - Busca un cliente por número de identificación
   - Retorna datos completos si existe

2. **crear_cliente(fullName: str, fullSurname: str, identified: str)**
   - Registra un nuevo cliente
   - Solo si no existe previamente

3. **crear_contacto(clientId: int, phoneNumber: str, email: str, address: str)**
   - Registra información de contacto del cliente

4. **crear_cita(clientId: int, appointmentDate: str, ubicacion: str, details: str)**
   - Crea una cita en el sistema
   - Formato fecha: "YYYY-MM-DD HH:MM:SS"

---

## 📊 Flujo de Conversación

```mermaid
graph TD
    A[Cliente inicia conversación] --> B[Bot identifica necesidad]
    B --> C[Solicita datos del cliente]
    C --> D{Cliente existe?}
    D -->|No| E[Crear nuevo cliente]
    D -->|Sí| F[Recuperar datos]
    E --> G[Crear contacto]
    F --> G
    G --> H[Confirmar datos]
    H --> I[Ofrecer fechas disponibles]
    I --> J[Crear cita]
    J --> K[Confirmación final]
```

---

## 🚨 Troubleshooting

### El servidor MCP no se conecta en Claude Desktop
1. Verifica las rutas absolutas en el config
2. Asegúrate de que Python esté en tu PATH
3. Revisa los logs de Claude Desktop
4. Prueba el servidor manualmente: `python server.py`

### Error de base de datos
1. Verifica que PostgreSQL esté corriendo
2. Confirma las credenciales en `.env`
3. Prueba la conexión: `python -m app.test.test_connect`

### API REST no responde
1. Verifica que el puerto 8000 esté libre
2. Confirma que ANTHROPIC_API_KEY esté configurada
3. Revisa logs en la consola

---

## 📝 Próximas Mejoras

- [ ] Autenticación de usuarios
- [ ] Notificaciones por email/SMS
- [ ] Panel administrativo web
- [ ] Integración con calendario
- [ ] Recordatorios automáticos
- [ ] Historial de servicios

---

## 📄 Licencia

MIT License

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📞 Soporte

Para preguntas o soporte, contacta a [tu-email@ejemplo.com]
```
