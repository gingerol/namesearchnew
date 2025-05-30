# Namesearch.io

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered brand and domain name intelligence platform for founders, brand strategists, and creative agencies.

## 🚀 Features

- **Domain Intelligence**: Real-time WHOIS lookups, TLD availability, and domain suggestions
- **Brand Analysis**: Linguistic safety, trademark screening, and cultural resonance
- **AI-Powered Naming**: Generate and evaluate brand names using advanced NLP
- **Market Intelligence**: SEO simulation, trend forecasting, and competitive analysis
- **Collaboration Tools**: Team workspaces, watchlists, and project management

## 🏗️ Project Structure

```
.
├── .github/                    # GitHub workflows and templates
├── backend/                    # FastAPI backend application
├── frontend/                   # React.js frontend application
├── docs/                       # Project documentation
│   ├── implementation-plan/    # Detailed implementation plans
│   └── scratchpad.md           # Development notes and learnings
├── docker/                     # Docker configuration files
├── scripts/                    # Utility scripts
├── .env.example                # Environment variables template
├── docker-compose.yml          # Development environment
├── pyproject.toml              # Python project configuration
└── README.md                   # This file
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/namesearch.io.git
   cd namesearch.io
   ```

2. Set up the development environment:
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   
   # Start services
   docker-compose up -d
   
   # Install backend dependencies
   cd backend
   poetry install
   
   # Install frontend dependencies
   cd ../frontend
   npm install
   ```

3. Run the development servers:
   ```bash
   # Start backend
   cd backend
   uvicorn app.main:app --reload
   
   # In a new terminal, start frontend
   cd frontend
   npm run dev
   ```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

For questions or feedback, please open an issue or contact [your-email@example.com](mailto:your-email@example.com).
