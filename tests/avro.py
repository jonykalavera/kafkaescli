import json
from typing import BinaryIO, Optional

from pydantic_avro.avro_to_pydantic import avsc_to_pydantic

"""AVRO tools module."""
# Standard Library Imports
import io

import avro.schema

# Third Party Library Imports
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import BinaryDecoder, DatumReader, DatumWriter
from avro_schemas import *

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





def produce(message):
    code = bytes(avsc_to_pydantic(json.loads(schemas.get_json(message))), "utf-8")
    filename = '{0}.py'.format(message.replace('.', '__')
    mdl = eval(compile(code, filename=filename, mode='eval'))
    class AvroFactory(ModelFactory):
        __model__ = AvroModel
    mock = AvroFactory.build().dict()
    schema = json.dumps(AvroModel.avro_schema())
    message = serialize([mock], schema)
    return message


def consume(payload):
    payload["value"] = deserialize_first(payload["value"])
    return payload
