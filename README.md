# Asset-Packs
Bundle of [asset packs](https://github.com/Next-Flip/Momentum-Firmware/blob/dev/documentation/file_formats/AssetPacks.md) for [Momentum Firmware](https://github.com/Next-Flip/Momentum-Firmware).

> [!IMPORTANT]
> These asset packs are all available on the [Momentum Firmware website](https://momentum-fw.dev/asset-packs).
> This repository serves only as a way to keep them updated and maintained easier.

### How?
The [flipper-update-indexer](https://github.com/Next-Flip/flipper-update-indexer) includes this repository as a submodule. It will parse the asset packs contents and serve the appropriate files on the API ([`https://up.momentum-fw.dev/asset-packs`](https://up.momentum-fw.dev/asset-packs)). Then the [Momentum-Website](https://github.com/Next-Flip/Momentum-Website) will query the API and allow users to download and install the asset packs.

The scope of this repo is keeping the asset packs themselves updated and recompile them as needed.

You can do this by:
```bash
    make repack
```