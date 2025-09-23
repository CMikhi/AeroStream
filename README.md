# IgniteDemoRepo

IgniteDemoRepo is a terminal-based messaging application built for the **Ignite Professional Studies Technology** program. It provides a modern TUI (Text User Interface) experience for messaging, leveraging robust Python frameworks for both the frontend and backend.

## Features

- **Terminal-Based TUI**: Built with [Textualize](https://github.com/Textualize/textual), offering an interactive, responsive, and visually appealing messaging interface directly in your terminal.
- **FastAPI Backend**: Handles all messaging logic and user management, providing fast and reliable REST and WebSocket endpoints.
- **Real-Time Messaging**: Communication between the TUI and backend is powered by both REST APIs for data retrieval and WebSockets for instant, two-way message delivery.
- **User Authentication**: Uses `bcrypt` to hash passwords at rest and compare incoming password requests against hash. Furthermore, we use JWT tokens for role-based authentication and endpoint security. 
- **Message History**: Upon joining a room, the backend will autopopulate the client with past messages for a specific room
- **Cross-Platform**: Works on zsh, bash, Windows, and any UNIX-based systems

## Technologies Used

- **[Textualize (Textual)](https://github.com/Textualize/textual)** — Python framework for building rich TUI applications.
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance backend framework for APIs and WebSockets.
- **WebSockets** — For real-time, bidirectional communication.
- **REST API** — For resource fetching and data manipulation.

## Project Structure

```
IgniteDemoRepo/
├── backend/                 # FastAPI backend services
│   ├── __init__.py         # Package initialization
│   ├── backend.py          # Main FastAPI application
│   ├── dbManager.py        # Database management utilities
│   ├── messageService.py   # Message handling logic
│   ├── roomService.py      # Room management logic
│   ├── ws_manager.py       # WebSocket connection management
│   ├── validation.py       # Input validation utilities
│   ├── script.py           # JWT debugging utility
│   └── fastapi_test_client.py  # API testing client
├── CLI/                    # Terminal User Interface
│   ├── cli.py             # Main TUI application
│   └── cli.css            # TUI styling
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CMikhi/IgniteDemoRepo.git
   cd IgniteDemoRepo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the FastAPI backend:**
   ```bash
   .venv/bin/uvicorn backend.backend:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start the TUI frontend:**
   ```bash
   python CLI/cli.py
   ```

## Development

### Running Tests

The project includes a test client for API validation:

```bash
# Start the backend server first, then:
python backend/fastapi_test_client.py
```

### Environment Variables

For production deployment, set the following environment variables:

- `SECRET_KEY`: JWT signing secret (required in production)
- `ENVIRONMENT`: Set to "production" for production deployment

### API Documentation

Once the backend is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## Usage

- Launch the backend server, then open the TUI client in your terminal.
- Log in or register
- Create a new room or join a new one
- Start messaging in real-time with other users.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Ignite Professional Studies](https://www.bentonvillek12.org/o/ignite)
- [Textualize](https://github.com/Textualize/textual)
- [FastAPI](https://fastapi.tiangolo.com/)

---

_For questions or support, open an issue on GitHub._