"""Containers module."""

from typing import Optional

from dependency_injector import containers, providers

from kafkaescli import constants
from kafkaescli.core.config.services import ConfigFileService, ConfigService
from kafkaescli.core.consumer.services import ConsumeService
from kafkaescli.core.middleware.models import MiddlewareHook
from kafkaescli.core.middleware.services import MiddlewareService
from kafkaescli.core.producer.services import ProduceService
from kafkaescli.infra.kafka import Consumer, Producer
from kafkaescli.infra.webhook import WebhookHandler


class Container(containers.DeclarativeContainer):
    # overridable config
    config_file_path = providers.Object(constants.DEFAULT_CONFIG_FILE_PATH)
    overrides = providers.Dict()
    profile_name = providers.Object(str)

    # Services
    config_file_service = providers.Factory(ConfigFileService, config_file_path=config_file_path)
    config_service = providers.Factory(
        ConfigService,
        config_file_service=config_file_service,
        profile_name=profile_name,
        overrides=overrides,
    )
    consumer = providers.Factory(
        Consumer,
        config_service=config_service,
    )
    producer = providers.Factory(
        Producer,
        config_service=config_service,
    )
    webhook_handler = providers.Factory(
        WebhookHandler,
    )
    hook_after_consume = providers.Factory(
        MiddlewareService, callback=MiddlewareHook.AFTER_CONSUME, config_service=config_service
    )
    hook_before_produce = providers.Factory(
        MiddlewareService, callback=MiddlewareHook.BEFORE_PRODUCE, config_service=config_service
    )
    consume_service = providers.Factory(
        ConsumeService,
        consumer=consumer,
        webhook_handler=webhook_handler,
        hook_after_consume=hook_after_consume,
    )
    produce_service = providers.Factory(
        ProduceService,
        producer=producer,
        hook_before_produce=hook_before_produce,
    )
