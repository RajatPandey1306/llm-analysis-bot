# LLM Quiz Solver - LangGraph Implementation

An intelligent, autonomous agent built with **LangGraph** and **Groq (Llama 4 Maverick)** that solves data-related quizzes involving web scraping, data processing, analysis, and visualization tasks.

## 🔍 Overview

This project autonomously solves multi-step quiz tasks involving:
- **Data sourcing**: Scraping websites, calling APIs, downloading files
- **Data preparation**: Cleaning text, PDFs, and various data formats
- **Data analysis**: Filtering, aggregating, statistical analysis
- **Data visualization**: Generating charts, narratives

## 🏗️ Architecture

The project uses a **LangGraph state machine** architecture:

```
┌─────────────┐
│   FastAPI   │  ← Receives POST requests at /solve
│   Server    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ LangGraph   │  ← Agent with Llama 4 Maverick
│   Agent     │
└──────┬──────┘
       │
       ├────────────┬────────────┬─────────────┬──────────────┐
       ▼            ▼            ▼             ▼              ▼
 [Scraper]    [Downloader]  [Code Exec]  [POST Req] [Add Deps]
```

## ✨ Features

- ✅ Autonomous multi-step problem solving
- ✅ Dynamic JavaScript rendering via Playwright
- ✅ Code generation & execution
- ✅ Self-installing dependencies via `uv`
- ✅ Robust error handling with retries
- ✅ Docker containerization ready
- ✅ Rate limiting (30 requests/min for Llama 4 Maverick)

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- `uv` package manager

### Step 1: Install uv
```bash
pip install uv
```

### Step 2: Clone and Setup
```bash
git clone <https://github.com/RajatPandey1306/llm-analysis-bot>
cd llm-quiz-solver

# Sync dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

### Step 3: Configure Environment
Create a `.env` file:
```bash
MY_EMAIL=your.email@example.com
MY_SECRET=your_secret_string
GROQ_API_KEY=your_groq_api_key
```

Get a Groq API key from [Groq Console](https://console.groq.com/keys).

## 🚀 Usage

### Local Development
```bash
uv run python main.py
```

Server starts at `http://0.0.0.0:7860`

### Test the Endpoint
```bash
curl -X POST http://localhost:7860/solve \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret_string",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected response:
```json
{
  "status": "ok"
}
```

## 🌐 API Endpoints

### POST /solve
Receives quiz tasks and triggers the autonomous agent.

**Request:**
```json
{
  "email": "your.email@example.com",
  "secret": "your_secret_string",
  "url": "https://example.com/quiz-123"
}
```

**Responses:**
- `200`: Secret verified, agent started
- `400`: Invalid JSON payload
- `403`: Invalid secret

### GET /healthz
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "uptime_seconds": 3600
}
```

## 🛠️ Tools & Capabilities

1. **Web Scraper** (`get_rendered_html`): Renders JavaScript-heavy pages
2. **File Downloader** (`download_file`): Downloads PDFs, CSVs, images
3. **Code Executor** (`run_code`): Executes Python code via `uv run`
4. **POST Request** (`post_request`): Sends JSON payloads to endpoints
5. **Dependency Installer** (`add_dependencies`): Dynamically installs packages

## 🐳 Docker Deployment

### Build
```bash
docker build -t llm-quiz-solver .
```

### Run
```bash
docker run -p 7860:7860 \\
  -e MY_EMAIL="your.email@example.com" \\
  -e MY_SECRET="your_secret" \\
  -e GROQ_API_KEY="your_api_key" \\
  llm-quiz-solver
```

### Deploy to Hugging Face Spaces

1. Create a new Space with **Docker SDK**
2. Push this repository to your Space
3. Add secrets in Space settings:
   - `MY_EMAIL`
   - `MY_SECRET`
   - `GROQ_API_KEY`

Your endpoint will be: `https://<username>-<space>.hf.space/solve`

## 📝 Requirements

- **API Endpoint**: POST to `/solve` with email/secret/url
- **Secret Verification**: Returns 403 for invalid secrets
- **Time Limit**: Solves each quiz within 3 minutes
- **Quiz Chaining**: Follows quiz chains until completion
- **Response Format**: JSON with appropriate status codes

## 📄 License

MIT License

---

**Author**: Your Name
**Course**: Tools in Data Science (TDS)
**Institution**: IIT Madras
