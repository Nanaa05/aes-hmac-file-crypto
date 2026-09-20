import hashlib
import os
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .crypto_common import CHUNK, IV_LEN, MAGIC, enc_path, load_key

def do_encrypt(input_path, key_path, out_path=None):
    out_path = out_path or enc_path(input_path)
    aes_key, mac_key = load_key(key_path)
    iv = os.urandom(IV_LEN)
    encryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).encryptor()
    padder = padding.PKCS7(128).padder()
    h = hmac.HMAC(mac_key, hashes.SHA256())
    digest = hashlib.sha256()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(input_path, "rb") as fin, open(out_path, "wb") as fout:
        header = MAGIC + iv
        h.update(header)
        fout.write(header)
        while True:
            chunk = fin.read(CHUNK)
            if not chunk:
                break
            digest.update(chunk)
            block = encryptor.update(padder.update(chunk))
            h.update(block)
            fout.write(block)
        block = encryptor.update(padder.finalize()) + encryptor.finalize()
        h.update(block)
        fout.write(block)
        fout.write(h.finalize())
    print(f"encrypted {input_path} -> {out_path}")
    print(f"  plaintext sha256: {digest.hexdigest()}")
