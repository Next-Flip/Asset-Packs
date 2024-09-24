#!/usr/bin/env python3
import sys
import json
import pathlib

import common

from ext import tarball
from ext import ziparch


def check(pack_set: pathlib.Path) -> None:
    # Pack ID
    assert common.PACK_ID_REGEX.match(
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
    packs = []
    total_fonts = []
    total_icons = []
    for pack in (pack_set / "source").iterdir():
        path = "/".join(pack.parts[-3:])
        assert (
            not pack.name.startswith(".") and pack.is_dir()
        ), f"Source path '{path}' is invalid"
        has_anims = (pack / "Anims/manifest.txt").is_file()
        has_fonts = list(pack.glob("Fonts/*.c"))
        has_fonts += list(pack.glob("Fonts/*.u8f"))
        total_fonts += has_fonts
        has_icons = list(pack.glob("Icons/*/*.png"))
        has_icons += list(pack.glob("Icons/*/*.bmx"))
        has_icons += list(pack.glob("Icons/*/*/frame_rate"))
        has_icons += list(pack.glob("Icons/*/*/meta"))
        total_icons += has_icons
        assert (
            has_anims or has_fonts or has_icons
        ), f"Source '{path}' has no content (Anims or Fonts or Icons)"
        packs.append(pack)
    assert packs, "Must have some asset pack source content"

    # Meta
    with (pack_set / "meta.json").open() as f_meta:
        meta = json.load(f_meta)
    properties = sorted(list(meta.keys()))
    expected = sorted(("name", "author", "source_url", "description"))
    assert properties == expected, f"Must have {expected} in meta.json"

    # Fonts and Icons validity
    unknown = []
    for font in total_fonts:
        if font.suffix in (".c", ".u8f"):
            font_name = font.stem
            font_path = font.parts[-3:]
        else:
            continue
        if font_name not in common.known_fonts:
            unknown.append("/".join(font_path))
    for icon in total_icons:
        if icon.name in ("frame_rate", "meta"):
            icon_name = icon.with_name("frame_rate").parts[-3:]
            icon_path = icon.parts[-5:]
        elif icon.suffix in (".png", ".bmx"):
            icon_name = icon.with_suffix(".png").parts[-2:]
            icon_path = icon.parts[-4:]
        else:
            continue
        if "/".join(icon_name) not in common.known_icons:
            unknown.append("/".join(icon_path))
    if unknown:
        # Don't assert, maybe pack author includes extra options to switch between
        print(f"\nPack '{pack_set.name}' has unknown content:", flush=True)
        print("\n".join(unknown), flush=True)


if __name__ == "__main__":
    ret = 0

    for pack_set in common.cli_pack_sets():
        try:
            check(pack_set)
        except Exception as exc:
            if not isinstance(exc, AssertionError):
                raise
            print(f"\nPack '{pack_set.name}' has wrong format:", flush=True)
            print(f"{exc}\n", flush=True)
            ret = 1

    if ret == 0:
        print(
            f"\nAll {'requested ' if sys.argv[1:] else ''}packs formats are correct!",
            flush=True,
        )
    else:
        print("\nSome packs have wrong format!", flush=True)
    sys.exit(ret)
