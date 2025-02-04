FROM python:3.11.3
COPY . /app
WORKDIR /app

#RUN python3 -m venv /opt/venv

ARG model 
ARG data
ARG pipeline

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 -m pip install gevent 

RUN chmod +x serverAppEntry.sh

EXPOSE 8082
EXPOSE 5001

ENV DB_USERNAME=root
ENV DB_PASSWORD=password
ENV MODEL_ID=$model
ENV DATA_ID=$data
ENV PIPELINE_ID=$pipeline

CMD ["/app/serverAppEntry.sh"]