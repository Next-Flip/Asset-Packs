#!/usr/bin/env python3
import re
import sys
import json
import pathlib

from ext import tarball
from ext import ziparch

# Pack IDs must be 3 or more lowercase letters, letters and dashes, no dashes at begin/end
PACK_ID_REGEX = re.compile(r"^[a-z0-9][a-z-0-9]+[a-z0-9]$")

here = pathlib.Path(__file__).parent
packs_root = here.parent

# In firmware repo, cd into assets/icons and run in bash:
# for icon in */*.png */*/frame_rate; do echo "$icon"; done > icons.txt
# TODO: Automate and/or provide a list via API or firmware repo
known_icons = (here / "icons.txt").read_text().splitlines()


def check(pack_set: pathlib.Path) -> None:
    # Pack ID
    assert PACK_ID_REGEX.match(
        pack_set.name
    ), "Must be 3 or more lowercase letters, letters and dashes, no dashes at begin/end"

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

    # Icons
    unknown = []
    for icon in icons:
        if icon.name in ("frame_rate", "meta"):
            icon = icon.with_name("frame_rate")
            icon_name = icon.parts[-3:]
            icon_path = icon.parts[-5:]
        elif icon.suffix in (".png", ".bmx"):
            icon = icon.with_suffix(".png")
            icon_name = icon.parts[-2:]
            icon_path = icon.parts[-4:]
        else:
            continue
        if "/".join(icon_name) not in known_icons:
            unknown.append("/".join(icon_path))
    if unknown:
        print(f"\nPack '{pack_set.name}' has {len(unknown)} unknown icons:", flush=True)
        print("\n".join(unknown), flush=True)

    # Meta
    with (pack_set / "meta.json").open() as f_meta:
        meta = json.load(f_meta)
    properties = sorted(list(meta.keys()))
    expected = sorted(("name", "author", "source_url", "description"))
    assert properties == expected, f"Must have {expected} in meta.json"


if __name__ == "__main__":
    ret = 0

    for pack_set in packs_root.iterdir():
        if pack_set.name.startswith(".") or not pack_set.is_dir():
            continue

        try:
            check(pack_set)
        except Exception as exc:
            if not isinstance(exc, AssertionError):
                raise
            print(f"\nPack '{pack_set.name}' has wrong format:", flush=True)
            print(f"{exc}\n", flush=True)
            ret = 1

    if ret == 0:
        print("\nAll formats are correct!", flush=True)
    else:
        print("\nSome packs have wrong format!", flush=True)
    sys.exit(ret)
