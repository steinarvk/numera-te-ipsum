FROM tiangolo/uwsgi-nginx:python2.7

RUN apt-get update -qq && apt-get install -y \
  libpq-dev

COPY . /app

RUN pip install -r requirements.txt

RUN python /app/setup.py install --force

COPY docker/nginx.conf /etc/nginx/conf.d/
COPY docker/uwsgi.ini /app/
COPY secrets/config.yaml /app/
