FROM .

WORKDIR /code
ADD ./ ./
RUN make pip-install

CMD [ "make", "test"]
