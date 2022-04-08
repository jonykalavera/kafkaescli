FROM python:3.10.2

ARG KAFKESCLI_API_TOKEN
ARG KAFKESCLI_API_URL=https://otc.uat.kafkescli.net/

ENV KAFKESCLI_API_TOKEN=${KAFKESCLI_API_TOKEN}
ENV KAFKESCLI_API_URL=${KAFKESCLI_API_URL}

WORKDIR /dist

COPY ./dist/* .

RUN python -m pip install ./kafkescli-0.1.0-py3-none-any.whl

CMD [ "python", "-m", "kafkescli" ]
