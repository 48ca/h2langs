#!/usr/bin/env python3

import os
import sys
import itertools
import copy
import argparse

from typing import Tuple, List, Optional, Set, Dict

from h2lang.create_sound_data import get_missions
from h2lang.create_data_from_full_archive import get_missions_new
from h2lang.common import Mission, LANGUAGES
from h2lang.missions import ARMORY
from config import SOUNDS_TO_CHECK, Special, Difficulty

def check_missions(missions: Dict[str, Mission]) -> List[bool]:
    return list(map(lambda l: l.check_matching(), missions.values()))

def find_durations(mission_name, indices, variants, mission, difficulty) -> Optional[Dict[str, float]]:
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
                total_dur += idx_or_special.calculate(snd_file.duration, difficulty)
        total_durations[code] = total_dur
    return total_durations

def print_name(name, totals):
    print('==== {} ===={}'.format(name, ' (no totals)' if not totals else ''))

def print_durations(name, durations, totals):
    print_name(name, totals)
    sd = sorted(durations, key=durations.get)
    if not sd:
        raise RuntimeError('no sorted durations')

    best_lang = sd[0]
    fastest = durations[best_lang]
    for lang in sd:
        print('{:9s} => +{:10.6f} (total:{:11.6f})'.format(LANGUAGES[lang], durations[lang] - fastest, durations[lang]))

def main() -> int:
    parser = argparse.ArgumentParser(description='Process halo timing differences.')
    parser.add_argument('archive', type=str, help='Path to the archive (or pickle)')
    parser.add_argument('--noarmory', help='Don\'t include armory in full-game duration summation.', action='store_true')
    parser.add_argument('--new', default=False, help='Use new archive format (experimental).', action='store_true')
    parser.add_argument('--nototaling', default=False, help='Don\'t total anything.', action='store_true')
    parser.add_argument('--difficulty', type=str, default='easy', help='Specify the difficulty.')
    args = parser.parse_args()

    if args.difficulty == 'easy':
        difficulty = Difficulty.EASY
    elif args.difficulty == 'normal':
        difficulty = Difficulty.NORMAL
    elif args.difficulty == 'heroic':
        difficulty = Difficulty.HEROIC
    elif args.difficulty == 'legendary':
        difficulty = Difficulty.LEGENDARY
    else:
        sys.stderr.write('Bad difficulty: {}\n'.format(args.difficulty))
        return 1

    noarmory = args.noarmory
    global_no_totaling = args.nototaling
    use_new_format = args.new

    archive = args.archive

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

    language_totals = {'': {}}
    for name, sound in SOUNDS_TO_CHECK.items():
        if name.startswith('SKIP'):
            continue
        mission_id = sound['mission']
        indices = sound['indices']
        variants = sound.get('variants')
        nototal = sound.get('nototal')
        if mission_id.key not in missions:
            print_name(name, not nototal)
            print('ERROR: Bad config: {}, mission not found'.format(name))
            continue

        do_totaling = not (global_no_totaling or nototal or (noarmory and mission_id.key == ARMORY.key))
        def add_to_totals(mkey, variant, lang, dur):
            if 'full_game' not in language_totals[variant]:
                language_totals[variant]['full_game'] = {}
            if lang not in language_totals[variant]['full_game']:
                language_totals[variant]['full_game'][lang] = 0.
            language_totals[variant]['full_game'][lang] += dur

            if mkey not in language_totals[variant]:
                language_totals[variant][mkey] = {}
            if lang not in language_totals[variant][mkey]:
                language_totals[variant][mkey][lang] = 0.
            language_totals[variant][mkey][lang] += dur

        mission = missions[mission_id.key]
        if not variants:
            durations = find_durations(mission_id.key, indices, {}, mission, difficulty)
            print_durations(name, durations, do_totaling)
            if do_totaling:
                for variant in language_totals:
                    for lang, dur in durations.items():
                        add_to_totals(mission_id.key, variant, lang, dur)
        if variants:
            if do_totaling:
                new_totals = {}
                for existing_variant in language_totals:
                    for new_variants in variants.values():
                        for new_variant in new_variants:
                            new_totals["{}|{}".format(existing_variant, new_variant)] = copy.deepcopy(language_totals[existing_variant])
                language_totals = new_totals

            for instance in itertools.product(*variants.values()):
                variants_to_try = dict(zip(variants.keys(), instance))
                durations = find_durations(mission_id.key, indices, variants_to_try, mission, difficulty)
                print_durations('{} [variant={}]'.format(name, variants_to_try), durations, do_totaling)
                if do_totaling:
                    for lang, dur in durations.items():
                        for var_val in variants_to_try.values():
                            num_added = 0
                            num_missed = 0
                            for e_var in language_totals:
                                if var_val in e_var:
                                    add_to_totals(mission_id.key, e_var, lang, dur)
                                    num_added += 1
                                else:
                                    num_missed += 1
                            if num_added != num_missed or (num_added + num_missed < len(language_totals)):
                                raise RuntimeError('Bad total counting')

    if do_totaling:
        print('========== TOTALS ==========')
        for variant, cats in language_totals.items():
            for cat, tot in cats.items():
                print_durations('{} [variants={}]'.format(cat, variant), tot, True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
