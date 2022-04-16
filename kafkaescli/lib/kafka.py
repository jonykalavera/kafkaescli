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

from kafkaescli.domain.constants import DEFAULT_BOOTSTRAP_SERVERS

if TYPE_CHECKING:
    from aiokafka.structs import ConsumerRecord

from kafkaescli.domain.models import ConsumerPayload, ProducerPayload

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
    topics: List[str]
    group_id: Optional[str] = None
    enable_auto_commit: bool = False
    auto_offset_reset: str = 'latest'
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS

    _consumer: AIOKafkaConsumer = field(init=False)

    def consumer_record_to_payload(self, message: "ConsumerRecord") -> ConsumerPayload:
        return ConsumerPayload.parse_obj(
            dict(
                metadata={
                    k: v if not isinstance(v, bytes) else v.decode("utf-8", "ignore")
                    for k, v in asdict(message).items()
                    if k != "value"
                },
                message=message.value,
            )
        )

    async def execute(self) -> AsyncIterator[ConsumerPayload]:
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            group_id=self.group_id,
            enable_auto_commit=self.enable_auto_commit,
            auto_offset_reset=self.auto_offset_reset,
            bootstrap_servers=self.bootstrap_servers,
        )
        # Get cluster layout and join group `my-group`
        await self._consumer.start()
        try:
            # Consume messages
            async for msg in self._consumer:
                payload = self.consumer_record_to_payload(msg)
                yield payload
                await self._consumer.commit()
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self._consumer.stop()


@dataclass
class Producer:
    bootstrap_servers: str
    topic: str
    value: bytes
    key: Optional[bytes] = None
    partition = 1
    _producer: AIOKafkaProducer = field(init=False)

    async def execute(self) -> ProducerPayload:
        self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        # Get cluster layout and initial topic/partition leadership information
        await self._producer.start()
        try:
            meta = await self._producer.send_and_wait(
                self.topic, value=self.value, key=self.key, partition=self.partition
            )
        finally:
            # Wait for all pending messages to be delivered or expire.
            await self._producer.stop()
        payload = ProducerPayload(metadata=meta._asdict(), message=self.value, key=self.key)
        return payload
