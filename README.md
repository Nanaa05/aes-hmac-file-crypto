# AES File Encryption + HMAC

Pair assignment. Three Python scripts using the `cryptography` library:
files are encrypted with **AES-256-CBC** and their integrity/authenticity is
protected with **HMAC-SHA256** (encrypt-then-MAC).

## Setup

Needs Python 3 and the `cryptography` library.

### Option 1: Install as a package

Installing the package makes the `filecrypt` command available everywhere in your environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option 2: Use requirements.txt

If you prefer not to install the package, you can just install the dependencies:

```sh
pip install -r requirements.txt
```

If pip refuses to install system wide, use a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```



Run every command below from the project root, since the default paths are relative.

## 1. Generate the shared key

```sh
# If you installed it as a package:
filecrypt -g

# Or if you used requirements.txt:
python3 -m aeshmac.main -g
```

Writes 32 random bytes to `keys/shared.key`. Do this once. Running it again
overwrites the key, and any file encrypted with the old key can no longer be
decrypted.

## 2. Encrypt

```sh
# If you installed it as a package:
filecrypt -e samples/small.txt
filecrypt -e samples/10mb_file.pdf

# Or if you used requirements.txt:
python3 -m aeshmac.main -e samples/small.txt
python3 -m aeshmac.main -e samples/10mb_file.pdf
```

The output goes to `encrypted/` with `.enc` appended:

```
samples/small.txt      ->  encrypted/small.txt.enc
samples/10mb_file.pdf  ->  encrypted/10mb_file.pdf.enc
```

It also prints the SHA-256 of the original file. Keep that value, it is what your
partner compares against at the end.

## 3. Decrypt

```sh
# If you installed it as a package:
filecrypt -d encrypted/small.txt.enc
filecrypt -d encrypted/10mb_file.pdf.enc

# Or if you used requirements.txt:
python3 -m aeshmac.main -d encrypted/small.txt.enc
python3 -m aeshmac.main -d encrypted/10mb_file.pdf.enc
```

The output goes to `decrypted/` with `.enc` removed, so the original extension is
kept and a decrypted PDF opens normally:

```
encrypted/small.txt.enc      ->  decrypted/small.txt
encrypted/10mb_file.pdf.enc  ->  decrypted/10mb_file.pdf
```

The HMAC is checked first. On success it prints `VERIFY OK` and then decrypts. If
the file was modified or the key is wrong it prints `VERIFY FAILED`, exits with
status 1, and writes no output file.

## 4. Confirm it matches the original

```sh
sha256sum samples/small.txt decrypted/small.txt
sha256sum samples/10mb_file.pdf decrypted/10mb_file.pdf
```

The two hashes on each line must be identical.

## Options

The `filecrypt` command takes the following flags:

| Flag | Meaning                                         |
| ---- | ----------------------------------------------- |
| `-e` | Encrypt a file                                  |
| `-d` | Decrypt a file                                  |
| `-g` | Generate a new shared secret key                |
| `-v` | Show version                                    |
| `-k` | Key file to use (default: `keys/shared.key`)    |
| `-o` | Output path override (derived as shown above)   |

```text
usage: filecrypt [-h] [-v] (-e | -d | -g) [-k KEY] [-o OUT] [input]

AES-HMAC file encryption/decryption utility

positional arguments:
  input               Input file (required for encrypt/decrypt)

options:
  -h, --help          show this help message and exit
  -v, --version       show program's version number and exit
  -e, --encrypt       Encrypt a file
  -d, --decrypt       Decrypt a file
  -g, --generate-key  Generate a new shared secret key
  -k, --key KEY       Path to the shared secret key (default: keys/shared.key)
  -o, --out OUT       Override the default output path
```

## Exchanging files with your partner

Send them:

1. `keys/shared.key`, over a different channel than the file itself.
2. The `.enc` file from `encrypted/`.
3. The SHA-256 that the encrypt command printed.

They run:

```sh
# If you installed it as a package:
filecrypt -d small.txt.enc -k shared.key

# Or if you used requirements.txt:
python3 -m aeshmac.main -d small.txt.enc -k shared.key

sha256sum decrypted/small.txt
```

and check that the hash equals the one you sent. That covers the three steps the
assignment asks for: verify the file, decrypt it, confirm it matches the original.

## Test results

| File                    | Size                      | Result                                  |
| ----------------------- | ------------------------- | --------------------------------------- |
| `samples/small.txt`     | 172 B (under 1 KB)        | VERIFY OK, decrypted, SHA-256 identical |
| `samples/10mb_file.pdf` | 10,615,705 B (over 10 MB) | VERIFY OK, decrypted, SHA-256 identical |

Negative tests, both rejected with exit code 1 and no output written:
a bit flipped inside the ciphertext, and decryption with a different key.

## How it works

| Concern                    | Choice                                                                                                                  |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Confidentiality            | AES-256-CBC, random 16 byte IV per file, PKCS#7 padding                                                                 |
| Integrity and authenticity | HMAC-SHA256 over `magic + iv + ciphertext`                                                                              |
| Key separation             | One 32 byte secret, split by HKDF-SHA256 into an AES key and a separate MAC key, so the same bytes are never used twice |
| Large files                | Streamed in 64 KiB chunks, so a 10 MB file never sits in memory                                                         |

Encrypted file layout:

```
b"CSEC1"    5 bytes    magic
iv         16 bytes
ciphertext  N bytes
tag        32 bytes    HMAC-SHA256
```

## Files

```
aeshmac/           package containing the crypto logic
  main.py          CLI entry point parsing -e, -d, -g
  generate_key.py  creates the 32 byte shared secret
  encrypt.py       AES-256-CBC, then appends the HMAC tag
  decrypt.py       verify pass, then decrypt pass
  crypto_common.py format constants, path helpers, HKDF key derivation
setup.py           package definition with entry points
samples/           original files
encrypted/         .enc files, these are what you send
decrypted/         recovered files
keys/shared.key    the shared secret, mode 0600
```
