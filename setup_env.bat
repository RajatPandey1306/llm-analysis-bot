@echo off
echo Setting up .env file with AI Pipe credentials...
echo.

REM Check if .env exists
if exist .env (
    echo Found existing .env file
    echo.
    echo Current contents:
    type .env
    echo.
    echo =====================================
    echo.
) else (
    echo Creating new .env file
)

REM Add the required environment variables
echo Adding AI Pipe configuration...
echo.

(
echo MY_EMAIL=21f3001699@ds.study.iitm.ac.in
echo MY_SECRET=Cb350_RS
echo AI_PIPE_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDE2OTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.SPdpYufGtU-Oam4AUZITz8RGVbYAuSWSPW2ktvCCFdg
echo AI_PIPE_BASE_URL=https://aipipe.org/openrouter/v1
echo PORT=8000
) > .env

echo.
echo =====================================
echo ✓ .env file has been created/updated!
echo =====================================
echo.
echo New .env contents:
type .env
echo.
echo =====================================
echo.
echo IMPORTANT: Now restart your server with:
echo python main.py
echo.
pause
