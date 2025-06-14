from gfunpack import chapters, characters, mapper, prefabs, stories


def test_stories():
    ss = stories.Stories(
        'downloader/output',
        'stories',
        gf_data_directory='path/to/gf-data-rus'
    )
    ss.save()
    chapters.Chapters(ss).save()
    print(ss.content_tags)
    print(ss.effect_tags)


if __name__ == '__main__':
    test_stories()
