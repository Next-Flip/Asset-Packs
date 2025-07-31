# Asset-Packs

A bundle of [asset packs](https://github.com/Next-Flip/Momentum-Firmware/blob/dev/documentation/file_formats/AssetPacks.md) for [Momentum Firmware](https://github.com/Next-Flip/Momentum-Firmware).

> [!IMPORTANT]
> These asset packs are all available on the [Momentum Firmware website](https://momentum-fw.dev/asset-packs).
> This repository serves only as a way to keep them updated and maintained more easily.

### How?

The [flipper-update-indexer](https://github.com/Next-Flip/flipper-update-indexer) includes this repository as a submodule. It will parse the asset packs contents and serve the appropriate files on the API ([`https://up.momentum-fw.dev/asset-packs`](https://up.momentum-fw.dev/asset-packs)). Then the [Momentum-Website](https://github.com/Next-Flip/Momentum-Website) will query the API and allow users to download and install the asset packs.

The scope of this repo is keeping the asset packs themselves updated and recompile as needed.

You can do this by:

```gitignore
make repack [pack-name]
# OR
python3 .utils/repack.py [pack-name]
```

## Generating Previews

For **Icons**: use [qFlipper](https://flipperzero.one/update), click 'Save Screenshot'

For **Animations**: we have a script that generates GIF previews directly from the bitmap/PNG animation frames for maximum quality:

1. Run the [previews](.utils/previews.py) script.

```gitignore
make previews [pack-name]
# OR
python3 .utils/previews.py [pack-name]
```

2. (_if necessary_) Your previews folder may have too many files or the order is incorrect (if you want a different frame to be first). Delete extra previews and rename evrything in the 1, 2, 3... order. You should have at least one GIF, and however many PNGs for Icons/Passports. **This 1.gif, 2.gif, etc. order maintains consistency and easier sorting.**

3. When ready, your pack should look like this:

```zig
baba-is-you/
├── download
│   ├── baba-is-you.tar.gz
│   └── baba-is-you.zip
├── meta.json
├── preview
│   ├── 1.gif
│   ├── 2.png
│   ├── 3.png
│   └── 4.png
└── source
    └── BABA IS YOU
        ├── Anims
        │   ├── BABA_IS_YOU
        │   │   ├── frame_0.bm
        │   │   ├── frame_1.bm
        │   │   ├── frame_2.bm
        │   │   └── meta.txt
        │   └── manifest.txt
        ├── Fonts
        │   ...
        └── Icons
            ...
```

## Support

If you enjoy the firmware please \***\*spread the word!\*\*** And if you really love it, maybe consider donating to the team? :D

-   **[Ko-fi](https://ko-fi.com/willyjl)**: One-off or Recurring, No signup required
-   **[PayPal](https://paypal.me/willyjl1)**: One-off, Signup required
-   **BTC**: `1EnCi1HF8Jw6m2dWSUwHLbCRbVBCQSyDKm`

**Thank you <3**
