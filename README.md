# Halo 2 Language Difference Analyzer

To check which language is fastest.

With current strategies, for full-game, German is the fastest!
Check the `output` directory.

The pickle dump that is included has the data for all levels (including the ones that don't matter) for all 8 languages.

You can run it with:
```
./check_languages.py
```

## How do you know which lines matter?

A two-step process: play the game and find where we *could* be waiting for dialogue, and then read through the scripts to see (1) if we are really waiting on something, (2) which lines we are waiting on, and (3) how we are waiting for those lines.

This information has been distilled into `config.py`.
