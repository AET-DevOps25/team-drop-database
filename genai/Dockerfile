FROM python:3.11-slim


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


RUN apt-get update && apt-get install -y \
    build-essential curl git \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install .


COPY travel_buddy_ai ./travel_buddy_ai
COPY import_attractions.py ./
COPY test_qa_fixed.py ./


EXPOSE 8000


CMD ["uvicorn", "travel_buddy_ai.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
