# gfStory-ru

Симулятор сюжетных сцен из игры Girls' Frontline (первая часть).  
Проект основан на [оригинальном репозитории gfStory](https://github.com/neon-nyan/gfStory), является [реворком репозитория gfStory_EN](https://github.com/gudzpoz/gfStory), адаптирован для работы с переведёнными на русский язык главами.

## Особенности

- Поддержка переведённых на русский язык сюжетных линий
- Автоматическая распаковка игровых ресурсов
- Три режима просмотра: редактор сценариев, симулятор и читалка
- Экспорт готовых сцен для просмотра в браузере
- Автопереход на следующий текст (в рамках текущего статуса перевода)

## Как собрать проект

### Системные зависимости

Для сборки потребуются:

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

<details>
<summary>Arch Linux</summary>

```bash
sudo pacman -S git python python-pdm ffmpeg pngquant imagemagick libb2 nodejs pnpm zip
```

Установка vgmstream:

Можно установить пакет vgmstream-git из AUR или использовать готовый бинарный файл:

```bash
mkdir -p ~/.local/bin && wget -qO- https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-linux-cli.tar.gz | tar zxf - -C ~/.local/bin
```
Не забудьте добавить ~/.local/bin в $PATH, если используете второй способ.
</details>

<details> 
<summary>Ubuntu / Debian</summary>

```bash
sudo apt install git python3 python3-venv ffmpeg pngquant imagemagick libb2-1 nodejs libfuse2 zip
```
Установка pdm:

```bash
wget -qO- https://pdm-project.org/install-pdm.py | python3 -
```
Установка pnpm:

```bash
wget -qO- https://get.pnpm.io/install.sh | sh -
```
Установка magick (для Ubuntu):

```bash
wget https://imagemagick.org/archive/binaries/magick -P ~/.local/bin
chmod +x ~/.local/bin/magick
```
Установка vgmstream:

```bash
wget -qO- https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-linux-cli.tar.gz | tar zxf - -C ~/.local/bin
```
Перезапустите терминал и убедитесь, что ~/.local/bin присутствует в $PATH.

</details>

<details> 
<summary>Fedora</summary>

```bash
sudo dnf install git python ffmpeg pngquant ImageMagick libb2 nodejs pnpm zip
```
Установка pdm:

```bash
wget -qO- https://pdm-project.org/install-pdm.py | python3 -
```
Установка vgmstream:

```bash
wget -qO- https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-linux-cli.tar.gz | tar zxf - -C ~/.local/bin
```
Перезапустите терминал и убедитесь, что ~/.local/bin присутствует в $PATH.

</details>

### Процесс сборки
Клонируйте репозиторий с подмодулями (включая подпроект с переводами):

```bash
git clone --recurse-submodules https://github.com/your-username/gfStory-ru.git
cd gfStory-ru
```
Запустите скрипт сборки:
```bash
./build.sh
```
> **Примечание**
> Если игра обновлялась с момента последней сборки, удалите директорию unpack/downloader/output, чтобы загрузить актуальные ресурсы клиента.

### Структура перевода
Переведённые главы находятся в подмодуле gf-data-rus/. При сборке они автоматически интегрируются с распакованными ресурсами игры.


### Состояние перевода
На данный момент переведены и интегрированы:

**Основные сюжетные линии:**
- `EP 0–11 (полностью)`

