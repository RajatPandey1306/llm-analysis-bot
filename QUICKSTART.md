# Quick Start Guide

## Installation Steps

### 1. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
```bash
playwright install chromium
```

### 4. Configure Environment
```bash
# Copy the example file
copy .env.example .env

# Edit .env with your details:
# - MY_EMAIL: Your email address
# - MY_SECRET: Your secret string
# - OPENAI_API_KEY: Your OpenAI API key
```

### 5. Run the Server
```bash
python main.py
```

Server will start on `http://localhost:8000`

### 6. Test Locally
```bash
# In another terminal, edit test_endpoint.py with your email/secret
python test_endpoint.py
```

### 7. Expose with ngrok
```bash
# In another terminal
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app/quiz`) for Google Form submission.

## Troubleshooting

**"playwright not found"**
```bash
playwright install chromium
```

**"OpenAI API error"**
- Check your OPENAI_API_KEY in .env
- Verify you have API credits

**"Module not found"**
```bash
pip install -r requirements.txt
```

## Next Steps

1. ✅ Test with demo endpoint
2. ✅ Submit Google Form with your ngrok URL
3. ✅ Wait for quiz evaluation on Nov 29, 2025
4. ✅ Prepare for viva using VIVA_PREP.md

Good luck! 🚀
