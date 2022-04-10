
![Kafkaescli](docs/images/kafkaescli-repository-open-graph-template.png)

[![CircleCI](https://circleci.com/gh/jonykalavera/kafkaescli/tree/main.svg?style=svg)](https://circleci.com/gh/jonykalavera/kafkaescli/tree/main)

# Install

Install from git

```sh
pip install git+https://github.com/jonykalavera/kafkaescli.git
```

# Usage

## Consume

```bash
# consume from `hello`
kafkaescli consume hello
# consume from `hello` showing metadata
kafkaescli consume hello --metadata
# produce totopic `hello`
kafkaescli produce hello world
# produce longer strings
kafkaescli produce hello "world of kafka"
# produce from stdin per line
echo "hello world of kfk" | kafkaescli produce hello --stdin
# produce to topic `world` form the output of a consumer of topic `hello`
kafkaescli consume hello | kafkaescli produce world --stdin
# produce `world` to `hello`, with middleware
kafkaescli produce hello json --middleware examples.json.JSONMiddleware
# consume from hello with middleware
kafkaescli consume hello --middleware examples.json.JSONMiddleware
# run a producer REST endpoint
kafkaescli runserver
# post consumed messages to WEBHOOK
kafkaescli consume hello --metadata --webhook https://myendpoint.example.com
# For more details see
kafkaescli --help
```

# Contributions

* [Jony Kalavera](https://github.com/jonykalavera)

Pull-requests are welcome and will be processed on a best-effort basis.
Follow the [contributing guide](CONTRIBUTING.md).

# Development

```sh
# install delopment dependencies
$ make install
$ alias kfk='python -m kafkaescli'
```
