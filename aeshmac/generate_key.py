import os
from .crypto_common import KEY_LEN

def do_generate_key(out_path):
    """Generate the 32-byte shared secret."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fd = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(os.urandom(KEY_LEN))
        print(f"wrote {KEY_LEN}-byte shared secret to {out_path}")
