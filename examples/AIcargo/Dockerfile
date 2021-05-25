FROM python:3.7

# RUN apt-get update && apt-get install -y gunicorn

ADD requirements.txt /app/

WORKDIR /app

RUN pip install --upgrade sentry-sdk
RUN pip install -r requirements.txt

ADD ./ /app/

EXPOSE 8000

CMD ["sh", "./entry.sh"]
