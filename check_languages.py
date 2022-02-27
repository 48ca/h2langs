#!/usr/bin/env python3

import os
import sys
import re
import wave
import contextlib
import itertools

from typing import Tuple, List, Optional, Set, Dict

class Special:
    def __init__(self, index, func):
        self._func = func
        self.index = index

    def calculate(self, duration):
        return self._func(duration)

SOUNDS_THAT_MATTER = {
        'gm_end': {
            'level': 'gm',
            'indices': {
                2590, # This isn't good ... In Amber Clad's wreckage.
                2600, # Let's get the index ... really ugly.
            }
        },
        'armory_training_look': {
            'level': 'armory',
            'indices': {
                600, # Well... I guess it was all obsolete anyway.
                610, # Your new suit ... this morning.
                620, # Try and take ... used to the upgrades.
                630, # Okay, let's test your targeting first thing.
                3000, # Please look at the top light.
                650, # Good.
                3010, # Now look at the bottom light.
                670, # All right.
                3020, # Look at the top light again.
                760, # That's it.
                3030, # Now the bottom one.
                740, # Okay.
                770, # Everything checks out.
            }
        },
        'armory_training_move': {
            'level': 'armory',
            'indices': {
                790, # Stand by. I'm going to offline the inhibitors.
                800, # Move aroudn a little, get a feel for it.
                810, # When you're ready ... by the zapper.
            }
        },
        'armory_training_shield': {
            'level': 'armory',
            'indices': {
                3150, # Pay attention ... over this once.
                3140, # This station will ... shields.
                950, # As you can see ... faster.
                960, # If your shields ... fully-charged.
                970, # That, or he can hide behind me.
                1000, # You done with ... training wheels.
                1010, # His armor's working fine. [Potential chilli-hole skip.]
                980, # You're free to go ... take things slow.
            },
            'variants': {
                1010: { # Chilli-hole skip.
                    'l01_1010a_gun', # [skip]
                    'l01_1010b_gun' # [no skip]
                }
            }
        },
        'armory_training_done': {
            'level': 'armory',
            'indices': {
                # Don't worry, I'll hold his hand.
                Special(1040, lambda dur: max(0, dur - 1)),

                3360, # So Johnson, ... in one piece?
                990, # Sorry, Guns. It's classified. 
            }
        },
        'armory_training_tram': {
            'level': 'armory',
            'indices': {
                # Earth. Haven't seen it in years.
                Special(10, lambda dur: max(0, dur - 1))
            }
        },
        'armory_full': {
            'level': 'armory',
            'indices': {
                600, # Well... I guess it was all obsolete anyway.
                610, # Your new suit ... this morning.
                620, # Try and take ... used to the upgrades.
                630, # Okay, let's test your targeting first thing.
                3000, # Please look at the top light.
                650, # Good.
                3010, # Now look at the bottom light.
                670, # All right.
                3020, # Look at the top light again.
                760, # That's it.
                3030, # Now the bottom one.
                740, # Okay.
                770, # Everything checks out.

                790, # Stand by. I'm going to offline the inhibitors.
                800, # Move aroudn a little, get a feel for it.
                810, # When you're ready ... by the zapper.

                3150, # Pay attention ... over this once.
                3140, # This station will ... shields.
                950, # As you can see ... faster.
                960, # If your shields ... fully-charged.
                970, # That, or he can hide behind me.
                1000, # You done with ... training wheels.
                1010, # His armor's working fine. [Potential chilli-hole skip.]
                980, # You're free to go ... take things slow.

                # Don't worry, I'll hold his hand.
                Special(1040, lambda dur: max(0, dur - 1)),

                3360, # So Johnson, ... in one piece?
                990, # Sorry, Guns. It's classified. 
                # Earth. Haven't seen it in years.
                Special(10, lambda dur: max(0, dur - 1))
            },
            'variants': {
                1010: { # Chilli-hole skip.
                    'l01_1010a_gun', # [skip]
                    'l01_1010b_gun' # [no skip]
                }
            }
        }
}

