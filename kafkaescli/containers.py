"""Containers module."""

from dependency_injector import containers, providers
from kafkaescli.lib.kafka import Consumer, Producer
from kafkaescli.lib.webhook import WebhookHandler
from kafkaescli.lib.middleware import MiddlewarePipeline
from . import services


class Container(containers.DeclarativeContainer):
    # Gateways
    consumer = providers.Object(
        Consumer,
    )
    producer = providers.Object(
        Producer,
    )
    webhook_handler = providers.Object(
        WebhookHandler,
    )
    middleware_pipeline = providers.Object(
        MiddlewarePipeline
    )
    # Services
    consumer_service = providers.Factory(
        services.ConsumeService,
        consumer=consumer,
        webhook_handler=webhook_handler,
        middleware_pipeline=middleware_pipeline,
    )