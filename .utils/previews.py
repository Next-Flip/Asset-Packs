#!/usr/bin/env python3
import ffmpeg
import pathlib

import common


def convert_mp4_previews(pack_set: pathlib.Path) -> None:
    previews = pack_set / "preview"

    for preview in previews.glob("*.mp4"):
        probe = ffmpeg.probe(preview)

        for stream in probe["streams"]:
            if stream["codec_type"] == "video":
                break
        else:  # Did not break, so no video stream
            print(f"Preview has no video: {preview.relative_to(common.packs_root)}")
            continue

        convert = ffmpeg.input(str(preview))

        # Personal ease of use: when captured from qFlipper with BlueRecorder,
        # this crops to fit the preview window perfectly
        if stream["width"] == 862 and stream["height"] == 532:
            convert = convert.crop(width=512, height=256, x=66, y=82)

        convert = convert.output(str(preview.with_suffix(".gif")))
        convert.run()


if __name__ == "__main__":
    for pack_set in common.cli_pack_sets():
        convert_mp4_previews(pack_set)
