FROM python:3.9

WORKDIR /app

RUN apt-get update && \
    apt-get install -y zip && \
    rm -rf /var/lib/apt/lists/*

VOLUME [ "/app" ]

RUN pip install boto3 requests -t /app
RUN cd /app && zip -r /app/lambda.zip .

COPY ./entrypoint.sh ./

ENTRYPOINT ["./entrypoint.sh"]
CMD ["builder"]