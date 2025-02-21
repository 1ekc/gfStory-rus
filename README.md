# gfStory-en

A Girls's Frontline cutscene simulator.

## How to build

Build dependencies:

- python
- ffmpeg
- zip
- pngquant
- imagemagick
- pdm
- nodejs
- pnpm
- libb2
- vgmstream

### Install dependencies

<details>
<summary>Arch Linux</summary>

```bash
sudo pacman -S git python python-pdm ffmpeg pngquant imagemagick libb2 nodejs pnpm zip
```

Install vgmstream:

Either install the `vgmstream-git` package from AUR or use the following command to install a precompiled binary in `~/.local/bin`.

```bash
mkdir -p ~/.local/bin && wget -qO- https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-linux-cli.tar.gz | tar zxf - -C ~/.local/bin
```

Don't forget to add `~/.local/bin` to your `$PATH` if you use this method.
</details>

<details>
<summary>Ubuntu</summary>

```bash
sudo apt install git python3 python3-venv ffmpeg pngquant imagemagick libb2-1 nodejs libfuse2 zip
```

Install pdm:

```bash
wget -qO- https://pdm-project.org/install-pdm.py | python3 -
```

Install pnpm:

```bash
wget -qO- https://get.pnpm.io/install.sh | sh -
```

Install magick:

Ubuntu based distros ship an ancient version of imagemagick that does not include `magick`, a "new" command line utility required by the image unpacker script. Fortunately, there's a standalone appimage of magick that we can use.

```bash
wget https://imagemagick.org/archive/binaries/magick -P ~/.local/bin
chmod +x ~/.local/bin/magick
```

Install vgmstream:

```bash
wget -qO- https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-linux-cli.tar.gz | tar zxf - -C ~/.local/bin
```

Restart your terminal and make sure that `~/.local/bin` is in your `$PATH`.
</details>

<details>
<summary>Fedora</summary>

```bash
sudo dnf install git python ffmpeg pngquant ImageMagick libb2 nodejs pnpm zip
```

Install pdm:

```bash
wget -qO- https://pdm-project.org/install-pdm.py | python3 -
```

Install vgmstream:

```bash
wget -qO- https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-linux-cli.tar.gz | tar zxf - -C ~/.local/bin
```

Restart your terminal and make sure that `~/.local/bin` is in your `$PATH`.
</details>

### Build

To build the site, run `build.sh` in the root of the repository.
> **Note**  
> If the game has been updated since the last time you ran the script, delete the `output` directory in `unpack/downloader/` to download the new client assets.

```bash
./build.sh
```

## How to run gfStory-en locally

Run the following command in the root of the repository to test your newly built site.

```bash
pnpm dev
```

Alternatively, you can use Python's built-in web server.

```bash
python -m http.server -d dist
```
