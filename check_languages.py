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
from h2lang.missions import ARMORY, MISSIONS
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

def print_name(name, totals, stream=sys.stdout):
    stream.write(' ====== {} ======{}\n'.format(name, ' (no totals)' if not totals else ''))

def print_durations(name, durations, totals, stream=sys.stdout):
    print_name(name, totals, stream)
    sd = sorted(durations, key=durations.get)
    if not sd:
        raise RuntimeError('no sorted durations')

    best_lang = sd[0]
    fastest = durations[best_lang]
    for lang in sd:
        stream.write('{:9s} => +{:10.6f} (total:{:11.6f})\n'.format(LANGUAGES[lang], durations[lang] - fastest, durations[lang]))

class VariantSet():
    def __init__(self):
        # Use a list because it guarantees order, but really
        # we should use an ordered set.
        self._variants = []

    def add_variant(self, variant):
        self._variants.append(variant)

    def has_variant(self, variant):
        return variant in self._variants

    def __str__(self):
        return str(self._variants)

DEFAULT_VARIANT = VariantSet()

class LanguageTotalTracker():
    def __init__(self):
        self._categories = {'Full Game': {DEFAULT_VARIANT: {}}}

    def _add_to_totals(self, lang_times, lang, dur):
        if lang not in lang_times:
            lang_times[lang] = 0.
        lang_times[lang] += dur

    def add_time(self, mission, durations):
        if mission not in self._categories:
            self._categories[mission] = {DEFAULT_VARIANT: {}}
        # Add the time to all categories.
        for cat in [mission, 'Full Game']:
            variants = self._categories[cat]
            for variant in variants:
                for lang, dur in durations.items():
                    self._add_to_totals(variants[variant], lang, dur)

    def add_new_variant(self, mission, variants):
        # Duplicate all existing variants, and then add each of the new variants.
        for cat in [mission, 'Full Game']:
            new_totals = {}
            old_totals = self._categories[cat]
            for existing_variant in old_totals:
                for new_variants in variants.values():
                    for new_variant in new_variants:
                        old_stuff = copy.deepcopy(old_totals[existing_variant])
                        new_vk = copy.deepcopy(existing_variant)
                        new_vk.add_variant(new_variant)
                        new_totals[new_vk] = old_stuff
            self._categories[cat] = new_totals

    def add_variant_time(self, mission, variants_to_try, durations):
        if mission not in self._categories:
            self._categories[mission] = {DEFAULT_VARIANT: {}}
        # Add the time to a specific variant.
        for cat in [mission, 'Full Game']:
            variants = self._categories[cat]
            num_added = 0
            num_missed = 0
            for variant in variants:
                for lang, dur in durations.items():
                    for var_val in variants_to_try.values():
                        if variant.has_variant(var_val):
                            self._add_to_totals(variants[variant], lang, dur)
                            num_added += 1
                        else:
                            num_missed += 1
            if num_added != num_missed:
                raise RuntimeError('Bad total counting: {} {}'.format(num_added, num_missed))
    def print_out(self, stderr=False):
        if not stderr:
            sys.stdout.write(' ========== TOTALS ========== \n')
        stream = sys.stderr if stderr else sys.stdout
        for cat in self._categories:
            real_name = MISSIONS[cat].name if cat in MISSIONS else cat
            for variant, durations in self._categories[cat].items():
                if variant != DEFAULT_VARIANT:
                    print_durations('{} [variant={}]'.format(real_name, variant), durations, True, stream)
                else:
                    print_durations(real_name, durations, True, stream)

def main() -> int:
    parser = argparse.ArgumentParser(description='Process halo timing differences.')
    parser.add_argument('archive', type=str, help='Path to the archive (or pickle)')
    parser.add_argument('--noarmory', help='Don\'t include armory.', action='store_true')
    parser.add_argument('--new', default=False, help='Use new archive format (experimental).', action='store_true')
    parser.add_argument('--nototaling', default=False, help='Don\'t total anything.', action='store_true')
    parser.add_argument('--difficulty', type=str, default='easy', help='Specify the difficulty.')
    parser.add_argument('--exclude', nargs='+',
            help='Exclude a particular section from analysis (e.g., if doing Arbiter Glass Clip, it shouldn\'t be included.')
    parser.add_argument('--stderrtotals', default=False, action='store_true',
            help='Write totals to stderr.')
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

    language_totals = LanguageTotalTracker()
    for name, sound in SOUNDS_TO_CHECK.items():
        if args.exclude and name in args.exclude:
            continue
        if name.startswith('SKIP'):
            continue
        mission_id = sound['mission']
        if mission_id.key == ARMORY.key and noarmory:
            continue
        indices = sound['indices']
        variants = sound.get('variants')
        nototal = sound.get('nototal')
        if mission_id.key not in missions:
            print_name(name, not nototal)
            print('ERROR: Bad config: {}, mission not found'.format(name))
            continue

        do_totaling = not (global_no_totaling or nototal)

        mission = missions[mission_id.key]
        if not variants:
            durations = find_durations(mission_id.key, indices, {}, mission, difficulty)
            print_durations(name, durations, do_totaling)
            if do_totaling:
                language_totals.add_time(mission_id.key, durations)
        if variants:
            if do_totaling:
                language_totals.add_new_variant(mission_id.key, variants)

            for instance in itertools.product(*variants.values()):
                variants_to_try = dict(zip(variants.keys(), instance))
                durations = find_durations(mission_id.key, indices, variants_to_try, mission, difficulty)
                print_durations('{} [variant={}]'.format(name, variants_to_try), durations, do_totaling)
                if do_totaling:
                    language_totals.add_variant_time(mission_id.key, variants_to_try, durations)

    if do_totaling:
        language_totals.print_out(args.stderrtotals)

    return 0

if __name__ == "__main__":
    sys.exit(main())
