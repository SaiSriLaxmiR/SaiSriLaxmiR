FROM python:3.12-slim

WORKDIR /app

COPY worker/requirements.txt ./worker-requirements.txt
COPY benchmark/requirements.txt ./benchmark-requirements.txt

RUN pip install --no-cache-dir \
    -r worker-requirements.txt \
    -r benchmark-requirements.txt

COPY benchmark ./benchmark
COPY worker ./worker

CMD ["python", "-m", "worker.main"]
