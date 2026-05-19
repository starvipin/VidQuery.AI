# Base Python Image
FROM python:3.11-slim

# Install `uv` directly from Astral's official image (Super fast)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Working directory set karein
WORKDIR /app

# Pehle sirf dependency files copy karein (Docker caching ke liye)
COPY pyproject.toml uv.lock ./

# Dependencies install karein (`--frozen` ensure karta hai ki lock file change na ho)
RUN uv sync --frozen --no-cache

# Ab baaki ka poora code copy karein
COPY . .

# Hugging Face Spaces ka default port
EXPOSE 7860

# `uv run` ka use karke gunicorn start karein
CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]