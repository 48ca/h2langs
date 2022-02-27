import re
import sys
import os
import contextlib
import pickle

from typing import List, Tuple, Optional

from .common import SoundFile, MissionLang, Mission, LANGUAGES
from .missions import MISSIONS

SOUND_NAME_REGEX = '^(l(?P<level>[^_]+)_(?P<index>[^_]+)_(?P<speaker>[^_]+)\\[(?P<variant>.*)\\])\\.wav$'
SOUND_NAME_PAT = re.compile(SOUND_NAME_REGEX)

PICKLE_FILENAME = 'sound-data-new.pkl'

def try_files(directory: str, dir_list: List[str]) -> Tuple[Optional[str], MissionLang]:
    extra_files = []

    final_lvl_lang = MissionLang()
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
        final_lvl_lang.add_file(parsed_file)

    return None, final_lvl_lang

def get_files_from_sound_dir(sound_dir: str) -> Tuple[Optional[str], MissionLang]:
    lvl_dialog_dir = os.path.join(sound_dir, 'dialog', 'levels')
    if not os.path.isdir(lvl_dialog_dir):
        return 'sound directory has incorrect structure: {}'.format(lvl_dialog_dir), None
    bsps = os.listdir(lvl_dialog_dir)
    if len(bsps) != 1:
        return 'found more than one bsp for mission: {}'.format(bsps), None
    bsp = bsps[0]
    real_dir = os.path.join(lvl_dialog_dir, bsp, 'mission')
    if not os.path.isdir(real_dir):
        return 'not a directory: {}'.format(real_dir), None

    return try_files(real_dir, os.listdir(real_dir))

def canonicalize_archive(lang_dir: str) -> Tuple[str, MissionLang]:
    files = os.listdir(lang_dir)
    if len(files) == 1 and files[0] == 'sound':
        sound_dir = os.path.join(lang_dir, 'sound')
        if os.path.isdir(sound_dir):
            return get_files_from_sound_dir(sound_dir)

    return try_files(lang_dir, files)

def get_missions_new(archive: str):
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

            err, mission_lang = try_files(level_dir, os.listdir(level_dir))
            if err:
                sys.stderr.write('Got error while reading archive: {}: {}\n'.format(level_dir, err))
                continue
            mission.add_language(lang, mission_lang)
            print('Loaded: {}/{}: {}'.format(mission_id.name, LANGUAGES[lang], mission_lang))

    if extra_files:
        sys.stderr.write('Found extra files: {}\n'.format(extra_files))
        return None

    with open(PICKLE_FILENAME, 'wb') as f:
        print('Dumped data to {}'.format(PICKLE_FILENAME))
        pickle.dump(missions, f)

    return missions
