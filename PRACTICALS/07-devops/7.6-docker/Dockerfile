# SPEC — Dockerfile for shop.py
# 1. Start from base image with Python 3.12
# 2. Set working directory
# 3. Copy app files
# 4. Install dependencies (none for us)
# 5. Run shop.py when container starts

FROM python:3.12
WORKDIR /app
COPY shop.py .
CMD ["python", "shop.py"]
