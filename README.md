# eCFR Analyzer

A web application for analyzing and visualizing federal regulations data from the Electronic Code of Federal Regulations (eCFR).

## Features

- View and analyze federal regulations by agency
- Sort by word count, number of regulations, or agency name
- Search functionality
- Modern, responsive UI
- RESTful API backend

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Uvicorn (ASGI server)

### Frontend
- React
- TypeScript
- Tailwind CSS
- Vite

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js (for local development)
- Python 3.10+ (for local development)

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ecfr-analyzer.git
   cd ecfr-analyzer
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. For local frontend development:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Project Structure

```
ecfr-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   └── ...
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── ...
│   ├── package.json
│   └── ...
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 