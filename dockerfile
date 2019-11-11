FROM python:3.6.5

RUN pip install --upgrade pip

ADD . /backend

WORKDIR /backend

RUN pip install -r requirements.txt

EXPOSE 5000

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info