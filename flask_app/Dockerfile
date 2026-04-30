FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-k", "sync", "-b", "0.0.0.0:5001", "app:app"]
