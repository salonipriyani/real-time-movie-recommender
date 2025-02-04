FROM python:3.10.7

COPY . /usr/src/app/
WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV DB_USER root
ENV DB_PASSWORD password

EXPOSE 9092
EXPOSE 5432


ENTRYPOINT ["python"]
CMD ["consumeKafka.py"]