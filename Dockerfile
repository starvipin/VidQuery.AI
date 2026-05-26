# Base Python Image
FROM python:3.11-slim

# Install `uv` directly from Astral's official image (Super fast)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- HUGGING FACE SECURITY FIX ---
# Create a new non-root user with ID 1000
RUN useradd -m -u 1000 user

# Switch to this new user
USER user

# Set home directory and path environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Working directory set karein (user ki home directory ke andar)
WORKDIR $HOME/app

# --- OWNERSHIP FIX ---
# Pehle sirf dependency files copy karein, aur ownership 'user' ko dein
COPY --chown=user pyproject.toml uv.lock ./

# Dependencies install karein
# Ab kyunki 'USER user' set hai, `uv` correct permissions ke sath .venv banayega
RUN uv sync --frozen --no-cache --no-install-project

# Ab baaki ka poora code copy karein with correct ownership
COPY --chown=user . $HOME/app

# Hugging Face Spaces ka default port
EXPOSE 7860

# `uv run` ka use karke gunicorn start karein
CMD ["uv", "run", "--no-sync", "gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
