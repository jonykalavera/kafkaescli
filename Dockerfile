FROM python:3.10.2

ARG KAFKAESCLI_VERSION
ENV KAFKAESCLI_VERSION=${KAFKAESCLI_VERSION}

WORKDIR /dist
COPY ./dist/* ./
RUN pip install "./kafkaescli-${KAFKAESCLI_VERSION}-py3-none-any.whl"

CMD [ "python", "-m", "kafkaescli" ]