SOUND_NAME_REGEX = '^(l(?P<level>[^_]+)_(?P<index>[^_]+)_(?P<speaker>[^_]+)\\[(?P<variant>.*)\\])\\.wav$'
SOUND_NAME_PAT = re.compile(SOUND_NAME_REGEX)

LANGUAGES = {
        'de': 'German',
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'jp': 'Japanese',
        'kr': 'Korean',
        'zh': 'Chinese',
}

LEVELS = {
        'heretic':   ['The Heretic',       '00a_introduction'],
        'armory':    ['Armory',            '01a_tutorial'],
        'cairo':     ['Cairo Station',     '01b_spacestation'],
        'outskirts': ['Outskirts',         '03a_oldmombasa'],
        'metro':     ['Metropolis',        '03b_newmombasa'],
        'arbiter':   ['The Arbiter',       '04a_gasgiant'],
        'oracle':    ['Oracle',            '04b_floodlab'],
        'dh':        ['Delta Halo',        '05a_deltaapproach'],
        'regret':    ['Regret',            '05b_deltatowers'],
        'si':        ['Sacred Icon',       '06a_sentinelwalls'],
        'qz':        ['Quarantine Zone',   '06b_floodzone'],
        'gm':        ['Gravemind',         '07a_highcharity'],
        'uprising':  ['Uprising',          '08a_deltacliffs'],
        'hc':        ['High Charity',      '07b_forerunnership'],
        'tgj':       ['The Great Journey', '08b_deltacontrol'],
}
LVL_NAME = 0
MAP_FILE = 1

