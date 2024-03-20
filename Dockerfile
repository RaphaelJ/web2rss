FROM python:3.11-bullseye


COPY . /app
WORKDIR /app

ENV PYTHONPATH="$PYTHONPATH:/app/src"

RUN pip install -r requirements.txt

ENV APP_SETTINGS="web2rss.config.ProductionConfig"
ENV DATABASE_URL="sqlite:///producton.sqlite3"

# These variables are required to run the create_tables script, but will be overriden when runing
# the image.
ENV SERVER_NAME="127.0.0.1"
ENV SECRET_KEY="some_secret_keu"
ENV MISTRAL_API_KEY="none"

RUN python -m web2rss.main create_tables

EXPOSE 8080

CMD [                               \
    "gunicorn",                     \
    "-c", "gunicorn.conf.py",       \
    "-b", "0.0.0.0:8080",           \
    "web2rss.app:app"               \
]