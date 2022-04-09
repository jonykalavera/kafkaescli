FROM python:3.10.2

ARG KAFKAESCLI_API_TOKEN
ARG KAFKAESCLI_API_URL=https://otc.uat.kafkaescli.net/

ENV KAFKAESCLI_API_TOKEN=${KAFKAESCLI_API_TOKEN}
ENV KAFKAESCLI_API_URL=${KAFKAESCLI_API_URL}

WORKDIR /dist

COPY ./dist/* .

RUN python -m pip install ./kafkaescli-0.1.0-py3-none-any.whl

CMD [ "python", "-m", "kafkaescli" ]
