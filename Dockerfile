# Use official Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY agent.py .
COPY main.py .
COPY tools/ tools/
# Note: .env is not copied - use HuggingFace Space secrets instead

# Sync dependencies
RUN uv sync

# Install Playwright browsers
RUN uv run playwright install chromium
RUN uv run playwright install-deps

# Expose port 7860 (HuggingFace Spaces default)
EXPOSE 7860

# Run the application
CMD ["uv", "run", "python", "main.py"]
