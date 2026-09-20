import os
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

MAGIC = b"CSEC1"
IV_LEN = 16
TAG_LEN = 32
CHUNK = 64 * 1024
KEY_LEN = 32
KEY_FILE = "keys/shared.key"
ENC_DIR = "encrypted"
DEC_DIR = "decrypted"
ENC_SUFFIX = ".enc"

def enc_path(src):
    """samples/small.txt -> encrypted/small.txt.enc"""
    return os.path.join(ENC_DIR, os.path.basename(src) + ENC_SUFFIX)

def dec_path(src):
    """encrypted/small.txt.enc -> decrypted/small.txt"""
    name = os.path.basename(src)
    if name.endswith(ENC_SUFFIX):
        name = name[:-len(ENC_SUFFIX)]
    return os.path.join(DEC_DIR, name)

def derive(secret):
    """Split one shared secret into an AES key and a separate MAC key."""
    def sub(info):
        return HKDF(algorithm=hashes.SHA256(), length=KEY_LEN,
                    salt=None, info=info).derive(secret)
    return sub(b"aes-key"), sub(b"hmac-key")

def load_key(path):
    """Read the shared secret file and return (aes_key, mac_key)."""
    with open(path, "rb") as f:
        secret = f.read()
    if len(secret) < KEY_LEN:
        sys.exit(f"key file {path} is too short "
                 f"({len(secret)} bytes, need >= {KEY_LEN})")
    return derive(secret)
