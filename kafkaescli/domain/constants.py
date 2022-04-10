import pkg_resources


APP_TITLE = "KafkaesCLI"
APP_PACKAGE = "kafkaescli"

try:
    APP_VERSION = pkg_resources.get_distribution(APP_PACKAGE).version
except pkg_resources.DistributionNotFound:
    APP_VERSION = 'development'

DEFAULT_BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_CONFIG_FILE_PATH = "~/.kafkaescli/config.json"
