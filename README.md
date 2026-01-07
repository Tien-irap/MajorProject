# Chess Analysis Platform

A comprehensive chess analysis platform that leverages Stockfish engine, machine learning, and AI to analyze chess games, identify player weaknesses, generate targeted puzzles, and provide personalized improvement recommendations.

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Design Decisions](#design-decisions)
- [Troubleshooting](#troubleshooting)
- [Dockerization](#dockerization)

## 🎯 About the Project

This Chess Analysis Platform is an advanced system designed to help chess players improve their game by:

- **Analyzing PGN files** to identify mistakes and blunders
- **Creating weakness profiles** based on player performance patterns
- **Generating personalized puzzles** using genetic algorithms
- **Providing AI-powered insights** using LLM analysis
- **Comparing player performance** against master-level games
- **Clustering mistakes** to identify common error patterns

The platform combines traditional chess engine analysis (Stockfish) with modern machine learning techniques and AI to provide deep insights into player performance.

## 🔍 Project Overview

### Key Features

1. **Game Analysis**
   - Deep analysis of chess games from PGN files
   - Move-by-move evaluation using Stockfish engine
   - Classification of moves (Book, Best, Good, Inaccuracy, Mistake, Blunder)
   - Win probability calculations

2. **Weakness Detection**
   - Global mistake dataset creation from multiple games
   - K-means clustering of mistakes based on features
   - Pattern recognition in player errors
   - ELO-aware analysis

3. **Puzzle Generation**
   - Genetic algorithm-based puzzle creation
   - Personalized puzzles targeting specific weaknesses
   - Difficulty scaling based on player skill level
   - Quality evaluation of generated positions

4. **AI-Powered Insights**
   - LLM integration for natural language analysis
   - Strategic recommendations
   - Pattern explanation and learning suggestions

5. **Master Comparison**
   - Compare player games against master-level performances
   - Identify deviations from optimal play
   - Learn from elite player decision-making

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Vite)   │
│  Port: 5173     │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────────────────────────────────────┐
│            Backend (FastAPI)                    │
│              Port: 8000                         │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │         API Routes Layer                 │  │
│  │  - Analysis Routes                       │  │
│  │  - Puzzle Generation Routes              │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                               │
│  ┌──────────────▼───────────────────────────┐  │
│  │         Services Layer                   │  │
│  │  - PGN Analysis                          │  │
│  │  - Global Data Processing                │  │
│  │  - Weakness Analysis                     │  │
│  │  - Puzzle Generator (Genetic Algorithm)  │  │
│  │  - LLM Analyzer                          │  │
│  │  - Master Comparison                     │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                               │
│  ┌──────────────▼───────────────────────────┐  │
│  │      Core Components                     │  │
│  │  - Database (MongoDB via Motor)          │  │
│  │  - Celery Task Queue                     │  │
│  │  - Configuration                         │  │
│  │  - Logger                                │  │
│  └──────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────┐
│   MongoDB      │  │   Redis     │
│   Port: 27017  │  │  Port: 6379 │
└────────────────┘  └─────────────┘
        │
┌───────▼────────┐
│ Celery Worker  │
│ (Background    │
│  Tasks)        │
└────────────────┘

External:
┌────────────────┐
│  Stockfish     │
│  Engine        │
└────────────────┘
```

### Data Flow

1. **Game Upload** → Frontend sends PGN file to Backend
2. **Analysis Pipeline** → Backend processes game with Stockfish
3. **Feature Extraction** → Moves analyzed and features extracted
4. **Storage** → Results stored in MongoDB
5. **Clustering** → Mistakes grouped using ML algorithms
6. **Insight Generation** → AI generates recommendations
7. **Response** → Results sent back to Frontend

## 📁 Project Structure

```
Major_project/
├── backend/                          # Backend application
│   └── app/
│       ├── main.py                   # FastAPI application entry point
│       ├── api/                      # API versioning
│       ├── core/                     # Core components
│       │   ├── config.py            # Configuration management
│       │   ├── database.py          # MongoDB connection
│       │   ├── celery_app.py        # Celery configuration
│       │   └── logger.py            # Logging setup
│       ├── models/                   # Pydantic models & schemas
│       ├── repos/                    # Database repositories
│       ├── routes/                   # API route handlers
│       │   ├── analysis_routes.py   # Game analysis endpoints
│       │   └── GenPuzzle.py         # Puzzle generation endpoints
│       ├── services/                 # Business logic
│       │   ├── analyze_pgn.py       # PGN file analysis
│       │   ├── global_data.py       # Global dataset creation
│       │   ├── global_analyzer.py   # Clustering & pattern detection
│       │   ├── weakness_analysis.py # Player weakness identification
│       │   ├── puzzle_generator.py  # Genetic algorithm puzzles
│       │   ├── GeneticAlgo.py       # GA implementation
│       │   ├── llm_analyzer.py      # AI insights generation
│       │   └── master_comparison.py # Master game comparison
│       └── tasks/                    # Celery background tasks
│
├── frontend/                         # Frontend application
│   ├── src/
│   │   ├── App.tsx                  # Main application component
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Page components
│   │   ├── hooks/                   # Custom React hooks
│   │   └── lib/                     # Utility functions
│   ├── public/                      # Static assets
│   └── package.json                 # Frontend dependencies
│
├── stockfish/                        # Stockfish chess engine
│   └── stockfish-macos-m1-apple-silicon
│
├── data/                            # PGN game files
│   ├── Horwitz.pgn
│   ├── Li.pgn
│   └── MacKenzie.pgn
│
├── output/                          # Generated datasets
│   └── global_mistake_features.csv
│
├── logs/                            # Application logs
│
├── docker-compose.yml               # Docker orchestration
├── Dockerfile.backend               # Backend container definition
├── Dockerfile.frontend              # Frontend container definition
├── backend_requirements.txt         # Python dependencies
└── frontend_requirements.txt        # Additional requirements
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.115.0+
- **Web Server**: Uvicorn with standard extras
- **Task Queue**: Celery 5.4.0+
- **Cache/Broker**: Redis 5.2.0+
- **Database**: MongoDB 7 (Motor 3.6.0+ for async operations)
- **Chess Engine**: Stockfish 3.28.0+, python-chess 1.11.1+
- **ML/Data Science**:
  - pandas 2.2.0+
  - numpy 2.0.0+
  - scikit-learn 1.6.0+
- **Image Processing**: CairoSVG 2.7.1+, Pillow 11.0.0+
- **Utilities**:
  - python-dotenv (environment management)
  - pydantic 2.10.0+ (data validation)
  - requests 2.32.0+

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI components
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Chess Integration**: chess.js 1.4.0+
- **Icons**: Lucide React
- **Utilities**:
  - class-variance-authority
  - clsx
  - date-fns

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: MongoDB 7
- **Cache**: Redis 7 (Alpine)
- **Reverse Proxy**: (Optional) Nginx

### External Services
- **Chess Engine**: Stockfish (Native binary)
- **AI/LLM**: Mistral API (for insights generation)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (with Bun or npm)
- Docker & Docker Compose (for containerized setup)
- MongoDB 7+ (if running locally)
- Redis 7+ (if running locally)

### Option 1: Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd Major_project
```

#### 2. Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv env
source env/bin/activate  # On macOS/Linux
# or
.\env\Scripts\activate  # On Windows

# Install dependencies
pip install -r backend_requirements.txt
```

#### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example (if exists) or create new
cp env.example .env  # If env.example exists
# or create .env manually with the following:

# Database
MONGO_URL=mongodb://localhost:27017/
DB_NAME=chess_analysis_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Stockfish
STOCKFISH_PATH=./stockfish/stockfish-macos-m1-apple-silicon
# For Linux: STOCKFISH_PATH=/usr/games/stockfish
# For Windows: STOCKFISH_PATH=./stockfish/stockfish.exe

# Global Dataset
GLOBAL_MISTAKES_CSV=./output/global_mistake_features.csv

# API Keys
MISTRAL_API_KEY=your_mistral_api_key_here

# Logging Level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR)
LOGGER=20
```

#### 4. Generate Global Mistakes Dataset

**This is a critical step** before running the application:

```bash
# Ensure virtual environment is activated
source env/bin/activate

# Run the global data processor
python -m backend.app.services.global_data

# This will:
# - Analyze games from data/MacKenzie.pgn (or your specified PGN)
# - Extract mistake features
# - Save results to output/global_mistake_features.csv
```

**Note**: This process can take time depending on the number of games. The default is set to 100 games for testing. Modify `max_games` parameter in [global_data.py](backend/app/services/global_data.py#L93) for more or fewer games.

#### 5. Start Services

**Start MongoDB** (if not using Docker):
```bash
mongod --dbpath=/path/to/your/data
```

**Start Redis** (if not using Docker):
```bash
redis-server
```

**Start Backend**:
```bash
# From project root
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Celery Worker** (in a new terminal):
```bash
source env/bin/activate
celery -A backend.app.core.celery_app.celery_app worker --loglevel=info
```

#### 6. Frontend Setup

```bash
cd frontend

# Install dependencies (using Bun)
bun install
# or with npm
npm install

# Start development server
bun run dev
# or
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Docker Setup (Recommended for Production)

#### 1. Environment Setup

Create a `.env` file as described above (Docker Compose will use it).

#### 2. Generate Global Dataset (One-time)

```bash
# Create virtual environment and install dependencies first
python3 -m venv env
source env/bin/activate
pip install -r backend_requirements.txt

# Run global data generation
python -m backend.app.services.global_data
```

#### 3. Build and Start All Services

```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

This will start:
- MongoDB (port 27017)
- Redis (port 6379)
- Backend API (port 8000)
- Celery Worker
- Frontend (port 5173)

#### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

#### 5. Stop Services

```bash
docker-compose down

# To also remove volumes (database data)
docker-compose down -v
```

## 💡 Design Decisions

### 1. Microservices Architecture
- **Decision**: Separated backend, frontend, workers, and databases into distinct services
- **Rationale**: Improved scalability, easier maintenance, independent deployment
- **Trade-off**: Increased complexity in local development

### 2. Asynchronous Processing with Celery
- **Decision**: Long-running tasks (game analysis, puzzle generation) run in background workers
- **Rationale**: Prevents API timeouts, improves user experience with non-blocking operations
- **Implementation**: Redis as message broker, separate worker containers

### 3. MongoDB for Data Storage
- **Decision**: NoSQL database (MongoDB) instead of relational database
- **Rationale**: 
  - Flexible schema for chess game data
  - Better performance for document-based queries
  - Natural fit for JSON-like game analysis results
- **Trade-off**: Less rigid data consistency guarantees

### 4. Genetic Algorithm for Puzzle Generation
- **Decision**: Custom genetic algorithm implementation for puzzle creation
- **Rationale**: 
  - Generates unique, personalized puzzles
  - Targets specific player weaknesses
  - More engaging than static puzzle databases
- **Implementation**: See [GeneticAlgo.py](backend/app/services/GeneticAlgo.py) and [puzzle_generator.py](backend/app/services/puzzle_generator.py)

### 5. Feature Engineering for Weakness Detection
- **Decision**: Extract specific features from mistakes (eval_before, eval_diff, piece_count, move_num, player_elo)
- **Rationale**: 
  - Enables ML-based clustering
  - Identifies patterns in player errors
  - Provides actionable insights
- **Implementation**: See [global_data.py](backend/app/services/global_data.py)

### 6. K-means Clustering for Pattern Recognition
- **Decision**: Use K-means clustering to group similar mistakes
- **Rationale**:
  - Unsupervised learning discovers hidden patterns
  - Groups mistakes by contextual similarity
  - Helps identify weakness categories
- **Implementation**: See [global_analyzer.py](backend/app/services/global_analyzer.py)

### 7. LLM Integration for Insights
- **Decision**: Integrate Mistral AI for natural language explanations
- **Rationale**: 
  - Provides human-readable strategic insights
  - Explains complex patterns in accessible language
  - Enhances user understanding and learning

### 8. Stockfish for Position Evaluation
- **Decision**: Use Stockfish as the primary evaluation engine
- **Rationale**: 
  - Industry-standard, strongest open-source engine
  - Provides accurate position evaluations
  - Well-documented and actively maintained

### 9. TypeScript for Frontend
- **Decision**: Use TypeScript instead of JavaScript
- **Rationale**: 
  - Type safety reduces runtime errors
  - Better IDE support and autocomplete
  - Easier refactoring and maintenance

### 10. Docker for Deployment
- **Decision**: Containerize all services with Docker
- **Rationale**: 
  - Consistent environment across development and production
  - Simplified deployment process
  - Easy scaling and orchestration

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Stockfish Not Found

**Error**: `Stockfish engine not found at path: ...`

**Solution**:
```bash
# Verify Stockfish path in .env matches your system
# For macOS M1/M2:
STOCKFISH_PATH=./stockfish/stockfish-macos-m1-apple-silicon

# Make it executable
chmod +x ./stockfish/stockfish-macos-m1-apple-silicon

# Test it
./stockfish/stockfish-macos-m1-apple-silicon
# Should open Stockfish UCI interface
```

#### 2. MongoDB Connection Failed

**Error**: `ConnectionFailure` or `ServerSelectionTimeoutError`

**Solution**:
```bash
# Check if MongoDB is running
# For Docker:
docker ps | grep mongo

# For local installation:
# macOS:
brew services list | grep mongodb

# Linux:
systemctl status mongod

# Start MongoDB if not running
docker-compose up -d mongodb  # For Docker
brew services start mongodb-community  # For macOS
sudo systemctl start mongod  # For Linux
```

#### 3. Redis Connection Issues

**Error**: `Error 61 connecting to localhost:6379. Connection refused.`

**Solution**:
```bash
# Check Redis status
docker ps | grep redis  # For Docker
redis-cli ping  # Should return PONG

# Start Redis
docker-compose up -d redis  # For Docker
redis-server  # For local installation
```

#### 4. Global Mistakes CSV Missing

**Error**: `FileNotFoundError: global_mistake_features.csv not found`

**Solution**:
```bash
# Run the global data generation script
source env/bin/activate
python -m backend.app.services.global_data

# Verify the file was created
ls -lh output/global_mistake_features.csv
```

#### 5. Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
```bash
# Ensure you're in the project root directory
pwd  # Should show .../Major_project

# Ensure virtual environment is activated
source env/bin/activate

# Verify PYTHONPATH (if needed)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip install -r backend_requirements.txt
```

#### 6. Port Already in Use

**Error**: `Address already in use` for port 8000, 5173, etc.

**Solution**:
```bash
# Find process using the port (replace 8000 with your port)
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different ports in .env or docker-compose.yml
```

#### 7. Docker Build Failures

**Error**: Build fails during `docker-compose up --build`

**Solution**:
```bash
# Clean up old containers and images
docker-compose down
docker system prune -a

# Rebuild with no cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs backend
docker-compose logs frontend
```

#### 8. Celery Worker Not Processing Tasks

**Error**: Tasks stay in pending state

**Solution**:
```bash
# Check Celery worker logs
docker-compose logs celery_worker  # Docker
# or check terminal where worker is running

# Verify Redis connection
redis-cli ping

# Restart worker
docker-compose restart celery_worker  # Docker
# or restart the terminal process
```

#### 9. Frontend API Connection Issues

**Error**: `Network Error` or `CORS` errors in browser console

**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check CORS configuration in backend/app/main.py
# Ensure frontend URL is in allowed origins

# Check environment variables in frontend
# Verify API_URL or VITE_API_URL is set correctly
```

#### 10. Analysis Takes Too Long

**Issue**: Game analysis or puzzle generation times out

**Solution**:
```bash
# Reduce analysis depth in analyze_pgn.py
# Default Stockfish depth: 15-20, reduce to 10-12 for faster results

# Reduce number of games processed
# In global_data.py, set max_games to lower value

# Use background tasks instead of synchronous processing
# Ensure Celery worker is running
```

### Getting Help

If issues persist:

1. **Check Logs**:
   ```bash
   # Docker logs
   docker-compose logs -f backend
   docker-compose logs -f celery_worker
   
   # Local logs
   tail -f logs/app.log
   ```

2. **Enable Debug Logging**:
   ```bash
   # In .env
   LOGGER=10  # DEBUG level
   ```

3. **Verify Dependencies**:
   ```bash
   # Backend
   pip list
   
   # Frontend
   bun list  # or npm list
   ```

4. **Check System Resources**:
   - Ensure sufficient RAM (Stockfish analysis is memory-intensive)
   - Check disk space for MongoDB and logs
   - Monitor CPU usage during analysis

## 🐳 Dockerization

### Services Architecture

The application uses Docker Compose with 5 services:

- **redis**: Message broker (Port 6379)
- **mongodb**: Database (Port 27017)
- **backend**: FastAPI server (Port 8000)
- **celery_worker**: Background task processor
- **frontend**: React/Vite app (Port 5173)

### Key Docker Commands

```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f [service_name]

# Stop and remove
docker-compose down

# Remove with data volumes
docker-compose down -v

# Restart specific service
docker-compose restart backend
```

### Production Notes

- Use environment secrets management (never commit `.env`)
- Add health checks for all services
- Configure resource limits in `docker-compose.yml`
- Consider nginx reverse proxy for SSL/load balancing
- Use specific image tags instead of `latest`

---

## 📝 License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software for personal or commercial purposes with attribution.

```
MIT License

Copyright (c) 2026 Pari, Shifa, Shreya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🤝 Contributing

We welcome contributions to the Chess Analysis Platform! Here's how you can help:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Tien-irap/MajorProject.git
   cd MajorProject
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style and conventions
   - Add tests for new features
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run backend tests
   pytest backend/tests/
   
   # Run frontend tests
   cd frontend && npm test
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a PR on GitHub with a clear description of your changes.

### Areas for Contribution

- 🐛 Bug fixes and issue resolution
- ✨ New features (opening theory analysis, endgame training, etc.)
- 📚 Documentation improvements
- 🧪 Test coverage expansion
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations
- 🌍 Internationalization (i18n)

### Code Standards

- Follow PEP 8 for Python code
- Use ESLint configuration for TypeScript/React
- Write meaningful commit messages
- Add docstrings to functions and classes
- Keep functions small and focused

### Reporting Issues

Found a bug? Have a suggestion? Please open an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

## 📧 Contact

- **Email**: patankarpari@gmail.com
- **GitHub**: [Tien-irap/MajorProject](https://github.com/Tien-irap/MajorProject)
- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/Tien-irap/MajorProject/issues)

---

**Built with ♟️ by Pari, Shifa, Shreya**
