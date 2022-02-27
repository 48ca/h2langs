#!/bin/bash -eux

ARCHIVE=$1

./check_languages.py --noarmory --difficulty easy $1 > easy_noarmory.txt
./check_languages.py --noarmory --difficulty legendary $1 > legendary_noarmory.txt
./check_languages.py --difficulty easy $1 > easy.txt
./check_languages.py --difficulty legendary $1 > legendary.txt
