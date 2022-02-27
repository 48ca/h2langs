from h2lang.missions import *

class Special:
    def __init__(self, index, func):
        self._func = func
        self.index = index

    def calculate(self, duration):
        return self._func(duration)

SOUNDS_TO_CHECK = {
        'gm_end': {
            'mission': GRAVEMIND,
            'indices': {
                2590, # This isn't good ... In Amber Clad's wreckage.
                2600, # Let's get the index ... really ugly.
            }
        },
        'armory_training_look': {
            'mission': ARMORY,
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
            'mission': ARMORY,
            'indices': {
                790, # Stand by. I'm going to offline the inhibitors.
                800, # Move aroudn a little, get a feel for it.
                810, # When you're ready ... by the zapper.
            }
        },
        'armory_training_shield': {
            'mission': ARMORY,
            'indices': {
                3150, # Pay attention ... over this once.
                3140, # This station will ... shields.
                950, # As you can see ... faster.
                960, # If your shields ... fully-charged.
                970, # That, or he can hide behind me.
                1000, # You done with ... training wheels.
                1010, # His armor's working fine. [Potential chili-hole skip.]
                980, # You're free to go ... take things slow.
            },
            'variants': {
                1010: { # Chili-hole skip.
                    'l01_1010a_gun', # [skip]
                    'l01_1010b_gun' # [no skip]
                }
            }
        },
        'armory_training_done': {
            'mission': ARMORY,
            'indices': {
                # Don't worry, I'll hold his hand.
                Special(1040, lambda dur: max(0, dur - 1)),

                3360, # So Johnson, ... in one piece?
                990, # Sorry, Guns. It's classified. 
            }
        },
        'armory_training_tram': {
            'mission': ARMORY,
            'indices': {
                # Earth. Haven't seen it in years.
                Special(10, lambda dur: max(0, dur - 1))
            }
        },
        'armory_full': {
            'mission': ARMORY,
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
                1010, # His armor's working fine. [Potential chili-hole skip.]
                980, # You're free to go ... take things slow.

                # Don't worry, I'll hold his hand.
                Special(1040, lambda dur: max(0, dur - 1)),

                3360, # So Johnson, ... in one piece?
                990, # Sorry, Guns. It's classified. 
                # Earth. Haven't seen it in years.
                Special(10, lambda dur: max(0, dur - 1))
            },
            'variants': {
                1010: { # Chili-hole skip.
                    'l01_1010a_gun', # [skip]
                    'l01_1010b_gun' # [no skip]
                }
            }
        }
}
