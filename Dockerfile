# Base Image
FROM python:3.9-slim

# Working directory set karein
WORKDIR /app

# Dependencies copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pura project code copy karein
COPY . .

# Hugging Face Spaces ka default port
EXPOSE 7860

# Gunicorn se app run karein (timeout 120s diya hai taaki OpenAI slow ho toh timeout na ho)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]