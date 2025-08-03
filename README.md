# AI Coding Agent Backend

A FastAPI-based backend for a Claude-style AI coding agent using Google's Gemini 2.5 API and LangGraph for orchestration.

## Features

- **Streaming Chat API** - Real-time conversation with AI agent
- **Code Artifact Management** - Extract, store, and manage generated code
- **Memory Management** - Short-term conversation memory using LangGraph
- **WebSocket Support** - Real-time bidirectional communication
- **Code Validation** - Syntax validation and security checks
- **File Downloads** - Download generated code as files
- **Session Management** - Persistent conversation sessions

## Architecture

### Core Components

- **FastAPI** - Modern, fast web framework
- **LangGraph** - Agent orchestration and memory management
- **Gemini 2.5** - Google's language model (free tier)
- **Pydantic** - Data validation and serialization

### Project Structure

```
backend/
├── app/
│   ├── agents/          # LangGraph agents and prompts
│   ├── api/             # REST API endpoints
│   ├── config/          # Configuration management
│   ├── core/            # Core utilities and dependencies
│   ├── models/          # Pydantic data models
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- Google AI API key (Gemini 2.5)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
GOOGLE_API_KEY=your_gemini_api_key_here
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### 4. Running the Application

```bash
# Development mode
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat/chat` - Send message (non-streaming)
- `POST /api/v1/chat/stream` - Send message (streaming)
- `WS /api/v1/chat/ws/{session_id}` - WebSocket chat
- `GET /api/v1/chat/sessions/{session_id}/history` - Get conversation history
- `DELETE /api/v1/chat/sessions/{session_id}` - Clear session
- `GET /api/v1/chat/sessions/{session_id}/stats` - Get session statistics

### Artifact Endpoints

- `GET /api/v1/artifacts/artifacts/{artifact_id}` - Get specific artifact
- `GET /api/v1/artifacts/sessions/{session_id}/artifacts` - Get session artifacts
- `GET /api/v1/artifacts/messages/{message_id}/artifacts` - Get message artifacts
- `GET /api/v1/artifacts/artifacts/{artifact_id}/download` - Download artifact
- `GET /api/v1/artifacts/artifacts/{artifact_id}/preview` - Preview artifact
- `PUT /api/v1/artifacts/artifacts/{artifact_id}` - Update artifact
- `DELETE /api/v1/artifacts/artifacts/{artifact_id}` - Delete artifact
- `POST /api/v1/artifacts/artifacts/{artifact_id}/validate` - Validate artifact

## Usage Examples

### Send a Chat Message

```python
import requests

response = requests.post("http://localhost:8000/api/v1/chat/chat", json={
    "message": "Create a React component for a todo list",
    "session_id": "my-session-123",
    "stream": False
})

print(response.json())
```

### Stream a Response

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat/stream",
    json={
        "message": "Write a Python function to calculate fibonacci numbers",
        "session_id": "my-session-123"
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b"data: "):
        data = line[6:]  # Remove "data: " prefix
        if data != b"[DONE]":
            print(data.decode())
```

### WebSocket Chat

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws/my-session-123");

ws.onopen = () => {
    ws.send(JSON.stringify({
        type: "message",
        message: "Hello, can you help me with coding?"
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## Key Features

### 1. LangGraph Integration

The agent uses LangGraph for:
- **Memory Management** - Maintains conversation context
- **Workflow Orchestration** - Structured request processing
- **State Management** - Persistent session state

### 2. Code Artifact System

Automatically extracts and manages code from AI responses:
- **Language Detection** - Identifies programming languages
- **Syntax Highlighting** - Proper code formatting
- **Validation** - Basic syntax and security checks
- **Preview Generation** - Runnable HTML previews for web code

### 3. Streaming Responses

Supports real-time streaming for better user experience:
- **Server-Sent Events** - HTTP streaming
- **WebSocket** - Bidirectional real-time communication
- **Chunked Processing** - Progressive response building

### 4. Security Features

- **Input Validation** - Comprehensive request validation
- **Content Sanitization** - Clean user inputs
- **Code Security Checks** - Basic security pattern detection
- **CORS Configuration** - Secure cross-origin requests

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking (optional)
mypy app/
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | Required |
| `DEBUG` | Debug mode | `False` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `ALLOWED_ORIGINS` | CORS origins | `["http://localhost:3000"]` |
| `MAX_CONVERSATION_HISTORY` | Memory limit | `50` |

## Deployment

### Using Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

### Using Render/Railway/Heroku

1. Set environment variables in your platform
2. Use `python -m app.main` as the start command
3. Ensure `PORT` environment variable is set correctly

## Troubleshooting

### Common Issues

1. **Gemini API Key Invalid**
   - Verify your API key is correct
   - Check API key has proper permissions

2. **CORS Errors**
   - Add your frontend URL to `ALLOWED_ORIGINS`
   - Ensure proper HTTP methods are allowed

3. **Memory Issues**
   - Adjust `MAX_CONVERSATION_HISTORY` setting
   - Clear old sessions periodically

4. **Streaming Not Working**
   - Check client supports Server-Sent Events
   - Verify WebSocket connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.