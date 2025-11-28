# Deploying to Hugging Face Spaces

This project is ready to be deployed to Hugging Face Spaces using Docker.

## Prerequisites

1.  A Hugging Face account.
2.  `GROQ_API_KEY`, `MY_EMAIL`, and `MY_SECRET` ready.

## Steps

1.  **Create a New Space**:
    *   Go to [Hugging Face Spaces](https://huggingface.co/spaces).
    *   Click **Create new Space**.
    *   Enter a name (e.g., `llm-quiz-solver`).
    *   Select **Docker** as the Space SDK.
    *   Choose **Blank** template.
    *   Click **Create Space**.

2.  **Upload Files**:
    *   You can upload files directly via the web interface or use git.
    *   Upload the following files to your Space's repository:
        *   `Dockerfile`
        *   `requirements.txt`
        *   `main.py`
        *   `agent.py`
        *   `solver.py`
        *   `browser.py`
        *   `submitter.py`
        *   `README.md` (optional but recommended)

3.  **Configure Secrets**:
    *   Go to the **Settings** tab of your Space.
    *   Scroll down to **Variables and secrets**.
    *   Add the following **Secrets** (NOT variables, for security):
        *   `GROQ_API_KEY`: Your Groq API Key.
        *   `MY_EMAIL`: Your email address.
        *   `MY_SECRET`: Your secret string.

4.  **Build and Run**:
    *   Hugging Face will automatically build the Docker image and start the container.
    *   Watch the **Logs** tab for any errors.
    *   Once the status is **Running**, your API endpoint will be available.

## API Endpoint

Your API endpoint will be:
`https://<your-username>-<space-name>.hf.space/quiz`

Example:
`https://johndoe-llm-quiz-solver.hf.space/quiz`

## Testing

You can test your deployed endpoint using curl:

```bash
curl -X POST https://<your-username>-<space-name>.hf.space/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```
