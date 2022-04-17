"""Services module."""
from dataclasses import dataclass
import logging
from typing import Dict, Type

from kafkaescli.domain import models, constants
from kafkaescli.lib.kafka import Consumer, Producer
from kafkaescli.lib.middleware import MiddlewarePipeline
from kafkaescli.lib.webhook import WebhookHandler
from kafkaescli.app.commands import ConsumeCommand

class BaseService:

    def __init__(self) -> None:
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )


@dataclass
class ConsumeService(BaseService):
    consumer: Type[Consumer]
    webhook_handler: Type[WebhookHandler]
    middleware_pipeline: Type[MiddlewarePipeline]

    def execute(self, cmd: ConsumeCommand):
        cmd._hook_after_consume = self.middleware_pipeline(cmd.config.middleware, models.MiddlewareHook.AFTER_CONSUME)
        cmd._webhook = self.webhook_handler(webhook=cmd.webhook)
        cmd._consumer = self.consumer(
            topics=cmd.topics,
            group_id=cmd.group_id,
            enable_auto_commit=False,
            auto_offset_reset=cmd.auto_offset_reset,
            bootstrap_servers=cmd.config.bootstrap_servers,
        )
        return cmd.execute()
