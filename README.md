# Deepdevflow

A multi-agent framework built with Google's Agent Development Kit (ADK).

## Overview

Deepdevflow is a powerful application that allows you to create, manage, and orchestrate conversations between multiple AI agents. It provides a user-friendly interface for interacting with AI agents and enables saving conversations by session ID.

The framework follows the MVC (Model-View-Controller) pattern:
- **Backend**: FastAPI server that serves as the API and controller layer
- **Frontend**: Streamlit UI that provides the view layer
- **Database**: SQLAlchemy ORM for the model layer

## Features

- 🤖 Multi-agent conversations with Google ADK integration
- 💾 Session-based conversation management and persistence
- 🔌 Support for remote agent integration
- 🧠 Multiple LLM providers (OpenAI, LiteLLM, Ollama, etc.)
- 🎨 Clean and responsive Streamlit UI
- 🔄 Real-time streaming responses
- 📊 Detailed visualization of agent activities

## Architecture

The application follows a clean architecture with separation of concerns:

```
Deepdevflow/
├── backend/             # FastAPI backend
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   │   ├── agent/       # Agent implementations
│   │   └── llm/         # LLM providers
│   └── utils/           # Utilities
├── frontend/            # Streamlit frontend
│   ├── components/      # UI components
│   ├── pages/           # Page views
│   ├── services/        # API client
│   ├── styles/          # CSS styles
│   └── utils/           # Utilities
└── config/              # Configuration files
```

## Getting Started

### Prerequisites

- Python 3.9+
- uv (modern Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/deepdevflow.git
   cd deepdevflow
   ```

2. Create and activate a virtual environment using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install the dependencies with uv:
   ```bash
   uv pip install -e .
   ```

   For development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

4. Create the configuration files:
   ```bash
   cp config/config.yaml.example config/config.yaml
   cp config/llm_config.yaml.example config/llm_config.yaml
   cp config/agent_config.yaml.example config/agent_config.yaml
   ```

5. Edit the configuration files with your settings.

### Running the Application

1. Start the backend server:
   ```bash
   python -m backend.app
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run frontend/app.py
   ```

3. Open your browser and navigate to:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/docs

## Usage

### Creating a Session

1. Navigate to the home page
2. Click on "New Session"
3. Enter a name for your session
4. Click "Create"

### Starting a Conversation

1. Select a session from the sessions list
2. Click on "New Conversation"
3. Enter a name for your conversation
4. Click "Create"

### Chatting with Agents

1. Select a conversation
2. Type your message in the input field
3. Press Enter to send the message
4. The appropriate agent will handle your query based on its capabilities

### Managing Agents

1. Navigate to the "Agents" page
2. View a list of all registered agents
3. Add new agents by clicking "Add New Agent"
4. Configure agent settings such as name, description, capabilities, and LLM model

## Configuration

### LLM Providers

The framework supports multiple LLM providers:

- **OpenAI**: GPT-4, GPT-3.5-Turbo
- **Anthropic**: Claude models
- **LiteLLM**: A unified interface to multiple LLM providers
- **Ollama**: Local LLM deployment

Configure providers in `config/llm_config.yaml`

### Agent Configuration

Configure agents in `config/agent_config.yaml`:

- Host agent configuration
- Remote agent connection settings
- Default capabilities and tools

### Application Settings

Configure general settings in `config/config.yaml`:

- Database connection string
- Server host and port
- Debug mode
- Default settings

## Development

### Using uv for Dependency Management

Deepdevflow uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management. uv is a modern replacement for pip that offers significant performance improvements and better dependency resolution.

Key uv commands:
- `uv venv`: Create a virtual environment
- `uv pip install -e .`: Install the package in development mode
- `uv pip install -e ".[dev]"`: Install with development dependencies
- `uv pip freeze`: Export dependencies to requirements.txt
- `uv pip compile pyproject.toml`: Generate a lock file

### Code Formatting

The project uses Black and isort for code formatting:

```bash
# Format code
black .
isort .
```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google's Agent Development Kit
- FastAPI framework
- Streamlit UI library
- SQLAlchemy ORM
- uv package manager
