FROM tiangolo/uwsgi-nginx:python2.7

RUN apt-get update -qq && apt-get install -y \
  libpq-dev

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY docker/nginx.conf /etc/nginx/conf.d/
COPY docker/uwsgi.ini /app/
COPY secrets/config.yaml /app/

COPY . /app

RUN python /app/setup.py install --force
