from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, AsyncIterator, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import (
    ConsumerStoppedError,
    IllegalOperation,
    IllegalStateError,
    KafkaConnectionError,
    KafkaError,
    NodeNotReadyError,
    NoOffsetForPartitionError,
    OffsetOutOfRangeError,
    RecordTooLargeError,
    RequestTimedOutError,
    StaleMetadata,
    TopicAuthorizationFailedError,
    UnknownTopicOrPartitionError,
    UnrecognizedBrokerVersion,
    UnsupportedVersionError,
)

from kafkaescli.core.config.models import Settings
from kafkaescli.core.config.services import ConfigService

if TYPE_CHECKING:
    from aiokafka.structs import ConsumerRecord

from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.core.producer.models import ProducerPayload
from kafkaescli.lib.results import as_result

KAFKA_EXCEPTIONS = (
    KafkaError,
    KafkaConnectionError,
    NodeNotReadyError,
    RequestTimedOutError,
    UnknownTopicOrPartitionError,
    UnrecognizedBrokerVersion,
    StaleMetadata,
    TopicAuthorizationFailedError,
    OffsetOutOfRangeError,
    ConsumerStoppedError,
    IllegalOperation,
    UnsupportedVersionError,
    IllegalStateError,
    NoOffsetForPartitionError,
    RecordTooLargeError,
)


@dataclass
class Consumer:
    config_service: ConfigService
    _consumer: AIOKafkaConsumer = field(init=False)

    def _consumer_record_to_payload(self, value: "ConsumerRecord") -> ConsumerPayload:
        return ConsumerPayload.parse_obj(
            dict(
                metadata={
                    k: v if not isinstance(v, bytes) else v.decode("utf-8", "ignore")
                    for k, v in asdict(value).items()
                    if k != "value"
                },
                value=value.value,
            )
        )

    @as_result(*KAFKA_EXCEPTIONS)
    async def execute(
        self,
        topics: List[str],
        group_id: Optional[str] = None,
        enable_auto_commit: bool = False,
        auto_offset_reset: str = 'latest',
        auto_commit_interval_ms: int = 1000,
    ) -> AsyncIterator[ConsumerPayload]:
        config = self.config_service.execute().unwrap_or_throw()
        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=config.bootstrap_servers,
            *topics,
            group_id=group_id,
            enable_auto_commit=enable_auto_commit,
            auto_offset_reset=auto_offset_reset,
            auto_commit_interval_ms=auto_commit_interval_ms,
        )
        # Get cluster layout and join group `my-group`
        await self._consumer.start()
        try:
            # Consume values
            async for msg in self._consumer:
                payload = self._consumer_record_to_payload(msg)
                yield payload
                await self._consumer.commit()
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self._consumer.stop()


@dataclass
class Producer:
    config_service: ConfigService
    _config: Settings = field(init=False)
    _producer: AIOKafkaProducer = field(init=False)

    def __post_init__(self):
        self._config = self.config_service.execute().unwrap_or_throw()

    @as_result(*KAFKA_EXCEPTIONS)
    async def execute(self, topic: str, value: bytes, key: Optional[bytes] = None, partition=1) -> ProducerPayload:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._config.bootstrap_servers)
        await self._producer.start()
        try:
            meta = await self._producer.send_and_wait(topic, value=value, key=key, partition=partition)
        finally:
            await self._producer.stop()
        payload = ProducerPayload(metadata=meta._asdict(), value=value, key=key)
        return payload
