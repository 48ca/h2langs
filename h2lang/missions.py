from collections import namedtuple

MissionIdentifier = namedtuple('MissionIdentifier', 'name level key')

MISSIONS = {
        'heretic':   MissionIdentifier('The Heretic',       '01_spacestation', 'heretic'),
        'armory':    MissionIdentifier('Armory',            '01_spacestation', 'armory'),
        'cairo':     MissionIdentifier('Cairo Station',     '01_spacestation', 'cairo'),
        'outskirts': MissionIdentifier('Outskirts',         '03_earthcity',    'outskirts'),
        'metro':     MissionIdentifier('Metropolis',        '03_earthcity',    'metro'),
        'arbiter':   MissionIdentifier('The Arbiter',       '04_gasgiant',     'arbiter'),
        'oracle':    MissionIdentifier('Oracle',            '04_gasgiant',     'oracle'),
        'dh':        MissionIdentifier('Delta Halo',        '05_deltatemple',  'dh'),
        'regret':    MissionIdentifier('Regret',            '05_deltatemple',  'regret'),
        'si':        MissionIdentifier('Sacred Icon',       '06_sentinelwall', 'si'),
        'qz':        MissionIdentifier('Quarantine Zone',   '06_sentinelwall', 'qz'),
        'gm':        MissionIdentifier('Gravemind',         '07_highcharity',  'gm'),
        'uprising':  MissionIdentifier('Uprising',          '08_controlroom',  'uprising'),
        'hc':        MissionIdentifier('High Charity',      '07_highcharity',  'hc'),
        'tgj':       MissionIdentifier('The Great Journey', '08_controlroom',  'tgj'),
}

THE_HERETIC =       MISSIONS['heretic']
ARMORY =            MISSIONS['armory']
CAIRO_STATION =     MISSIONS['cairo']
OUTSKIRTS =         MISSIONS['outskirts']
METROPOLIS =        MISSIONS['metro']
THE_ARBITER =       MISSIONS['arbiter']
ORACLE =            MISSIONS['oracle']
DELTA_HALO =        MISSIONS['dh']
REGRET =            MISSIONS['regret']
SACRED_IRON =       MISSIONS['si']
QUARANTINE_ZONE =   MISSIONS['qz']
GRAVEMIND =         MISSIONS['gm']
UPRISING =          MISSIONS['uprising']
HIGH_CHARITY =      MISSIONS['hc']
THE_GREAT_JOURNEY = MISSIONS['tgj']
