#!/bin/bash -eux

ARCHIVE=${1:-sound-data.pkl}

./check_languages.py --noarmory --difficulty easy $ARCHIVE > output/easy_noarmory.txt
./check_languages.py --noarmory --difficulty legendary $ARCHIVE > output/legendary_noarmory.txt
./check_languages.py --difficulty easy $ARCHIVE > output/easy.txt
./check_languages.py --difficulty legendary $ARCHIVE > output/legendary.txt

function gen_with_excludes() {
    output=$1
    excludes="${@:2}"
    mkdir -p output/$output
    ./check_languages.py --noarmory --difficulty easy $ARCHIVE --exclude $excludes > output/$output/easy_noarmory.txt
    ./check_languages.py --noarmory --difficulty legendary $ARCHIVE --exclude $excludes > output/$output/legendary_noarmory.txt
    ./check_languages.py --difficulty easy $ARCHIVE --exclude $excludes > output/$output/easy.txt
    ./check_languages.py --difficulty legendary $ARCHIVE --exclude $excludes > output/$output/legendary.txt
}

gen_with_excludes cairo_hangar1_skip cairo_malta
gen_with_excludes cairo_hangar1and2_skip cairo_malta cairo_athens
gen_with_excludes cairo_h1skip_arby_glassclip cairo_malta arbiter_no_glassclip
gen_with_excludes arby_glassclip arbiter_no_glassclip
