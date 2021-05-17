FROM python:3.7

ADD requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

ADD ./ /app/

EXPOSE 8000

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
