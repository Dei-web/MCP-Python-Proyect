"""
Servidor MCP para el Bot de Taller Express
Expone las herramientas a través del protocolo MCP
"""

from app.mcp.agent import agent

if __name__ == "__main__":
    agent.run()
