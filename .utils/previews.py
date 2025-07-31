#!/usr/bin/env python3
import pathlib
import heatshrink2
from PIL import Image, ImageOps
from typing import List
import re
import argparse
import numpy as np

import common


def decompress_bitmap(bm_data: bytes) -> bytes:
    if len(bm_data) < 2:
        raise ValueError("Invalid bitmap data: too short")

    compression_flag, second_byte = bm_data[0], bm_data[1]

    if compression_flag == 0x00:
        return bm_data[1:]
    elif compression_flag == 0x01 and second_byte == 0x00:
        if len(bm_data) < 4:
            raise ValueError("Invalid compressed bitmap data")

        compressed_len = bm_data[2] | (bm_data[3] << 8)
        compressed_data = bm_data[4 : 4 + compressed_len]

        if len(compressed_data) != compressed_len:
            raise ValueError(
                f"Compressed data length mismatch: expected {compressed_len}, got {len(compressed_data)}"
            )

        try:
            decompressed = heatshrink2.decompress(
                compressed_data, window_sz2=8, lookahead_sz2=4
            )
            decompressed_bytes = bytes(decompressed)

            if len(decompressed_bytes) == 0:
                raise ValueError("Decompression returned empty data")

            non_zero_count = sum(1 for b in decompressed_bytes if b != 0)
            all_ff_count = sum(1 for b in decompressed_bytes if b == 0xFF)

            if non_zero_count == 0:
                raise ValueError(
                    f"Decompression returned {len(decompressed_bytes)} bytes of all zeros"
                )

            return decompressed_bytes
        except Exception as e:
            raise ValueError(f"Failed to decompress bitmap data: {e}")
    else:
        raise ValueError(
            f"Unknown compression format: 0x{compression_flag:02x}{second_byte:02x}"
        )


