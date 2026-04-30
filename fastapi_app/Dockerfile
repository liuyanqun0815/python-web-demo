FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8001

CMD ["gunicorn", "-w", "4", "--threads", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8001", "main:app"]
