# FastAPI Environment Setup Commands

Based on the CLAUDE.md file, here are the commands to set up and run the FastAPI environment:

## 1. Create Virtual Environment

Using `uv` (recommended):
```bash
uv venv
```

Or using Python's built-in venv:
```bash
python -m venv .venv
```

## 2. Activate Virtual Environment

On macOS/Linux:
```bash
source .venv/bin/activate
```

On Windows (if applicable):
```bash
.venv\Scripts\activate
```

## 3. Install Dependencies

Using `uv`:
```bash
uv pip install -r requirements.txt
```

Or using pip:
```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Copy the example environment file and update with your credentials:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials for:
- Supabase URL and API key
- Redis URL
- Vendor API key (sports data provider)
- bKash billing credentials

## 5. Run the Development Server

```bash
uvicorn app.main:app --reload --port 8001
```

## 6. Access the Application

Once the server is running:

- **API**: http://localhost:8001/
- **API Docs (Swagger UI)**: http://localhost:8001/docs
- **OpenAPI JSON**: http://localhost:8001/openapi.json
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## 7. Generate OpenAPI Contract

When API changes are made, regenerate the contract:
```bash
make contract
```

Or manually:
```bash
python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > contracts/openapi.json
```

## Project Structure

```
/app
  /api        routers (auth, matches, predictions, chat, billing, users)
  /core       config, security (JWT verify), deps
  /models     pydantic + db models
  /services   prediction, rag, ingestion, billing, rewards
  /ml         model artifacts + inference
  /rag        index build + retrieval

/contracts
  CONTRACT_VERSION
  openapi.json (generated)

API_CHANGELOG.md
CLAUDE.md
```

## Quick Start Summary

```bash
# 1. Create and activate venv
uv venv && source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run server
uvicorn app.main:app --reload --port 8001

# Server will be available at http://localhost:8001
```
