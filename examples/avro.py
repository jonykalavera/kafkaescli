"""AVRO tools module."""
import io
import json

import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.core.models import JSONSerializable


def deserialize(value):
    """De-serializes AVRO encoded binary string and yield records.

    Args:
        value (str): binary string value.

    Yields:
        dict: de-serialized record.
    """
    file_desc = io.BytesIO(value)
    setattr(file_desc, "mode", ["b"])
    with DataFileReader(file_desc, DatumReader()) as reader:
        yield from reader


def deserialize_first(value):
    """Deserialize AVRO encoded binary string and return the first record.

    Args:
        value (str): binary string value.

    Returns:
        dict: de-serialized record.
    """
    return next(deserialize(value))


def serialize(records, schema_json):
    """Serialize list of records to AVRO encoded binary string.

    Args:
        records (list): list of records.
        schema_json (str): json encoded schema to be used.

    Returns:
        string: binary string value.
    """
    schema = avro.schema.parse(schema_json)  # need to know the schema to write
    output = io.BytesIO()
    result = b""
    with DataFileWriter(output, DatumWriter(), schema) as writer:
        for record in records:
            writer.append(record)
        writer.flush()
        result = writer.writer.getvalue()
    return result


EMPLOYEE_SCHEMA = json.dumps(
    {
        "type": "record",
        "namespace": "app.domain",
        "name": "Employee",
        "fields": [{"name": "Name", "type": "string"}, {"name": "Age", "type": "int"}],
    }
)


async def hook_before_produce(value: JSONSerializable) -> JSONSerializable:
    value = serialize([json.loads(str(value))], EMPLOYEE_SCHEMA)
    return value


async def hook_after_consume(payload: ConsumerPayload) -> ConsumerPayload:
    payload.value = deserialize_first(payload.value)
    return payload
