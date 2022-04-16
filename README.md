
![Kafkaescli](docs/images/kafkaescli-repository-open-graph-template.png)
[![Coverage Status](https://coveralls.io/repos/github/jonykalavera/kafkaescli/badge.svg?branch=main)](https://coveralls.io/github/jonykalavera/kafkaescli?branch=main)
[![CircleCI](https://circleci.com/gh/jonykalavera/kafkaescli/tree/main.svg?style=svg)](https://circleci.com/gh/jonykalavera/kafkaescli/tree/main) [![Join the chat at https://gitter.im/jonykalavera/kafkaescli](https://badges.gitter.im/jonykalavera/kafkaescli.svg)](https://gitter.im/jonykalavera/kafkaescli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# Install

Install from [pypi](https://pypi.org/project/kafkaescli/)

```sh
pip install kafkaescli
```

# Usage

```bash
# consume from `hello`
kafkaescli consume hello
# consume from `hello` showing metadata
kafkaescli consume hello --metadata
# produce topic `hello`
kafkaescli produce hello world
# produce longer strings
kafkaescli produce hello "world of kafka"
# produce from stdin a value per line
cat values.json | kafkaescli produce hello --stdin
# produce to topic `world` form the output of a consumer of topic `hello`
kafkaescli consume hello | kafkaescli produce world --stdin
# produce `{"foo":"bar"}` to topic `hello`, with middleware
kafkaescli produce hello '{"foo":"bar"}' --middleware '{"hook_before_produce": "examples.json.hook_before_produce"}'
# consume from topic `hello` with middleware
kafkaescli consume hello --middleware '{"hook_after_consume": "examples.json.hook_after_consume"}'
# run the web api http://localhost:8000/docs
kafkaescli runserver
# POST consumed values to WEBHOOK
kafkaescli consume hello --metadata --webhook https://myendpoint.example.com
# For more details see
kafkaescli --help
```
These examples assume a Kafka instance is running at `localhost:9092`

# Contributions

* [Jony Kalavera](https://github.com/jonykalavera)

Pull-requests are welcome and will be processed on a best-effort basis.
Follow the [contributing guide](CONTRIBUTING.md).
