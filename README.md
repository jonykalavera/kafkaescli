
![Kafkaescli](docs/images/kafkaescli-repository-open-graph-template.png)

[![CircleCI](https://circleci.com/gh/jonykalavera/kafkaescli/tree/main.svg?style=svg)](https://circleci.com/gh/jonykalavera/kafkaescli/tree/main)

# Install

Install from git

```sh
pip install git+https://github.com/jonykalavera/kafkaescli.git
```

# Usage

```bash
# general help
kafkaescli --help
# command help
kafkaescli consume --help
# consume from hello
kafkaescli consume hello
# consume from hello with callback function
kafkaescli consume hello --callback examples.json.consume
# produce to hello, the message: world
kafkaescli produce hello world
# produce to hello, the message: "world of cli kafka"
kafkaescli produce hello "world of cli kafka"
# produce to hello, the message: world with callback function
kafkaescli produce hello world --callback examples.json.produce
# run producer endpoint
kafkaescli runserver
# produce to hello, from stdin lines"
echo "hello world of kfk" | kafkaescli produce hello --stdin
# consume from hello piped to produce to world
kafkaescli consume hello | kafkaescli produce world --stdin
# consume from hello showing medadata and post to webhook
kafkaescli consume hello --metadata --webhook https://myendpoint.example.com
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
