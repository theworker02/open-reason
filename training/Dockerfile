# CPU-only Open Reason trainer. Do not request a GPU.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPEN_REASON_IN_DOCKER=1 \
    OPEN_REASON_DISABLE_CUDA=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY training ./training

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install --no-cache-dir transformers tokenizers huggingface_hub pyyaml

# data/release is mounted at runtime; checkpoints write to training/work
CMD ["python", "-m", "open_reason.training.docker_entry"]
