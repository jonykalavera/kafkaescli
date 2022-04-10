import pkg_resources


APP_TITLE = "KafkaesCLI"
APP_PACKAGE = "kafkaescli"
APP_VERSION = pkg_resources.get_distribution(APP_PACKAGE).version
DEFAULT_BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_CONFIG_FILE_PATH = "~/.kafkaescli/config.json"
