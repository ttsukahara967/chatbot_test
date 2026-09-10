FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# GPU variant: install the standard PyPI build of PyTorch, which bundles CUDA
# support (unlike the CPU-only build from download.pytorch.org/whl/cpu used
# on machines without an NVIDIA GPU). This requires the host to have an
# NVIDIA driver and the NVIDIA Container Toolkit installed; torch.cuda still
# works fine without a GPU present (falls back to CPU), it's just a larger image.
RUN pip install --no-cache-dir torch

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
