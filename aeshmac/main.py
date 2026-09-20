import argparse
import sys
from importlib.metadata import version, PackageNotFoundError

from .crypto_common import KEY_FILE
from .encrypt import do_encrypt
from .decrypt import do_decrypt
from .generate_key import do_generate_key

try:
    __version__ = version("aeshmac")
except PackageNotFoundError:
    __version__ = "unknown"

def main():
    parser = argparse.ArgumentParser(description="AES-HMAC file encryption/decryption utility")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", action="store_true", help="Encrypt a file")
    group.add_argument("-d", "--decrypt", action="store_true", help="Decrypt a file")
    group.add_argument("-g", "--generate-key", action="store_true", help="Generate a new shared secret key")
    
    parser.add_argument("input", nargs="?", help="Input file (required for encrypt/decrypt)")
    parser.add_argument("-k", "--key", default=KEY_FILE, help=f"Path to the shared secret key (default: {KEY_FILE})")
    parser.add_argument("-o", "--out", help="Override the default output path")
    
    args = parser.parse_args()
    
    if args.generate_key:
        do_generate_key(args.out or args.key)
        return 0
        
    if not args.input:
        parser.error("input file is required for encryption and decryption")
        
    if args.encrypt:
        do_encrypt(args.input, args.key, args.out)
    elif args.decrypt:
        return do_decrypt(args.input, args.key, args.out)
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
