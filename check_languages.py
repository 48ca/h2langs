#!/usr/bin/env python3

import os
import sys
import itertools

from typing import Tuple, List, Optional, Set, Dict

from h2lang.create_sound_data import get_missions
from h2lang.create_data_from_full_archive import get_missions_new
from h2lang.common import Mission, LANGUAGES
from config import SOUNDS_TO_CHECK, Special

def check_missions(missions: Dict[str, Mission]) -> List[bool]:
    return list(map(lambda l: l.check_matching(), missions.values()))

def find_durations(mission_name, indices, variants, mission) -> Optional[Dict[str, float]]:
    total_durations = {}
    for code, language in mission.languages.items():
        total_dur = 0.
        for idx_or_special in indices:
            is_special = isinstance(idx_or_special, Special)
            idx = idx_or_special.index if is_special else idx_or_special

            if idx not in language.files:
                print('Invalid config: could not find sound file:', idx)
                return None

            files = language.files[idx]
            if idx not in variants and len(files) > 1:
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

def print_durations(name, durations):
    print('==== {} ===='.format(name))
    sd = sorted(durations, key=durations.get)
    if not sd:
        raise RuntimeError('no sorted durations')

    best_lang = sd[0]
    fastest = durations[best_lang]
    for lang in sd:
        print('{:9s} => +{:10.6f} (total:{:10.6f})'.format(LANGUAGES[lang], durations[lang] - fastest, durations[lang]))

def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write('usage: {} <path-to-archive OR path-to-pickle> [--new]\n'.format(sys.argv[0]))
        return 1

    archive = sys.argv[1]

    if len(sys.argv) >= 3:
        use_new_format = sys.argv[2] == '--new'
    else:
        use_new_format = False

    if not os.path.exists(archive):
        sys.stderr.write('Path does not exist: {}\n'.format(arhive))
        return 1

    if use_new_format:
        missions = get_missions_new(archive)
    else:
        missions = get_missions(archive)

    if not missions:
        return 1

    # Make sure that there are no mismatched files.
    passed = check_missions(missions)
    if not all(passed):
        for i, l in enumerate(missions):
            if not passed[i]:
                sys.stderr.write('Missions mismatched: {}\n'.format(l))
        return 1

    for name, sound in SOUNDS_TO_CHECK.items():
        mission_id = sound['mission']
        indices = sound['indices']
        variants = sound.get('variants')
        if mission_id.key not in missions:
            sys.stderr.write('Bad config: {}, mission not found\n'.format(name))
            continue

        mission = missions[mission_id.key]
        if not variants:
            durations = find_durations(mission_id.key, indices, {}, mission)
            print_durations(name, durations)
        if variants:
            for instance in itertools.product(*variants.values()):
                variants_to_try = dict(zip(variants.keys(), instance))
                durations = find_durations(mission_id.key, indices, variants_to_try, mission)
                print_durations('{} [variant={}]'.format(name, variants_to_try), durations)

    return 0

if __name__ == "__main__":
    sys.exit(main())
