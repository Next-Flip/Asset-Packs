#!/usr/bin/env python3
import sys
import shutil
import pathlib
import tarfile
import functools

from ext import asset_packer
from ext import tarball
from ext import ziparch

RESOURCE_ENTRY_NAME_MAX_LENGTH = 100

here = pathlib.Path(__file__).parent
packs_root = here.parent


def _tar_filter(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
    if len(tarinfo.name) > RESOURCE_ENTRY_NAME_MAX_LENGTH:
        raise ValueError("Resource name too long")
    return tarball.tar_sanitizer_filter(tarinfo)


def repack(pack_set: pathlib.Path) -> None:
    source = pack_set / "source"
    packed = pack_set / ".packed"
    asset_packer.pack(source, packed, logger=functools.partial(print, flush=True))

    output = pack_set / "download"
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    pack_zip = output / (pack_set.name + ziparch.ZIP_ARCH_EXTENSION)
    pack_tar = output / (pack_set.name + tarball.TAR_GZIP_EXTENSION)

    ziparch.compress_tree_ziparch(str(packed), str(pack_zip))
    tarball.compress_tree_tarball(str(packed), str(pack_tar), filter=_tar_filter)

    shutil.rmtree(packed)


if __name__ == "__main__":
    args = sys.argv[1:]

    if args:
        pack_sets = args
    else:
        pack_sets = [
            pack_set.name
            for pack_set in packs_root.iterdir()
            if not pack_set.name.startswith(".")
        ]

    for pack_set in pack_sets:
        pack_set = packs_root / pack_set
        if not pack_set.is_dir():
            if args:
                print(f"\nPack '{pack_set.name}' does not exist!\n", flush=True)
            continue
        repack(pack_set)
