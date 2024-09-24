import re
import sys
import pathlib

# Pack IDs must be 3 or more lowercase letters, letters and dashes, no dashes at begin/end
PACK_ID_REGEX = re.compile(r"^[a-z0-9][a-z-0-9]+[a-z0-9]$")

here = pathlib.Path(__file__).parent
packs_root = here.parent

known_fonts = [
    "Primary",
    "Secondary",
    "Keyboard",
    "BigNumbers",
    "BatteryPercent",
]
# In firmware repo, cd into assets/icons and run in bash:
# for icon in */*.png */*/frame_rate; do echo "$icon"; done > icons.txt
# TODO: Automate and/or provide a list via API or firmware repo
known_icons = (here / "icons.txt").read_text().splitlines()


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
