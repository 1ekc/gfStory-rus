import argparse
import os
import pathlib
import logging

from gfunpack import audio, backgrounds, chapters, characters, mapper, prefabs, stories

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('gfunpack')

parser = argparse.ArgumentParser()
parser.add_argument('dir')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('--no-clean', action='store_true')
parser.add_argument('--gf-data-rus', help='Path to gf-data-rus repository')
args = parser.parse_args()

cpus = os.cpu_count() or 2

downloaded = args.dir
destination = pathlib.Path(args.output)

images = destination.joinpath('images')
bg = backgrounds.BackgroundCollection(downloaded, str(images), pngquant=True, concurrency=cpus)
bg.save()

sprite_indices = prefabs.Prefabs(downloaded)
chars = characters.CharacterCollection(downloaded, str(images), sprite_indices, pngquant=True, concurrency=cpus)
chars.extract()

character_mapper = mapper.Mapper(sprite_indices, chars)
character_mapper.write_indices()

bgm = audio.BGM(downloaded, str(destination.joinpath('audio')), concurrency=cpus, clean=not args.no_clean)
bgm.save()

print(f"GF Data RUS path: {args.gf_data_rus}")
print(f"Path exists: {os.path.exists(args.gf_data_rus)}")
print(f"Files in gf-data-rus: {os.listdir(args.gf_data_rus)}")
print(f"Files in gf-data-rus/asset/avgtxt: {os.listdir(os.path.join(args.gf_data_rus, 'asset', 'avgtxt'))}")

ss = stories.Stories(
    downloaded,
    str(destination.joinpath('stories')),
    gf_data_directory=args.gf_data_rus
)
ss.save()
cs = chapters.Chapters(ss)
cs.save()
