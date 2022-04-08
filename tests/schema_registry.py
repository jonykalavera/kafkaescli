import json
import os

SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")

from confluent_kafka.schema_registry.avro import AvroDeserializer, SchemaRegistryClient

schema_registry = SchemaRegistryClient(SCHEMA_REGISTRY_URL)


def callback(payload):
    print("HELLO CALLBACK")
    payload["value"] = AvroDeserializer(schema_registry=schema_registry)(
        payload["value"]
    )
    return payload


async def async_callback(payload):
    return callback(payload=payload)
