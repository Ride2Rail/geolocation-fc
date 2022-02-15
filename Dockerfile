FROM python:3.9

WORKDIR /code

ENV FLASK_APP=geolocation-fc.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY geolocation-fc.py geolocation-fc.py
COPY  geolocation-fc.conf  geolocation-fc.conf
COPY  codes codes

EXPOSE 5015

CMD ["flask", "run"]