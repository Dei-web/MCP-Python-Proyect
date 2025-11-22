from app.mcp.agent import agent

if __name__ == "__main__":
    agent.run(transport="http", port=8000)
