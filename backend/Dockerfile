FROM python:3.8

ENV root /usr
ENV src /usr/src

COPY requirements.txt $root
RUN pip install -r $root/requirements.txt

COPY src $src
WORKDIR $src

CMD PYTHONPATH=/usr python /usr/src/api/controllers.py