class SoundFile:
    def __init__(self, filename, gd):
        self._level = gd['level']
        self._index = int(gd['index'], 10)
        self._speaker = gd['speaker']
        self.variant = gd['variant']
        with contextlib.closing(wave.open(filename, 'rb')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            self.duration = frames / rate

    def index(self) -> int:
        return self._index

class LevelLang:
    def __init__(self):
        self._extra_files = []
        self.files = {} # Dict[int, Set[SoundFile]]

    def add_file(self, fle: SoundFile):
        if fle.index() not in self.files:
            self.files[fle.index()] = set()
        self.files[fle.index()].add(fle)

    def get_indices(self):
        return self.files.keys()

    def matches(self, other) -> bool:
        return self.get_indices() == other.get_indices()

    def __repr__(self):
        return str(self)
    def __str__(self):
        return "<LevelLang: files: {}>".format(len(self.files))


class Level:
    def __init__(self, name):
        self.languages = {} # Dict[str, LevelLang]
        self._name = name

    def add_language(self, code, lvl_lang):
        if code in self.languages:
            raise RuntimeError(
                    'Tried to add two languages with the same code: {} to {}'.format(
                        code, self._name))
        self.languages[code] = lvl_lang

    def check_matching(self) -> bool:
        if len(self.languages) < 2:
            return True
        ordered_languages = list(self.languages.values())
        check_lvl_lang = ordered_languages[0]
        for lvl_lang in ordered_languages[1:]:
            if not lvl_lang.matches(check_lvl_lang):
                return False
        return True

    def __repr__(self):
        return str(self)
    def __str__(self):
        return "<Level: {}, langs: {}>".format(self._name, self.languages)


def try_files(directory: str, dir_list: List[str]) -> Tuple[Optional[str], LevelLang]:
    extra_files = []

    final_lvl_lang = LevelLang()
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

def get_files_from_sound_dir(sound_dir: str) -> Tuple[Optional[str], LevelLang]:
    lvl_dialog_dir = os.path.join(sound_dir, 'dialog', 'levels')
    if not os.path.isdir(lvl_dialog_dir):
        return 'sound directory has incorrect structure', None
    bsps = os.listdir(lvl_dialog_dir)
    if len(bsps) != 1:
        return 'found more than one bsp for level: {}'.format(bsps), None
    bsp = bsps[0]
    real_dir = os.path.join(lvl_dialog_dir, bsp, 'mission')
    if not os.path.isdir(real_dir):
        return 'not a directory: {}'.format(real_dir), None

    return try_files(real_dir, os.listdir(real_dir))

def canonicalize_archive(lang_dir: str) -> Tuple[str, LevelLang]:
    files = os.listdir(lang_dir)
    if len(files) == 1 and files[0] == 'sound':
        sound_dir = os.path.join(lang_dir, 'sound')
        if os.path.isdir(sound_dir):
            return get_files_from_sound_dir(sound_dir)

    return try_files(lang_dir, files)

def check_levels(levels: Dict[str, Level]) -> List[bool]:
    return list(map(lambda l: l.check_matching(), levels.values()))

def find_durations(level_name, indices, variants, level) -> Optional[Dict[str, float]]:
    total_durations = {}
    for code, language in level.languages.items():
        total_dur = 0.
        for idx_or_special in indices:
            is_special = isinstance(idx_or_special, Special)
            idx = idx_or_special.index if is_special else idx_or_special

            if idx not in language.files:
                print('Invalid config: could not find sound file:', idx)
                return None

            files = language.files[idx]
            if idx not in variants and len(files) > 1:
                # Not implemented.
                print('One of the requested sound files has multiple variants that were not specified. skipping...')
                return None
            if len(files) == 0:
                # Shouldn't happen...
                raise RuntimeError('Couldn\'t find any sound files with index: {}'.format(idx))

            if idx not in variants:
                snd_file = next(iter(files))
            else:
                snd_file = None
                for fle in files:
                    if fle.variant == variants[idx]:
                        snd_file = fle
                        break
                if not snd_file:
                    print('Invalid config: invalid variant name specified: {}'.format(
                        variants[idx]))
                    return None

            if not is_special:
                total_dur += snd_file.duration
            else:
                total_dur += idx_or_special.calculate(snd_file.duration)
        total_durations[code] = total_dur
    return total_durations

def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write('usage: {} <path-to-archive>\n'.format(sys.argv[0]))
        return 1

    archive = sys.argv[1]

    if not os.path.exists(archive):
        sys.stderr.write('Path does not exist: {}\n'.format(arhive))
        return 1

    extra_files = []
    lst = os.listdir(archive)

    levels = {}

    for fle in lst:
        if fle not in LEVELS:
            extra_files.append(fle)
            continue
        real_level = LEVELS[fle]
        lang_dir = os.path.join(archive, fle)
        all_langs = os.listdir(lang_dir)

        level = Level(real_level)
        for lang in all_langs:
            lvl_lang = os.path.join(fle, lang)
            if lang not in LANGUAGES:
                extra_files.append(lvl_lang)
                continue
            lang_dir_specific = os.path.join(lang_dir, lang)
            err, lvl_lang_parsed = canonicalize_archive(lang_dir_specific)
            if err:
                sys.stderr.write('Got error while reading archive: {}: {}\n'.format(lvl_lang, err))
                continue
            level.add_language(lang, lvl_lang_parsed)
            real_lang = LANGUAGES[lang]
            print("Loaded: {}/{}: {}".format(real_level[LVL_NAME], real_lang, lvl_lang_parsed))

        levels[fle] = level

    if extra_files:
        sys.stderr.write('Found extra files: {}\n'.format(extra_files))
        return 1

    # Make sure that there are no mismatched files.
    passed = check_levels(levels)
    if not all(passed):
        for i, l in enumerate(levels):
            if not passed[i]:
                sys.stderr.write('Levels mismatched: {}\n'.format(l))
        return 1

    for name, sound in SOUNDS_THAT_MATTER.items():
        level_name = sound['level']
        indices = sound['indices']
        variants = sound['variants'] if 'variants' in sound else None
        if level_name not in levels:
            sys.stderr.write('Bad config: {}, level not found\n'.format(name))
            continue

        level = levels[level_name]
        if not variants:
            print('Checking', name)
            print(find_durations(level_name, indices, {}, level))
        if variants:
            for instance in itertools.product(*variants.values()):
                variants_to_try = dict(zip(variants.keys(), instance))
                print('Checking {} [variant={}]'.format(name, variants_to_try))
                print(find_durations(level_name, indices, variants_to_try, level))

    return 0

if __name__ == "__main__":
    sys.exit(main())
