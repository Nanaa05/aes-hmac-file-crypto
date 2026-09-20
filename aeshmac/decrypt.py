import hashlib
import os
import sys
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .crypto_common import CHUNK, IV_LEN, MAGIC, TAG_LEN, dec_path, load_key

def do_decrypt(input_path, key_path, out_path=None):
    out_path = out_path or dec_path(input_path)
    aes_key, mac_key = load_key(key_path)
    body_len = os.path.getsize(input_path) - TAG_LEN
    if body_len < len(MAGIC) + IV_LEN:
        sys.exit("VERIFY FAILED: file is too short to be a CSEC1 container")
    with open(input_path, "rb") as fin:
        header = fin.read(len(MAGIC) + IV_LEN)
        if header[:len(MAGIC)] != MAGIC:
            sys.exit("VERIFY FAILED: bad magic (not a CSEC1 file)")
        iv = header[len(MAGIC):]
        h = hmac.HMAC(mac_key, hashes.SHA256())
        h.update(header)
        remaining = body_len - len(header)
        while remaining:
            chunk = fin.read(min(CHUNK, remaining))
            if not chunk:
                sys.exit("VERIFY FAILED: truncated file")
            remaining -= len(chunk)
            h.update(chunk)
        try:
            h.verify(fin.read(TAG_LEN))
        except InvalidSignature:
            print("VERIFY FAILED: HMAC mismatch - file was tampered with "
                  "or wrong key", file=sys.stderr)
            return 1
        print("VERIFY OK: HMAC-SHA256 matches")
        fin.seek(len(header))
        decryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        digest = hashlib.sha256()
        remaining = body_len - len(header)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "wb") as fout:
            while remaining:
                chunk = fin.read(min(CHUNK, remaining))
                remaining -= len(chunk)
                plain = unpadder.update(decryptor.update(chunk))
                digest.update(plain)
                fout.write(plain)
            plain = unpadder.update(decryptor.finalize()) + unpadder.finalize()
            digest.update(plain)
            fout.write(plain)
    print(f"decrypted {input_path} -> {out_path}")
    print(f"  plaintext sha256: {digest.hexdigest()}")
    return 0
