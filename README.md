# CodexAid - MCP Self-Learning Service

A powerful service for building, managing, and deploying self-learning and self-generating MCP (Model Context Protocol) agents.

## Overview

CodexAid is a framework that allows you to create intelligent MCP agents that can learn from tasks and generate new skills on their own. The system follows a design-develop-deploy pipeline that turns natural language prompts into functional MCP servers with custom tools.

## Features

- **Self-Learning**: Create agents that can learn from user interactions
- **Self-Generation**: Generate new MCP servers based on natural language prompts
- **Tool Generation**: Automatically create and deploy new tools based on requirements
- **FastAPI Integration**: Expose MCP functionality through an HTTP API
- **Design-Develop Pipeline**: Structured approach to converting tasks into working code

## Architecture

The system consists of several key components:

- **Designer**: Analyzes tasks and creates specifications for development
- **Developer**: Implements tools based on specifications
- **MCP Builder**: Constructs MCP servers from developed tools
- **Tool Server**: FastAPI server that hosts and manages MCP tools

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Dependencies listed in pyproject.toml

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd CodexAid

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Usage

1. Start the Tool Server:

```bash
python mcp_service/tool_server.py
```

2. Create a new MCP from a prompt:

```python
from scr.work import mcp_create

# Generate a new MCP server from a natural language prompt
mcp_str = mcp_create("Create a tool that summarizes web content")

# Save the generated server
with open("my_new_mcp.py", "w") as f:
    f.write(mcp_str)
```

3. Use the HTTP API to generate new MCPs:

```bash
curl -X POST "http://localhost:8848/new_mcp" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Create a tool that searches for information"}'
```

## API Endpoints

- `GET /health` - Check server health
- `GET /reset` - Reset the MCP manager
- `GET /get_tool` - Get available tools
- `GET /get_tool/{agent_name}` - Get tools for a specific agent
- `POST /call_tool/{tool_name}` - Call a specific tool
- `POST /new_mcp` - Generate a new MCP from a prompt

## Configuration

Edit the `config.py` file to configure:

- LLM API endpoints and keys
- MCP service paths
- Server port

## Examples

### Creating a Learning Timer

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("LearningTimer")

@mcp.tool(description='Start a learning timer when detected')
async def start_learning_timer():
    # Implementation details
    pass

if __name__ == '__main__':
    mcp.run(transport='stdio')
```

## License

See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
