# Phase 1: Project Setup & Configuration

## Overview
Set up the foundational project structure, configuration files, and development environment.

## Goals
- Create project skeleton
- Configure environment and dependencies
- Set up development tooling
- Establish documentation structure

## File Changes

### .gitignore (NEW)
Standard Python gitignore with:
- __pycache__/, *.py[cod], *$py.class
- .env, .venv/, venv/, env/
- *.log
- .pytest_cache/, .coverage
- .vscode/, .idea/
- *.db, *.sqlite
- playwright/.browsers/ (Playwright browser binaries)

### .env.example (NEW)
Create environment variables template:
- OPENALGO_API_KEY: API key for OpenAlgo authentication
- OPENALGO_HOST: OpenAlgo server URL (default: http://127.0.0.1:5000)
- OPENALGO_VERSION: API version (default: v1)
- CORS_ORIGINS: Comma-separated allowed origins for CORS
- LOG_LEVEL: Logging level (default: INFO)
- MAX_WEBSOCKET_CONNECTIONS: Maximum concurrent WebSocket connections (default: 100)
- TICK_BUFFER_SIZE: Size of tick buffer per symbol (default: 1000)
- DEFAULT_TIMEFRAMES: Comma-separated default timeframes (default: 1m,5m,15m,1h,1d)

### requirements.txt (NEW)
List all required Python packages:
- fastapi>=0.109.0
- uvicorn[standard]>=0.27.0
- openalgo>=1.0.3
- ta>=0.11.0
- playwright>=1.40.0
- pandas>=2.1.0
- numpy>=1.26.0
- scipy>=1.11.0
- pydantic>=2.5.0
- pydantic-settings>=2.1.0
- websockets>=12.0
- aiohttp>=3.9.0
- python-multipart>=0.0.6
- orjson>=3.9.0

### README.md (NEW)
Create comprehensive project documentation including:
- Project overview and features
- Installation instructions (clone OpenAlgo reference, install dependencies)
- Required dependencies
- Environment variables setup
- Playwright browser installation command: `playwright install chromium`
- API endpoints documentation with examples
- WebSocket usage examples
- Multi-timeframe support explanation
- Available indicators list from ta library

### Directory Structure (NEW)
Create the following directories:
- app/
- app/core/
- app/schemas/
- app/services/
- app/api/
- app/api/v1/
- app/api/v1/endpoints/
- app/utils/
- tests/
- scripts/
- docs/

### __init__.py Files (NEW)
Create empty __init__.py files in:
- app/__init__.py
- app/core/__init__.py
- app/schemas/__init__.py
- app/services/__init__.py
- app/api/__init__.py
- app/api/v1/__init__.py
- app/api/v1/endpoints/__init__.py
- app/utils/__init__.py
- tests/__init__.py

### scripts/clone_openalgo.sh (NEW)
Create bash script to clone OpenAlgo repository:
- Clone https://github.com/marketcalls/openalgo to a reference directory
- Clone https://github.com/marketcalls/openalgo-python-library for library reference
- Add instructions for setting up OpenAlgo server if needed
- Make script executable
- Add error handling

### scripts/setup.sh (NEW)
Create setup script:
- Create virtual environment
- Install dependencies from requirements.txt
- Install Playwright browsers: playwright install chromium
- Copy .env.example to .env
- Print setup instructions
- Check Python version (require 3.10+)
- Make script executable

### scripts/run_dev.sh (NEW)
Create development run script:
- Activate virtual environment
- Run FastAPI with: fastapi dev app/main.py
- Set reload=True for development
- Set host=0.0.0.0 and port=8000
- Make script executable

### scripts/run_prod.sh (NEW)
Create production run script:
- Activate virtual environment
- Run FastAPI with: fastapi run app/main.py
- Set workers based on CPU count
- Set host and port from environment or defaults
- Add logging configuration
- Make script executable

## Completion Criteria
- [ ] All configuration files created
- [ ] Directory structure established
- [ ] Scripts are executable and tested
- [ ] README provides clear setup instructions
- [ ] Environment template is comprehensive

## Next Phase
Phase 2: Core Infrastructure (Configuration & Logging)
