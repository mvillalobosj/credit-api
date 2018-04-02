FROM alpine:3.6

RUN apk — update upgrade \
  && apk add --update \
              bash \
              build-base \
              curl \
              git \
              gcc \
              g++ \
              make \
              musl \
              python-dev \
              python3 \
              python3-dev \
              postgresql-dev \
              unzip \
              wget \
              zlib-dev \
  && pip3.6 install --upgrade pip \
  && rm /var/cache/apk/*

# make some useful symlinks that are expected to exist
RUN cd /usr/bin \
  && ln -sf easy_install-3.6 easy_install \
  && ln -sf idle3.6 idle \
  && ln -sf pydoc3.6 pydoc \
  && ln -sf python3.6 python \
  && ln -sf python-config3.6 python-config \
  && ln -sf pip3.6 pip

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt /app/requirements.txt
COPY testing_requirements.txt /app/testing_requirements.txt
# pip install dependencies
RUN pip3 install -U pip && \
  pip3 install -r requirements.txt && \
  pip3 install -r testing_requirements.txt

RUN pip3 install gunicorn==19.7.0
COPY . /app

CMD ["gunicorn", \
     "--access-logfile=-", \
     "--error-logfile=-", \
     "--bind=0.0.0.0:5001", \
     "--workers=1", \
     "--timeout=120", \
     "--reload", \
     "--log-level=debug", \
     "app.wsgi:app"]
