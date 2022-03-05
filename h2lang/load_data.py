import re
import sys
import os
import contextlib
import pickle

from typing import List, Tuple, Optional

from .common import SoundFile, MissionLang, Mission, LANGUAGES
from .missions import MISSIONS

SOUND_NAME_REGEX = '^([lcx](?P<level>[^_]+)_(?P<index>[^_]+)_(?P<speaker>[^_]+)\\[(?P<variant>.*)\\])\\.wav$'
SOUND_NAME_PAT = re.compile(SOUND_NAME_REGEX)

PICKLE_FILENAME = 'sound-data.pkl'

def try_files(directory: str) -> Tuple[Optional[str], MissionLang]:
    extra_files = []

    final_lvl_lang = MissionLang()
    dir_list = os.listdir(directory)
    for sound in dir_list:
        res = SOUND_NAME_PAT.match(sound)
        if not res:
            extra_files.append(sound)
            continue
        full_path = os.path.join(directory, sound)
        if not os.path.isfile(full_path):
            return 'found sound file that is not a file: {}'.format(full_path), None

        gd = res.groupdict()
        if any(map(lambda k: k not in gd, ['level', 'index', 'speaker'])):
            return 'improper filename: {} (parsed: {})'.format(sound, gd), None

        parsed_file = SoundFile(full_path, gd)
        # For the dump that I am using, the output sample rate is 44100 when it should be
        # between 44786 and 44787 (manually checked this), which means all the durations
        # are slightly longer than they should be.
        # The discrepancy in the sample rate is likely a bug in the extractor.
        parsed_file.apply_correction(44100/44786)
        final_lvl_lang.add_file(parsed_file)

    return None, final_lvl_lang

def get_missions(archive: str):
    extra_files = []

    if archive == PICKLE_FILENAME:
        # Attempt to load the data from the pickle data.
        with open(PICKLE_FILENAME, 'rb') as f:
            return pickle.load(f)

    if not os.path.isdir(archive):
        sys.stderr.write('Not a directory: {}\n'.format(archive))
        return None

    lst = os.listdir(archive)

    missions = {}
    for mission_id in MISSIONS.values():
        missions[mission_id.key] = Mission(mission_id)

    for lang in lst:
        if lang not in LANGUAGES:
            extra_files.append(lang)
            continue
        lang_dir = os.path.join(archive, lang, 'sound', 'dialog', 'levels')
        if not os.path.isdir(lang_dir):
            sys.stderr.write('Not a directory: {}\n'.format(lang_dir))
            continue

        all_levels = os.listdir(lang_dir)
        for mission_id in MISSIONS.values():
            mission = missions[mission_id.key]
            level = mission_id.level
            level_dir = os.path.join(lang_dir, level, 'mission')
            if not os.path.isdir(level_dir):
                sys.stderr.write('Not a directory: {}\n'.format(level_dir))
                continue

            err, mission_lang = try_files(level_dir)
            if err:
                sys.stderr.write('Got error while reading archive: {}: {}\n'.format(level_dir, err))
                continue
            mission.add_language(lang, mission_lang)
            print('Loaded: {}/{}: {}'.format(mission_id.name, LANGUAGES[lang], mission_lang))

    if extra_files:
        sys.stderr.write('Found extra files: {}\n'.format(extra_files))

    with open(PICKLE_FILENAME, 'wb') as f:
        print('Dumped data to {}'.format(PICKLE_FILENAME))
        pickle.dump(missions, f)

    return missions
