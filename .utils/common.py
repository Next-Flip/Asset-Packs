import sys
import pathlib

here = pathlib.Path(__file__).parent
packs_root = here.parent


def cli_pack_sets() -> list[pathlib.Path]:
    args = sys.argv[1:]

    if args:
        pack_sets = [packs_root / arg for arg in args]
    else:
        pack_sets = [pack_set for pack_set in packs_root.iterdir()]

    ret = []
    for pack_set in pack_sets:
        if pack_set.name.startswith("."):
            if args:
                print(f"\nPack '{pack_set.name}' can't start with . !\n", flush=True)
            continue
        if not pack_set.is_dir():
            if args:
                print(f"\nPack '{pack_set.name}' is not a directory!\n", flush=True)
            continue
        ret.append(pack_set)
    return ret
