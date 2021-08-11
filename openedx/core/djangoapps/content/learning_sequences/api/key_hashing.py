"""
Experimental API definitions related to generating and inspecting URL-friendly
hashes of usage keys, allowing courseware URLs to be shortened.
See TNL-8638 for details.

Do not import from this module directly.
Use openedx.core.djangoapps.content.learning_sequences.api -- that
__init__.py imports from here, and is a more stable place to import from.
"""
import hashlib
import math
from base64 import urlsafe_b64encode

from opaque_keys.edx.keys import UsageKey

# This constant must be defined in models.py to prevent an import cycle,
# but we intentionally re-export it as part of the public learning_sequences API.
from ..models import USAGE_KEY_HASH_LENGTH

# Number of hash digest bits needed in order to produce a base64-encoded output
# of length `USAGE_KEY_HASH_LENGTH`.
# Each base64 character captures 6 bits (because 2 ^ 6 = 64).
_USAGE_KEY_HASH_BITS = USAGE_KEY_HASH_LENGTH * 6

# Number of hash digest bytes needed in order to produce a base64-encoded output
# of length `USAGE_KEY_HASH_LENGTH`. Is equal to one eighth of `_USAGE_KEY_HASH_BITS`.
# In the event that _USAGE_KEY_HASH_BITS is not divisible by 8, we round up.
# We will cut off the extra any output at the end of `hash_usage_key`.
_USAGE_KEY_HASH_BYTES = math.ceil(_USAGE_KEY_HASH_BITS / 8)

# A regex to capture strings that could be the output of `hash_usage_key`.
# Captures a string of length `USAGE_KEY_HASH_LENGTH`, made up of letters,
# numbers, dashes, underscores, and/or equals signs.
USAGE_KEY_HASH_PATTERN = rf'(?P<usage_key_hash>[A-Z_a-z0-9=-]{{{USAGE_KEY_HASH_LENGTH}}})'


def hash_usage_key(usage_key: UsageKey) -> str:
    """
    Get the blake2b hash key for the given usage_key and encode the value.

    Encoding is URL-safe Base64, which includes (case-sensitive) letters,
    numbers, and the dash (-), underscore (_) and equals (=) characters.

    Args:
        usage_key: the id of the location to which to generate the path

    Returns:
        The string of the encoded hashed key, of length `USAGE_KEY_HASH_LENGTH`.
    """
    usage_key_bytes = bytes(str(usage_key), 'utf-8')
    usage_key_hash_bytes = hashlib.blake2b(
        usage_key_bytes, digest_size=_USAGE_KEY_HASH_BYTES
    ).digest()
    encoded_hash_bytes = urlsafe_b64encode(usage_key_hash_bytes)
    encoded_hash = str(encoded_hash_bytes, 'utf-8')
    # When `USAGE_KEY_HASH_LENGTH` is divisible by 4,
    # `encoded_hash` should end up equal to `trimmed_encoded_hash`.
    trimmed_encoded_hash = encoded_hash[:USAGE_KEY_HASH_LENGTH]
    return trimmed_encoded_hash
