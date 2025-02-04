FROM python:3.11.3
COPY . /app
WORKDIR /app

#RUN python3 -m venv /opt/venv

ARG female_model
ARG female_data
ARG male_model
ARG male_data
ARG pipeline

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 -m pip install gevent 

RUN chmod +x serverAppEntry.sh

EXPOSE 8082
EXPOSE 5002

ENV DB_USERNAME=root
ENV DB_PASSWORD=password

ENV FEMALE_MODEL_ID=$female_model
ENV FEMALE_DATA_ID=$female_data
ENV MALE_MODEL_ID=$male_model
ENV MALE_DATA_ID=$male_data
ENV PIPELINE_ID=$pipeline

CMD ["/app/serverAppEntry.sh"]