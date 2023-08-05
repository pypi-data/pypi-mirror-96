"""Package that automatically caches and dispatch serialization and deserialization to the correct functions depending on the extension."""
from .cache import Cache, cache
from .exception import SerializationException

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "Cache", 
    "cache", 
    "SerializationException",
]