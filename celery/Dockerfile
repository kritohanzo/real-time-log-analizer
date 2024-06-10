FROM python:3.11-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install pip --upgrade
RUN pip install -r requirements.txt --no-cache-dir
COPY ./web/ .
CMD ["celery", "--app", "main", "worker", "--pool=prefork", "--concurrency=2", "--loglevel=info"]