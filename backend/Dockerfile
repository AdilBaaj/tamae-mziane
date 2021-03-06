FROM python:3.8

ENV root /usr
ENV src /usr/src

COPY requirements.txt $root
COPY src $src

WORKDIR $src

RUN pip install -r $root/requirements.txt

CMD tail -f /dev/null