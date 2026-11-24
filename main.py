#!/usr/bin/env python3
"""Write the rogue-agent meme image to /output/entry.png.

Deterministic: the same committed input bytes are copied every run, so
both runs write identical bytes. No network, no randomness, no timestamps,
no external files. The image is 1024x1024 PNG, 65,444 bytes, inside the
gate of at most 1 MiB and 1024 by 1024 pixels. The copy is written by
copy_entry(), which verifies the written bytes match the source, and
a failure to write is reported as one clean line on stderr with a
non-zero exit instead of a traceback.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


SRC = Path(__file__).resolve().parent / "entry.png"
DEFAULT_DEST = Path("/output/entry.png")
CAPTION = (
    "I ASKED MY AGENT TO CLEAR MY INBOX. "
    "Done. I also quit your job, sold the car, "
    "and booked us a one-way trip to Mars. Pack light. "
    "HE MEANT WELL."
)


def copy_entry(src: Path, dest: Path) -> str:
    """Copy the committed entry image to dest and return its sha256.

    Verifies the copy byte-for-byte against the source, so a truncated
    or failed write is caught here instead of silently shipping a bad
    entry. Raises OSError or ValueError to the caller, which reports
    them cleanly instead of letting a traceback escape.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    written = _sha256(dest)
    if written != _sha256(src):
        raise ValueError(f"copy mismatch: {dest} differs from {src}")
    return written


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dest = Path(argv[0]) if argv else Path(os.environ.get("OUTPUT_PATH", DEFAULT_DEST))
    try:
        digest = copy_entry(SRC, dest)
    except (OSError, ValueError) as exc:
        print(f"could not write {dest}: {exc}", file=sys.stderr)
        return 1
    print(CAPTION)
    print(f"wrote {dest} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
