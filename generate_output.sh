#!/bin/bash -eux

ARCHIVE=${1:-sound-data.pkl}
BREAKDOWNS=BREAKDOWNS
mkdir -p output/$BREAKDOWNS

./check_languages.py --stderrtotals --noarmory --difficulty easy $ARCHIVE 2> output/easy_noarmory.txt > output/$BREAKDOWNS/easy_noarmory.txt
./check_languages.py --stderrtotals --noarmory --difficulty legendary $ARCHIVE 2> output/legendary_noarmory.txt > output/$BREAKDOWNS/legendary_noarmory.txt
./check_languages.py --stderrtotals --difficulty easy $ARCHIVE 2> output/easy.txt > output/$BREAKDOWNS/easy.txt
./check_languages.py --stderrtotals --difficulty legendary $ARCHIVE 2> output/legendary.txt > output/$BREAKDOWNS/legendary.txt

function gen_with_excludes() {
    output=$1
    excludes="${@:2}"
    mkdir -p output/$output
    mkdir -p output/$BREAKDOWNS/$output
    ./check_languages.py --stderrtotals --noarmory --difficulty easy $ARCHIVE --exclude $excludes 2> output/$output/easy_noarmory.txt > output/$BREAKDOWNS/$output/easy_noarmory.txt
    ./check_languages.py --stderrtotals --noarmory --difficulty legendary $ARCHIVE --exclude $excludes 2> output/$output/legendary_noarmory.txt > output/$BREAKDOWNS/$output/legendary_noarmory.txt
    ./check_languages.py --stderrtotals --difficulty easy $ARCHIVE --exclude $excludes 2> output/$output/easy.txt > output/$BREAKDOWNS/$output/easy.txt
    ./check_languages.py --stderrtotals --difficulty legendary $ARCHIVE --exclude $excludes 2> output/$output/legendary.txt > output/$BREAKDOWNS/$output/legendary.txt
}

gen_with_excludes cairo_hangar1_skip cairo_malta
gen_with_excludes cairo_hangar1and2_skip cairo_malta cairo_athens
gen_with_excludes cairo_h1skip_arby_glassclip cairo_malta arbiter_no_glassclip
gen_with_excludes arby_glassclip arbiter_no_glassclip
