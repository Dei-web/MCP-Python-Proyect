#!/usr/bin/env python3
"""
Script para probar el servidor MCP localmente
antes de configurarlo en Claude Desktop
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.mcp.agent import (
    _buscar_cliente_logic as buscar_cliente,
    _crear_cliente_logic as crear_cliente,
    _listar_clientes_logic as listar_clientes,
    _crear_contacto_logic as crear_contacto,
    _crear_cita_logic as crear_cita,
)


def test_tools():
    """Prueba básica de las herramientas MCP"""

    print("🧪 Probando herramientas MCP...\n")

    # 1. Buscar cliente que no existe
    print("1️⃣ Buscando cliente inexistente...")
    result = buscar_cliente("999999999")
    print(f"   Resultado: {result}\n")

    # 2. Crear cliente nuevo
    print("2️⃣ Creando nuevo cliente...")
    result = crear_cliente(
        fullName="María", fullSurname="González Test", identified="999999999"
    )
    print(f"   Resultado: {result}\n")

    # 3. Buscar el cliente creado
    print("3️⃣ Buscando cliente creado...")
    result = buscar_cliente("999999999")
    print(f"   Resultado: {result}\n")

    if result.get("status") == "success":
        client_id = result["data"]["id"]

        # 4. Crear contacto
        print("4️⃣ Creando contacto...")
        result = crear_contacto(
            clientId=client_id,
            phoneNumber="3001234567",
            email="maria.test@example.com",
            address="Calle Test 123",
        )
        print(f"   Resultado: {result}\n")

        # 5. Crear cita
        print("5️⃣ Creando cita...")
        result = crear_cita(
            clientId=client_id,
            appointmentDate="2025-12-01 10:00:00",
            ubicacion="Taller Express - Av. Principal #123, Cali",
            details="Cambio de aceite y revisión general",
            state="ASIGNADA",
        )
        print(f"   Resultado: {result}\n")

    # 6. Listar todos los clientes
    print("6️⃣ Listando todos los clientes...")
    result = listar_clientes()
    print(f"   Resultado: {result}\n")

    print("✅ Pruebas completadas!")


if __name__ == "__main__":
    try:
        test_tools()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
