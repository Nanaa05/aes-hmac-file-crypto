import argparse
import os
from crypto_common import KEY_FILE, KEY_LEN

def main():
  """Generate the 32-byte shared secret used by encrypt.py and decrypt.py."""
  p = argparse.ArgumentParser(description="generate a shared secret")
  p.add_argument("-o", "--out", default=KEY_FILE)
  args = p.parse_args()
  
  os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
  fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
  with os.fdopen(fd, "wb") as f:
      f.write(os.urandom(KEY_LEN))
      print(f"wrote {KEY_LEN}-byte shared secret to {args.out}")

if __name__ == "__main__":
    main()
