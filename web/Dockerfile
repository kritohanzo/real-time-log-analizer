FROM python:3.11-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install pip --upgrade
RUN pip install -r requirements.txt --no-cache-dir
COPY ./web/ .
RUN chmod 700 entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]