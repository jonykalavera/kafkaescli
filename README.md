
![KafkesCLI](docs/images/kafkescli-repository-open-graph-template.png)

# Install

Install from git

```sh
pip install git+https://github.com/jonykalavera/kafkescli.git
```

# Usage

```bash
# general help
kafkescli --help
# command help
kafkescli consume --help
# consume from hello
kafkescli consume hello
# consume from hello with callback function
kafkescli consume hello --callback examples.json.consume
# produce to hello, the message: world
kafkescli produce hello world
# produce to hello, the message: "world of cli kafka"
kafkescli produce hello "world of cli kafka"
# produce to hello, the message: world with callback function
kafkescli produce hello world --callback examples.json.produce
# run producer endpoint
kafkescli runserver
# produce to hello, from stdin lines"
echo "hello world of kfk" | kafkescli produce hello --stdin
# consume from hello piped to produce to world
kafkescli consume hello | kafkescli produce world --stdin
# consume from hello showing medadata and post to webhook
kafkescli consume hello --metadata --webhook https://myendpoint.example.com
```

# Contributions

* [Jony Kalavera](https://github.com/jonykalavera)

Pull-requests are welcome and will be processed on a best-effort basis.
Follow the [contributing guide](CONTRIBUTING.md).
