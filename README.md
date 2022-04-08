
## Examples

```
kafkescli --help
kafkescli consume --help
kafkescli consume hello
kafkescli consume hello --callback tests.json.consume
kafkescli produce hello world
kafkescli produce hello world --callback tests.json.produce
kafkescli produce hello "world of cli kafka"
echo "hello world of kfk" |kafkescli produce hello
kafkescli consume hello | kafkescli produce world
kafkescli consume hello --metadata --webhook https://myendpoint.example.com
```
