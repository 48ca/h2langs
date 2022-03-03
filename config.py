from enum import Enum
from h2lang.missions import *

class Difficulty(Enum):
    EASY = 0
    NORMAL = 1
    HEROIC = 2
    LEGENDARY = 3

EASY = Difficulty.EASY
NORMAL = Difficulty.NORMAL
HEROIC = Difficulty.HEROIC
LEGENDARY = Difficulty.LEGENDARY

ALL_DIFFICULTIES = {EASY, NORMAL, HEROIC, LEGENDARY}

class Special:
    def __init__(self, index, func=None, difficulties=ALL_DIFFICULTIES):
        self._func = func
        self.index = index
        self._difficulties = difficulties

    def calculate(self, duration, difficulty):
        if difficulty not in self._difficulties:
            return 0
        if self._func:
            return self._func(duration)
        return duration

SOUNDS_TO_CHECK = {
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
        },
    },
    'armory_training_move': {
        'mission': ARMORY,
        'indices': {
            790, # Stand by. I'm going to offline the inhibitors.
            800, # Move aroudn a little, get a feel for it.
            810, # When you're ready ... by the zapper.
        },
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
            1010: [ # Chili-hole skip.
                'l01_1010a_gun', # [skip]
                'l01_1010b_gun' # [no skip]
            ]
        },
    },
    'armory_training_done': {
        'mission': ARMORY,
        'indices': {
            # Don't worry, I'll hold his hand.
            Special(1040, lambda dur: max(0, dur - 1)),

            3360, # So Johnson, ... in one piece?
            990, # Sorry, Guns. It's classified. 
        },
    },
    'armory_training_tram': {
        'mission': ARMORY,
        'indices': {
            # Earth. Haven't seen it in years.
            Special(10, lambda dur: max(0, dur - 1))
        },
    },
    'cairo_malta': {
        'mission': CAIRO_STATION,
        'indices': {
            200, # Hey, check it out. ... boarders.
            210, # Malta, what's your status, over?
            220, # I don't believe it. ... We won!
        }
    },
    'cairo_athens': {
        'mission': CAIRO_STATION,
        'indices': {
            230, # Uh-oh. They're leaving the Athens.
            260, # Cortana, assessment.
            270, # The explosion ... a bomb.
            280, # Then they ... find it.
        }
    },
    'arbiter_start': {
        'mission': THE_ARBITER,
        'indices': {
            210, # We are the arm ... the blade.
            220, # Be silent ... without incident.
        }
    },
    'arbiter_no_glassclip': {
        'mission': THE_ARBITER,
        'indices': {
            470, # Deal with him, my brothers.
            480, # I will defend the Oracle.
        }
    },
    'SKIP_oracle_start_standard': {
        'mission': ORACLE,
        'indices': {
            40, # I wondered ... I'm flattered.
            50, # He's using a holo-drone. He must be close!
            60, # Come out so we may kill you.
            70, # Hahaha, get in line.
        },
        'nototal': True,
    },
    # It's a little bit unclear to me how dialog skip works, but I think
    # the effect is that we don't wait for the 'flattered' line.
    'oracle_start_dialog_skip': {
        'mission': ORACLE,
        'indices': {
            50, # He's using a holo-drone. He must be close!
            60, # Come out so we may kill you.
            70, # Hahaha, get in line.
        }
    },
    'oracle_cables': {
        'mission': ORACLE,
        'indices': {
            1380, # That's one ... at the station list.
            1400, # One final cable, Arbiter.
        }
    },
    'oracle_heretic_leader': {
        'mission': ORACLE,
        'indices': {
            # How did the prophets buy your loyalty, Arbiter?
            Special(800, difficulties={HEROIC, LEGENDARY}),
            # With a new command? A new fleet?
            Special(810, difficulties={HEROIC, LEGENDARY}),
            # Or was it the promise? Their Great Journey!
            Special(820, difficulties={HEROIC, LEGENDARY}),
            # Look around you, Arbiter.
            Special(830, difficulties={LEGENDARY}),
            # This facility ... study of the parasite.
            Special(840, difficulties={LEGENDARY}),
            # But where are ... was the result?
            Special(850, difficulties={LEGENDARY}),
            # All that time ... foul creatures on ice.
            Special(860, difficulties={LEGENDARY}),
            # And now ... have us worship?
            Special(870, difficulties={LEGENDARY}),
            # Trascended? Hardly.
            Special(880, difficulties={LEGENDARY}),
            # Come ... where they went.
            Special(890, difficulties={LEGENDARY}),
        }
    },
    'regret_first_elevator': {
        'mission': REGRET,
        'indices': {
            1000, # Ah now I see. ... to the outlying structures.
            1010, # Looks like we're going down.
            1020, # Unless you'd prefer to swim.
        }
    },
    'regret_end': {
        'mission': REGRET,
        'indices': {
            220, # Bad news. ... We need to get out of here!
        }
    },
    'si_end_fight': {
        'mission': SACRED_ICON,
        'indices': {
            170, # Arbiter! What are you doing here?
        }
    },
    'gm_begin': {
        'mission': GRAVEMIND,
        'indices': {
            1000, # The demon ... chamber?
            1010, # Protect the hierarchs! Seal the exits!
            2190, # Oh, I don't think so.
            2110, # Put me down on one of the pedestals near the door.
            2150, # That prophet ... take it from him.
            2140, # Let me get these doors...
        },
    },
    'gm_all_doors': {
        'mission': GRAVEMIND,
        'indices': {
            2060, # Right this way!
            # 2300, # Here, Chief! Jump in! [Only bottle-necked if prison skip is faster.]
        },
    },
    'gm_end': {
        'mission': GRAVEMIND,
        'indices': {
            2640, # Hang on... I'm picking up two more transponders.
            2650, # It's the commander and Johnson.
            2660, # They're closing on Truth's position, Chief.
            2670, # They'll need your help.
            2590, # This isn't good ... In Amber Clad's wreckage.
            2600, # Let's get the index ... really ugly.
        },
    },
    'tgj_scarab_door': {
        'mission': THE_GREAT_JOURNEY,
        'indices': {
            840, # Stay clear of the door.
            850, # Hey bastards, knock knock.
        }
    },
}
