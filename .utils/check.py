#!/usr/bin/env python3
import sys
import json
import pathlib

from ext import tarball
from ext import ziparch


def check(pack_set: pathlib.Path) -> None:
    # Downloads
    assert (
        pack_set / f"download/{pack_set.name}{ziparch.ZIP_ARCH_EXTENSION}"
    ).is_file(), f"Must have packed {ziparch.ZIP_ARCH_EXTENSION} download"
    assert (
        pack_set / f"download/{pack_set.name}{tarball.TAR_GZIP_EXTENSION}"
    ).is_file(), f"Must have packed {tarball.TAR_GZIP_EXTENSION} download"

    # Previews
    previews = 0
    for ext in (".png", ".jpg", ".gif"):
        previews += sum(1 for _ in pack_set.glob(f"preview/*{ext}"))
    assert previews in range(1, 8), "Must have between 1 and 7 previews"

    # Source
    anims = list(pack_set.glob("source/*/Anims/manifest.txt"))
    fonts = list(pack_set.glob("source/*/Fonts/*.c"))
    fonts += list(pack_set.glob("source/*/Fonts/*.u8f"))
    icons = list(pack_set.glob("source/*/Icons/*/*.png"))
    icons += list(pack_set.glob("source/*/Icons/*/*.bmx"))
    icons += list(pack_set.glob("source/*/Icons/*/*/frame_rate"))
    icons += list(pack_set.glob("source/*/Icons/*/*/meta"))
    assert anims or fonts or icons, "Must have some content (Anims or Fonts or Icons)"

    # Meta
    with (pack_set / "meta.json").open() as f_meta:
        meta = json.load(f_meta)
    properties = sorted(list(meta.keys()))
    expected = sorted(("name", "author", "source_url", "description"))
    assert properties == expected, f"Must have {expected} in meta.json"


if __name__ == "__main__":
    pack_sets = pathlib.Path(__file__).parent.parent
    for pack_set in pack_sets.iterdir():
        if pack_set.name.startswith(".") or not pack_set.is_dir():
            continue
        try:
            check(pack_set)
        except Exception as exc:
            if not isinstance(exc, AssertionError):
                raise
            print(f"\nPack {pack_set.name} has wrong format:", flush=True)
            print(f"{exc}\n", flush=True)
            sys.exit(1)
    print("\nNo problems detected!", flush=True)
