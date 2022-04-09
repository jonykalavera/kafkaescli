from typing import Union

# so long as we can send it as json in the end
JSONSerializable = Union[str, bytes, list, dict, tuple, int, float]