def xbm_to_image(xbm_data: bytes, width: int, height: int) -> Image.Image:
    bytes_per_row = (width + 7) // 8
    expected_bytes = bytes_per_row * height

    if len(xbm_data) < expected_bytes:
        raise ValueError(
            f"Insufficient XBM data: need {expected_bytes} bytes, got {len(xbm_data)}"
        )

    img, pixels = Image.new("1", (width, height)), []

    for y in range(height):
        for x in range(width):
            byte_index = y * bytes_per_row + (x // 8)
            bit_offset = x % 8

            if byte_index < len(xbm_data):
                bit = (xbm_data[byte_index] >> bit_offset) & 1
                pixels.append(bit)
            else:
                pixels.append(0)

    img.putdata(pixels)
    return img


def parse_meta_txt(meta_path: pathlib.Path) -> dict:
    meta = {}

    if not meta_path.exists():
        return meta

    content = meta_path.read_text().strip()

    for line in content.split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()

            if key in ["width", "height", "frame rate"]:
                try:
                    meta[key] = int(value)
                except ValueError:
                    meta[key] = value
            elif key == "frames order":
                meta[key] = [int(x) for x in value.split()]
            else:
                meta[key] = value

    return meta


def find_anims_folders(pack_path: pathlib.Path) -> List[pathlib.Path]:
    anims_dirs, anim_folders = list(pack_path.rglob("Anims")), []

    for anims_dir in anims_dirs:
        for subdir in anims_dir.iterdir():
            if subdir.is_dir():
                meta_file = subdir / "meta.txt"

                if meta_file.exists() and (
                    list(subdir.glob("frame_*.bm")) or list(subdir.glob("frame_*.png"))
                ):
                    anim_folders.append(subdir)

    return anim_folders


def create_gif_from_frames(
    anim_folder: pathlib.Path, output_path: pathlib.Path
) -> bool:
    try:
        meta_file = anim_folder / "meta.txt"
        meta = parse_meta_txt(meta_file)

        if not meta:
            print(f"Warning: Could not parse meta.txt in {anim_folder}")
            return False

        width = meta.get("width", 128)
        height = meta.get("height", 64)
        frame_rate = meta.get("frame rate", 6)
        frames_order = meta.get("frames order", [])

        if not frames_order:
            print(f"Warning: No frame order found in {anim_folder}")
            return False

        frames = []

        if list(anim_folder.glob("frame_*.png")):
            for frame_idx in frames_order:
                png_file = anim_folder / f"frame_{frame_idx}.png"

                if not png_file.exists():
                    print(f"Warning: Missing PNG frame file {png_file}")
                    continue

                try:
                    img = Image.open(png_file)
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.LANCZOS)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    frames.append(img)

                except Exception as e:
                    print(f"Error processing PNG frame {png_file}: {e}")
                    continue

        elif list(anim_folder.glob("frame_*.bm")):
            for frame_idx in frames_order:
                bm_file = anim_folder / f"frame_{frame_idx}.bm"

                if not bm_file.exists():
                    print(f"Warning: Missing BM frame file {bm_file}")
                    continue

                try:
                    bm_data = bm_file.read_bytes()
                    xbm_data = decompress_bitmap(bm_data)
                    expected_bytes = ((width + 7) // 8) * height
                    img = xbm_to_image(xbm_data, width, height)
                    rgb_img = img.convert("RGB")
                    rgb_img_inverted = ImageOps.invert(rgb_img)
                    rgb_img = rgb_img_inverted
                    frames.append(rgb_img)

                except Exception as e:
                    print(f"Error processing BM frame {bm_file}: {e}")
                    continue
        else:
            print(f"Warning: No frame files found in {anim_folder}")
            return False

        if not frames:
            print(f"Warning: No valid frames found in {anim_folder}")
            return False

        duration_ms = int(1000 / frame_rate) if frame_rate > 0 else 167
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_frames = []
        background_color = (254, 138, 43)  # #fe8a2b
        output_width, output_height = 512, 256

        for frame in frames:
            frame_array = np.array(frame)
            alpha = np.where(
                (frame_array[:, :, 0] > 240)
                & (frame_array[:, :, 1] > 240)
                & (frame_array[:, :, 2] > 240),
                0,
                255,
            )

            frame_rgba_array = np.dstack([frame_array, alpha])
            frame_rgba = Image.fromarray(frame_rgba_array.astype(np.uint8), "RGBA")

            scaled_frame = frame_rgba.resize(
                (output_width, output_height), Image.NEAREST
            )
            bg_frame = Image.new("RGB", (output_width, output_height), background_color)
            bg_frame.paste(scaled_frame, (0, 0), scaled_frame)
            final_frames.append(bg_frame)

        final_frames[0].save(
            output_path,
            save_all=True,
            append_images=final_frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

        print(f"Created GIF: {output_path} ({len(frames)} frames, {frame_rate} FPS)")
        return True

    except Exception as e:
        print(f"Error creating GIF from {anim_folder}: {e}")
        return False


def process_pack(pack_path: pathlib.Path) -> None:
    anim_folders = find_anims_folders(pack_path)

    if not anim_folders:
        print(f"  No animation folders found in {pack_path.name}")
        return

    preview_dir = pack_path / "preview"
    preview_dir.mkdir(exist_ok=True)

    existing_gifs = list(preview_dir.glob("*.gif"))
    for gif_file in existing_gifs:
        gif_file.unlink()
        print(f"  Deleted existing GIF: {gif_file.name}")

    success_count = 0
    for index, anim_folder in enumerate(anim_folders, 1):
        output_file = preview_dir / f"{index}.gif"

        if create_gif_from_frames(anim_folder, output_file):
            success_count += 1

    print(f"  Created {success_count}/{len(anim_folders)} GIF previews")

    if success_count > 0:
        image_files = []
        for ext in ("*.png", "*.jpg"):
            image_files.extend(preview_dir.glob(ext))

        image_files = [f for f in image_files if not f.name.startswith(".")]

        if image_files:
            image_files.sort(key=lambda x: x.name.lower())

            next_number = success_count + 1
            for image_file in image_files:
                new_name = f"{next_number}{image_file.suffix}"
                new_path = preview_dir / new_name

                if image_file.name != new_name:
                    image_file.rename(new_path)
                    print(f"  Renamed {image_file.name} -> {new_name}")

                next_number += 1


def main():
    parser = argparse.ArgumentParser(
        description="Generate GIF previews from bitmap/PNG animation frames"
    )
    parser.add_argument("pack_name", help="Name of the asset pack to process")
    args = parser.parse_args()

    pack_path = common.packs_root / args.pack_name

    if not pack_path.exists():
        print(f"Error: Pack '{args.pack_name}' not found")
        return

    if not pack_path.is_dir():
        print(f"Error: '{args.pack_name}' is not a directory")
        return

    print(f"Processing pack: {args.pack_name}")
    process_pack(pack_path)


if __name__ == "__main__":
    main()
