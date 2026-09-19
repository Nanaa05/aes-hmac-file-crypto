import argparse
import hashlib
import os
import sys
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from crypto_common import (CHUNK, IV_LEN, KEY_FILE, MAGIC, TAG_LEN, dec_path, load_key)

def main():
    p = argparse.ArgumentParser(description="verify then decrypt a file")
    p.add_argument("input", help="the .enc file to verify and decrypt")
    p.add_argument("-k", "--key", default=KEY_FILE)
    p.add_argument("-o", "--out", help="override the default decrypted/<name>")
    args = p.parse_args()
    args.out = args.out or dec_path(args.input)
    aes_key, mac_key = load_key(args.key)
    body_len = os.path.getsize(args.input) - TAG_LEN
    if body_len < len(MAGIC) + IV_LEN:
        sys.exit("VERIFY FAILED: file is too short to be a CSEC1 container")
    with open(args.input, "rb") as fin:
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
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "wb") as fout:
            while remaining:
                chunk = fin.read(min(CHUNK, remaining))
                remaining -= len(chunk)
                plain = unpadder.update(decryptor.update(chunk))
                digest.update(plain)
                fout.write(plain)
            plain = unpadder.update(decryptor.finalize()) + unpadder.finalize()
            digest.update(plain)
            fout.write(plain)
    print(f"decrypted {args.input} -> {args.out}")
    print(f"  plaintext sha256: {digest.hexdigest()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
