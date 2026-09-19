import argparse
import hashlib
import os
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from crypto_common import CHUNK, IV_LEN, KEY_FILE, MAGIC, enc_path, load_key

def main():
    p = argparse.ArgumentParser(description="encrypt a file (AES-256-CBC + HMAC)")
    p.add_argument("input", help="file to encrypt")
    p.add_argument("-k", "--key", default=KEY_FILE)
    p.add_argument("-o", "--out", help="override the default encrypted/<name>.enc")
    args = p.parse_args()
    args.out = args.out or enc_path(args.input)
    aes_key, mac_key = load_key(args.key)
    iv = os.urandom(IV_LEN)
    encryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).encryptor()
    padder = padding.PKCS7(128).padder()
    h = hmac.HMAC(mac_key, hashes.SHA256())
    digest = hashlib.sha256()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.input, "rb") as fin, open(args.out, "wb") as fout:
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
    print(f"encrypted {args.input} -> {args.out}")
    print(f"  plaintext sha256: {digest.hexdigest()}")

if __name__ == "__main__":
    main()
