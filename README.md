
![Kafkaescli](docs/images/kafkaescli-repository-open-graph-template.png)

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
# produce from stdin per line
echo "hello world of kfk" | kafkaescli produce hello --stdin
# produce to topic `world` form the output of a consumer of topic `hello`
kafkaescli consume hello | kafkaescli produce world --stdin
# produce `world` to `hello`, with middleware
kafkaescli produce hello json --middleware examples.json.JSONMiddleware
# consume from hello with middleware
kafkaescli consume hello --middleware examples.json.JSONMiddleware
# run the web api http://localhost:8000/docs
kafkaescli runserver
# POST consumed messages to WEBHOOK
kafkaescli consume hello --metadata --webhook https://myendpoint.example.com
# For more details see
kafkaescli --help
```

# Contributions

* [Jony Kalavera](https://github.com/jonykalavera)

Pull-requests are welcome and will be processed on a best-effort basis.
Follow the [contributing guide](CONTRIBUTING.md).
