FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y jq && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV PORT=8000

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port $PORT"
