"""AVRO tools module."""
import json
import io


# Third Party Library Imports
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import avro.schema



def deserialize(value):
    """ De-serializes AVRO encoded binary string and yield records.

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
    """ Deserialize AVRO encoded binary string and return the first record.

    Args:
        value (str): binary string value.

    Returns:
        dict: de-serialized record.
    """
    return next(deserialize(value))


def serialize(records, schema_json):
    """ Serialize list of records to AVRO encoded binary string.

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
    """ Produce avro with embedded schema message given a json message string.

    Args:
        message: data as json string.
    """
    schema = json.loads(message)
    message = serialize([message], schema)
    return message


def consume(payload):
    """ Deserialized avro with embedded schema.

    Args:
        message: data as json string.
    """
    payload["value"] = deserialize_first(payload["value"])
    return payload
