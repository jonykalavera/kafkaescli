import json
from dataclasses import asdict
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
from kafkaescli.domain.types import JSONSerializable

if TYPE_CHECKING:
    from aiokafka.structs import ConsumerRecord, RecordMetadata

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


def consumer_record_to_payload(message: "ConsumerRecord") -> ConsumerPayload:
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


async def consume_messages(
    topics: List[str],
    group_id: Optional[str] = None,
    enable_auto_commit: bool = True,
    auto_offset_reset: str = 'latest',
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS,
) -> AsyncIterator["ConsumerRecord"]:
    consumer = AIOKafkaConsumer(
        *topics,
        group_id=group_id,
        enable_auto_commit=enable_auto_commit,
        auto_offset_reset=auto_offset_reset,
        bootstrap_servers=bootstrap_servers,
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            payload = consumer_record_to_payload(msg)
            yield payload
            await consumer.commit()
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


async def produce_message(
    bootstrap_servers, topic, value: bytes, key: Optional[bytes], partition=1
) -> ProducerPayload:
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        meta = await producer.send_and_wait(topic, value, partition=partition)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
    payload = ProducerPayload(metadata=meta._asdict(), message=value, key=key)
    return payload
