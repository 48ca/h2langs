#!/bin/bash -eux

ARCHIVE=${1:-sound-data.pkl}

./check_languages.py --stderrtotals --noarmory --difficulty easy $ARCHIVE 2> output/easy_noarmory.txt > output/easy_noarmory_breakdown.txt
./check_languages.py --stderrtotals --noarmory --difficulty legendary $ARCHIVE 2> output/legendary_noarmory.txt > output/legendary_noarmory_breakdown.txt
./check_languages.py --stderrtotals --difficulty easy $ARCHIVE 2> output/easy.txt > output/easy_breakdown.txt
./check_languages.py --stderrtotals --difficulty legendary $ARCHIVE 2> output/legendary.txt > output/legendary_breakdown.txt

function gen_with_excludes() {
    output=$1
    excludes="${@:2}"
    mkdir -p output/$output
    ./check_languages.py --stderrtotals --noarmory --difficulty easy $ARCHIVE --exclude $excludes 2> output/$output/easy_noarmory.txt > output/$output/easy_noarmory_breakdown.txt
    ./check_languages.py --stderrtotals --noarmory --difficulty legendary $ARCHIVE --exclude $excludes 2> output/$output/legendary_noarmory.txt > output/$output/legendary_noarmory_breakdown.txt
    ./check_languages.py --stderrtotals --difficulty easy $ARCHIVE --exclude $excludes 2> output/$output/easy.txt > output/$output/easy_breakdown.txt
    ./check_languages.py --stderrtotals --difficulty legendary $ARCHIVE --exclude $excludes 2> output/$output/legendary.txt > output/$output/legendary_breakdown.txt
}

gen_with_excludes cairo_hangar1_skip cairo_malta
gen_with_excludes cairo_hangar1and2_skip cairo_malta cairo_athens
gen_with_excludes cairo_h1skip_arby_glassclip cairo_malta arbiter_no_glassclip
gen_with_excludes arby_glassclip arbiter_no_glassclip
